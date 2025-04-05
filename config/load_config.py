from config.model.llm_config import LanguageModelConfig
from pathlib import Path
import yaml
from yaml.error import YAMLError
import logging

def _load_llm_config(config: Path) -> LanguageModelConfig:
    try:
        config_dict = yaml.safe_load(config.read_text())
        return LanguageModelConfig(**config_dict)
    except (YAMLError, FileNotFoundError) as e:
        error_msg = f"配置文件读取失败: {str(e)}"
        logging.error(error_msg)
        raise ValueError(error_msg)
    except (PermissionError, TypeError) as e:
        error_msg = f"配置文件访问或格式错误: {str(e)}"
        logging.error(error_msg)
        raise ValueError(error_msg)

