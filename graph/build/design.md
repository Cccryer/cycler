(:Document {
    id: String,           // 文档唯一标识符
    title: String,        // 文档标题
    source: String,       // 文档来源
    created_at: DateTime, // 创建时间
    updated_at: DateTime  // 更新时间
})

(:Chunk {
    id: String,           // 文本块唯一标识符
    content: String,      // 文本内容
    start_index: Integer, // 在文档中的起始位置
    end_index: Integer,   // 在文档中的结束位置
    embedding: Vector     // 文本向量表示（可选）
})

(:Entity {
    id: String,           // 实体唯一标识符
    name: String,         // 实体名称
    type: String,         // 实体类型（如：人物、地点、组织等）
    description: String,  // 实体描述
    confidence: Float     // 实体识别的置信度
})

(:Document)-[:CONTAINS {
    created_at: DateTime  // 关系创建时间
}]->(:Chunk)

(:Chunk)-[:MENTIONS {
    start_index: Integer, // 实体在文本中的起始位置
    end_index: Integer,   // 实体在文本中的结束位置
    confidence: Float     // 关系置信度
}]->(:Entity)
