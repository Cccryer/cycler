import logging
import pandas as pd
from config.model.input_config import InputConfig
from storage.base.pipeline_storage import PipelineStorage
import re
from typing import Callable, Dict
from utils.hashing import gen_sha512_hash
from pathlib import Path
logger = logging.getLogger(__name__)

'''
    加载文件到pd.DataFrame
'''

# 文件加载器注册表
_LOADERS: Dict[str, Callable[[str, PipelineStorage, InputConfig], pd.DataFrame]] = {}

def register_loader(file_type: str) -> Callable:
    """注册文件加载器的装饰器"""
    def decorator(loader_func: Callable) -> Callable:
        _LOADERS[file_type] = loader_func
        return loader_func
    return decorator

def get_loader(file_type: str) -> Callable:
    """获取指定类型的文件加载器"""
    if file_type not in _LOADERS:
        raise ValueError(f"未注册的文件类型: {file_type}")
    return _LOADERS[file_type]

async def load_file(
    path: str,
    storage: PipelineStorage,
    config: InputConfig,
    group: dict | None = None
) -> pd.DataFrame:
    """加载单个文件"""
    loader = get_loader(config.file_type)
    return await loader(path, storage, config, group)

async def load_files(
    config: InputConfig,
    storage: PipelineStorage,
) -> pd.DataFrame:
    """加载文件并应用加载器函数"""
    files = list(
        storage.find(
            re.compile(config.file_pattern),
            file_filter=config.file_filter,
        )
    )

    if len(files) == 0:
        msg = f"No {config.file_type} files found in {config.base_dir}"
        raise ValueError(msg)
    
    files_loaded = []

    for file, group in files:
        try:
            df = await load_file(file, storage, config, group)
            # 添加分组信息
            for key, value in group.items():
                df[key] = value
            files_loaded.append(df)
        except Exception as e:  # noqa: BLE001 (catching Exception is fine here)
            logger.warning("Warning! Error loading file %s. Skipping...", file)
            logger.warning("Error: %s", e)

    logger.info(
        "Found %d %s files, loading %d", len(files), config.file_type, len(files_loaded)
    )
    result = pd.concat(files_loaded)
    total_files_log = (
        f"Total number of unfiltered {config.file_type} rows: {len(result)}"
    )
    logger.info(total_files_log)
    return result


@register_loader("csv")
async def load_csv_file(
    path: str,
    storage: PipelineStorage,
    config: InputConfig,
    group: dict | None = None
) -> pd.DataFrame:
    """加载CSV文件"""
    content = await storage.get(path, encoding=config.encoding)
    return pd.read_csv(pd.StringIO(content))


@register_loader("txt")
async def load_txt_file(
    path: str,
    storage: PipelineStorage,
    config: InputConfig,
    group: dict | None = None
) -> pd.DataFrame:
    """加载TXT文件"""
    if group is None:
        group = {}
    content = await storage.get(path, encoding=config.encoding)
    new_item = {**group, "text": content}
    new_item["id"] = gen_sha512_hash(new_item, new_item.keys())
    new_item["title"] = str(Path(path).name)
    new_item["creation_date"] = await storage.get_creation_date(path)
    return pd.DataFrame([new_item])

@register_loader("json")
async def load_json_file(
    path: str,
    storage: PipelineStorage,
    config: InputConfig,
    group: dict | None = None 
) -> pd.DataFrame:
    """加载JSON文件"""
    content = await storage.get(path, encoding=config.encoding)
    return pd.read_json(pd.StringIO(content))
