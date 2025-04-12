import time
import os
import pickle
import concurrent.futures
from typing import List, Optional
import pandas as pd
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from tenacity import retry

from utils.hashing import gen_sha512_hash

class EntityRelationExtractor:
    """
    实体关系提取器，负责从文本中提取实体和关系。
    使用LLM分析文本块，生成结构化的实体和关系数据。
    """
    
    def __init__(self, llm, system_template, human_template, 
                 entity_types: List[str], relationship_types: List[str],
                 cache_dir="./cache/graph", max_workers=4, batch_size=5):
        """
        初始化实体关系提取器
        
        Args:
            llm: 语言模型
            system_template: 系统提示模板
            human_template: 用户提示模板
            entity_types: 实体类型列表
            relationship_types: 关系类型列表
            cache_dir: 缓存目录
            max_workers: 并行工作线程数
            batch_size: 批处理大小
        """
        self.llm = llm
        self.entity_types = entity_types
        self.relationship_types = relationship_types
        self.chat_history = []
        
        # 设置分隔符
        self.tuple_delimiter = " : "
        self.record_delimiter = "\n"
        self.completion_delimiter = "\n\n"
        
        # 创建提示模板
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        self.chat_prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            MessagesPlaceholder("chat_history"),
            human_message_prompt
        ])
        
        # 创建处理链
        self.chain = self.chat_prompt | self.llm
        
        # 缓存设置
        self.cache_dir = cache_dir
        self.enable_cache = True
        
        # 确保缓存目录存在
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # 并行处理配置
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # 缓存统计
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _generate_cache_key(self, text: str) -> str:
        """生成文本的缓存键"""
        return gen_sha512_hash(text)
    
    def _cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _save_to_cache(self, cache_key: str, result: str) -> None:
        """保存结果到缓存"""
        if not self.enable_cache:
            return
            
        cache_path = self._cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            print(f"缓存保存错误: {e}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """从缓存加载结果"""
        if not self.enable_cache:
            return None
            
        cache_path = self._cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    result = pickle.load(f)
                    self.cache_hits += 1
                    return result
            except Exception as e:
                print(f"缓存加载错误: {e}")
        
        self.cache_misses += 1
        return None
    
    def process_chunks(self, chunks_df: pd.DataFrame) -> pd.DataFrame:
        """
        处理文本块DataFrame
        
        Args:
            chunks_df: 包含文本块的DataFrame，格式为Chunker的输出
            
        Returns:
            pd.DataFrame: 处理结果
        """
        t0 = time.time()
        total_chunks = len(chunks_df)
        
        # 预检查缓存命中率
        cache_keys = chunks_df["text"].apply(self._generate_cache_key)
        cached_results = {key: self._load_from_cache(key) for key in cache_keys}
        non_cached_indices = [idx for idx, key in enumerate(cache_keys) if cached_results[key] is None]
        
        if len(non_cached_indices) > 0:
            # 只为未缓存的chunks创建任务
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 创建任务字典
                future_to_chunk = {
                    executor.submit(self._process_single_chunk, chunks_df.iloc[idx]["text"]): idx 
                    for idx in non_cached_indices
                }
                
                # 处理完成的任务
                for future in concurrent.futures.as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        result = future.result()
                        cached_results[cache_keys[chunk_idx]] = result
                        
                            
                    except Exception as exc:
                        print(f'Chunk {chunk_idx} 处理异常: {exc}')
                        # 重试逻辑
                        retry_count = 0
                        while retry_count < 3:
                            try:
                                print(f'尝试重试 Chunk {chunk_idx}, 第 {retry_count+1} 次')
                                result = self._process_single_chunk(chunks_df.iloc[chunk_idx]["text"])
                                cached_results[cache_keys[chunk_idx]] = result
                                break
                            except Exception as retry_exc:
                                print(f'重试失败: {retry_exc}')
                                retry_count += 1
                                time.sleep(1)  # 短暂延迟
                        
                        if cached_results[cache_keys[chunk_idx]] is None:
                            cached_results[cache_keys[chunk_idx]] = ""
        
        # 整理结果
        chunks_df["extraction_result"] = [cached_results[key] for key in cache_keys]
        
        # 输出缓存统计
        cache_ratio = self.cache_hits / (self.cache_hits + self.cache_misses) * 100 if (self.cache_hits + self.cache_misses) > 0 else 0
        print(f"处理完成, 缓存命中率: {cache_ratio:.1f}%")
        
        process_time = time.time() - t0
        print(f"所有chunks处理完成, 总耗时: {process_time:.2f}秒, 平均每chunk: {process_time/total_chunks:.2f}秒")
        
        return chunks_df
    
    def process_chunks_batch(self, chunks_df: pd.DataFrame, progress_callback=None) -> pd.DataFrame:
        """
        批量处理chunks，减少LLM调用次数
        
        Args:
            chunks_df: 包含文本块的DataFrame
            progress_callback: 进度回调函数
            
        Returns:
            pd.DataFrame: 处理结果
        """
        # 智能动态批处理大小
        chunk_lengths = chunks_df["text"].str.len()
        avg_chunk_size = chunk_lengths.mean() if not chunk_lengths.empty else 0
        
        # 根据平均chunk大小动态调整批处理大小
        dynamic_batch_size = max(1, min(self.batch_size, int(10000 / (avg_chunk_size + 1))))
        
        results = []
        # 按批次处理
        for i in range(0, len(chunks_df), dynamic_batch_size):
            batch_df = chunks_df.iloc[i:i+dynamic_batch_size]
            
            # 缓存检查
            batch_keys = batch_df["text"].apply(self._generate_cache_key)
            cached_batch_results = [self._load_from_cache(key) for key in batch_keys]
            
            # 如果所有结果都已缓存，则跳过LLM调用
            if None not in cached_batch_results:
                results.extend(cached_batch_results)
                if progress_callback:
                    for j in range(len(batch_df)):
                        progress_callback(i + j)
                continue
            
            # 准备批处理输入
            batch_texts = batch_df["text"].tolist()
            batch_text = f"\n{'-'*50}\n".join(batch_texts)
            
            try:
                # 使用原始提示模板处理批量输入
                batch_response = self.chain.invoke({
                    "chat_history": self.chat_history,
                    "entity_types": self.entity_types,
                    "relationship_types": self.relationship_types,
                    "tuple_delimiter": self.tuple_delimiter,
                    "record_delimiter": self.record_delimiter,
                    "completion_delimiter": self.completion_delimiter,
                    "input_text": batch_text
                })
                
                # 解析批量响应
                batch_results = self._parse_batch_response(batch_response.content)
                
                # 处理结果数量不匹配的情况
                if len(batch_results) != len(batch_texts):
                    print(f"批处理结果数量不匹配 (期望 {len(batch_texts)}, 实际 {len(batch_results)}), 将单独处理每个chunk")
                    batch_results = []
                    for idx, text in enumerate(batch_texts):
                        # 检查缓存
                        cached_result = cached_batch_results[idx]
                        if cached_result is not None:
                            batch_results.append(cached_result)
                        else:
                            individual_result = self._process_single_chunk(text)
                            batch_results.append(individual_result)
                else:
                    # 缓存批处理结果
                    for idx, result in enumerate(batch_results):
                        if cached_batch_results[idx] is None:  # 只缓存未命中的结果
                            self._save_to_cache(batch_keys[idx], result)
                
                results.extend(batch_results)
            except Exception as e:
                print(f"批处理错误，切换到单个处理: {e}")
                for idx, text in enumerate(batch_texts):
                    try:
                        individual_result = self._process_single_chunk(text)
                        results.append(individual_result)
                    except Exception as e2:
                        print(f"单个chunk处理失败: {e2}")
                        results.append("")
            
            # 更新进度
            if progress_callback:
                for j in range(len(batch_df)):
                    progress_callback(i + j)
        
        chunks_df["extraction_result"] = results
        return chunks_df
    
    def _parse_batch_response(self, batch_content: str) -> List[str]:
        """解析批量响应，将其分割为单独的结果"""
        parts = batch_content.split(f"\n{'-'*50}\n")
        return [part.strip() for part in parts]
    
    @retry(times=3, exceptions=(Exception,), delay=1.0)
    def _process_single_chunk(self, input_text: str) -> str:
        """处理单个文本块（带缓存）"""
        # 生成缓存键
        cache_key = self._generate_cache_key(input_text)
        
        # 尝试从缓存加载
        cached_result = self._load_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # 未缓存，调用LLM处理
        response = self.chain.invoke({
            "chat_history": self.chat_history,
            "entity_types": self.entity_types,
            "relationship_types": self.relationship_types,
            "tuple_delimiter": self.tuple_delimiter,
            "record_delimiter": self.record_delimiter,
            "completion_delimiter": self.completion_delimiter,
            "input_text": input_text
        })
        
        result = response.content
        
        # 保存结果到缓存
        self._save_to_cache(cache_key, result)
        
        return result
    
    def stream_process_large_files(self, file_path: str, chunk_size: int = 5000, 
                                   structure_builder=None, graph_writer=None) -> None:
        """
        以流式方式处理大文件，避免一次性加载全部内容
        
        Args:
            file_path: 文件路径
            chunk_size: 块大小
            structure_builder: 结构构建器
            graph_writer: 图写入器
        """
        if not structure_builder or not graph_writer:
            print("需要提供structure_builder和graph_writer才能进行流式处理")
            return
            
        def text_chunks_iterator(file_path, chunk_size):
            with open(file_path, 'r', encoding='utf-8') as f:
                chunk = []
                chars_count = 0
                for line in f:
                    chunk.append(line)
                    chars_count += len(line)
                    if chars_count >= chunk_size:
                        yield chunk
                        chunk = []
                        chars_count = 0
                if chunk:  # 不要忘记最后一个可能不满的chunk
                    yield chunk
        
        # 处理文件的元数据
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_name)[1]
        
        # 创建文档节点
        structure_builder.create_document(
            type=file_type,
            uri=file_path,
            file_name=file_name,
            domain="document"
        )
        
        # 流式处理文件
        chunks = []
        for chunk in text_chunks_iterator(file_path, chunk_size):
            chunks.append(chunk)
        
        # 创建chunk之间的关系
        chunks_with_hash = structure_builder.create_relation_between_chunks(
            file_name, chunks
        )
        
        # 并行处理所有chunks
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 创建任务
            future_to_chunk = {}
            for chunk_data in chunks_with_hash:
                chunk_text = chunk_data['chunk_doc'].page_content
                cache_key = self._generate_cache_key(chunk_text)
                cached_result = self._load_from_cache(cache_key)
                
                if cached_result:
                    # 如果缓存命中，直接处理结果
                    try:
                        graph_document = graph_writer.convert_to_graph_document(
                            chunk_data['chunk_id'],
                            chunk_data['chunk_doc'].page_content,
                            cached_result
                        )
                        
                        if len(graph_document.nodes) > 0 or len(graph_document.relationships) > 0:
                            graph_writer.graph.add_graph_documents(
                                [graph_document],
                                baseEntityLabel=True,
                                include_source=True
                            )
                    except Exception as e:
                        print(f"处理缓存结果时出错: {e}")
                else:
                    # 如果缓存未命中，提交任务
                    future = executor.submit(self._process_single_chunk, chunk_text)
                    future_to_chunk[future] = chunk_data
            
            # 处理结果并写入图数据库
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk_data = future_to_chunk[future]
                try:
                    result = future.result()
                    
                    # 实时写入一个chunk的结果到图数据库
                    graph_document = graph_writer.convert_to_graph_document(
                        chunk_data['chunk_id'],
                        chunk_data['chunk_doc'].page_content,
                        result
                    )
                    
                    if len(graph_document.nodes) > 0 or len(graph_document.relationships) > 0:
                        graph_writer.graph.add_graph_documents(
                            [graph_document],
                            baseEntityLabel=True,
                            include_source=True
                        )
                        
                except Exception as exc:
                    print(f"处理chunk {chunk_data['chunk_id']} 时发生错误: {exc}")