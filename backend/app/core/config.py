from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Stock Screening"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 调试模式
    DEBUG: bool = True
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # AI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    AI_MODEL_NAME: str = "gpt-3.5-turbo"
    
    # AkShare 配置
    AKSHARE_TIMEOUT: int = 30
    
    # 数据配置
    DEFAULT_STOCK_SYMBOLS: List[str] = ["sh600000", "sh600036", "sz000001", "sz000858"]
    DEFAULT_HISTORY_DAYS: int = 180
    
    # 服务器配置
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
