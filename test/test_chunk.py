import pytest
import pandas as pd
from pathlib import Path
from storage.input.create_input import create_input
from config.model.input_config import InputConfig, InputType
from graph.chunk.chunker import Chunker
from config.enums import ChunkStrategyType
def test_chunker_with_story():
    """测试孔乙己文本的分块效果"""
    # 使用storage接口读取文本
    input_text = create_input(InputConfig(type=InputType.file, base_dir="test"), root_dir="test")
    print(input_text)
    # 创建分块器实例
    chunker = Chunker(
        group_by_columns=["text"],
        size=200,  # 每块约200字
        overlap=50,      # 重叠50字
        encoding_model="text-embedding-3-small",
        strategy=ChunkStrategyType.sentence
    )
    
    # 执行分块
    chunks_df = chunker.chunk(input_text)
    
    # 基本断言
    assert isinstance(chunks_df, pd.DataFrame)
    assert not chunks_df.empty
    assert "text" in chunks_df.columns
    assert "index" in chunks_df.columns
    
    # 检查分块结果
    chunks = chunks_df["text"].tolist()
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) >= chunker.min_chunk_size for chunk in chunks)
    
    # 检查重叠
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        # 检查相邻块是否有重叠
        overlap_found = False
        for j in range(min(len(current_chunk), chunker.overlap * 2)):
            if next_chunk.startswith(current_chunk[-j:]):
                overlap_found = True
                assert j >= chunker.overlap // 2, f"重叠太小: {j} 字符"
                break
        assert overlap_found, f"块 {i} 和 {i+1} 之间没有找到重叠"
    
    # 保存结果到文件
    output_dir = Path("test/output")
    output_dir.mkdir(exist_ok=True)
    
    # 保存原始DataFrame
    chunks_df.to_csv(output_dir / "chunks.csv", index=False)
    
    # 保存可读性更好的文本格式
    with open(output_dir / "chunks_readable.txt", "w", encoding="utf-8") as f:
        f.write(f"总块数: {len(chunks)}\n")
        f.write(f"配置: 块大小={chunker.chunk_size}, 重叠={chunker.overlap}, 最小块大小={chunker.min_chunk_size}\n\n")
        
        for i, chunk in enumerate(chunks, 1):
            f.write(f"=== 块 {i} ===\n")
            f.write(f"长度: {len(chunk)} 字符\n")
            f.write(chunk)
            f.write("\n\n")
            
            if i < len(chunks):
                # 显示与下一块的重叠
                next_chunk = chunks[i]
                overlap_text = ""
                for j in range(min(len(chunk), chunker.overlap * 2)):
                    if next_chunk.startswith(chunk[-j:]):
                        overlap_text = chunk[-j:]
                        break
                if overlap_text:
                    f.write(f"与下一块重叠 ({len(overlap_text)} 字符):\n{overlap_text}\n")
            f.write("\n" + "=" * 50 + "\n\n")
    
    # 保存统计信息
    stats = pd.DataFrame({
        "块长度": [len(chunk) for chunk in chunks],
        "开始文本": [chunk[:20] + "..." for chunk in chunks],
        "结束文本": ["..." + chunk[-20:] for chunk in chunks]
    })
    stats.to_csv(output_dir / "chunk_stats.csv", index=True)
    
    # 返回测试结果供查看
    return {
        "chunks_df": chunks_df,
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(len(chunk) for chunk in chunks) / len(chunks),
        "min_chunk_size": min(len(chunk) for chunk in chunks),
        "max_chunk_size": max(len(chunk) for chunk in chunks)
    }

if __name__ == "__main__":
    # 运行测试并打印结果
    result = test_chunker_with_story()
    print("\n测试结果统计:")
    print(f"总块数: {result['total_chunks']}")
    print(f"平均块大小: {result['avg_chunk_size']:.1f} 字符")
    print(f"最小块: {result['min_chunk_size']} 字符")
    print(f"最大块: {result['max_chunk_size']} 字符")
    print(f"\n结果已保存到: test/output/")