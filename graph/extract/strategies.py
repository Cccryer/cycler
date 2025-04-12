from graph.extract.typing import Document, EntityTypes, EntityExtractionResult, StrategyConfig, WorkflowCallbacks
from config.model.llm_config import LanguageModelConfig
from llm.manager import ModelManager
from llm.protocol.base import ChatModel
from graph.extract.extractor import GraphExtractor
import networkx as nx

async def run_graph_intelligence(
    docs: list[Document],
    entity_types: EntityTypes,
    args: StrategyConfig,
) -> EntityExtractionResult:
    """Run the graph intelligence entity extraction strategy."""
    llm_config = LanguageModelConfig(**args["llm"])

    llm = ModelManager.get_instance().get_or_create_chat_model(
        name="extract_graph",
        model_type="openai_chat",
        config=llm_config,
    )

    return await run_extract_graph(llm, docs, entity_types, args)


async def run_extract_graph(
    model: ChatModel,
    docs: list[Document],
    entity_types: EntityTypes,
    callbacks: WorkflowCallbacks | None,
    args: StrategyConfig,
) -> EntityExtractionResult:
    """Run the entity extraction chain."""
    tuple_delimiter = args.get("tuple_delimiter", None)
    record_delimiter = args.get("record_delimiter", None)
    completion_delimiter = args.get("completion_delimiter", None)
    extraction_prompt = args.get("extraction_prompt", None)
    encoding_model = args.get("encoding_name", None)
    max_gleanings = args.get("max_gleanings", 1)

    extractor = GraphExtractor(
        model_invoker=model,
        prompt=extraction_prompt,
        encoding_model=encoding_model,
        max_gleanings=max_gleanings,
        on_error=lambda e, s, d: (
            callbacks.error("Entity Extraction Error", e, s, d) if callbacks else None
        ),
    )
    text_list = [doc.text.strip() for doc in docs]

    results = await extractor(
        list(text_list),
        {
            "entity_types": entity_types,
            "tuple_delimiter": tuple_delimiter,
            "record_delimiter": record_delimiter,
            "completion_delimiter": completion_delimiter,
        },
    )

    graph = results.output
    # Map the "source_id" back to the "id" field
    for _, node in graph.nodes(data=True):  # type: ignore
        if node is not None:
            node["source_id"] = ",".join(
                docs[int(id)].id for id in node["source_id"].split(",")
            )

    for _, _, edge in graph.edges(data=True):  # type: ignore
        if edge is not None:
            edge["source_id"] = ",".join(
                docs[int(id)].id for id in edge["source_id"].split(",")
            )

    entities = [
        ({"title": item[0], **(item[1] or {})})
        for item in graph.nodes(data=True)
        if item is not None
    ]

    relationships = nx.to_pandas_edgelist(graph)

    return EntityExtractionResult(entities, relationships, graph)
