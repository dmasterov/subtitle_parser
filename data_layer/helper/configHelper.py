import yaml
from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoConfig:
    video_id: str

@dataclass
class CefrLevel:
    min_level: float
    max_level: float

@dataclass
class DictionaryApiConfig:
    api_url: str
    max_concurrent_requests: int
    max_retries: int
    retry_backoff_base: float

@dataclass
class TranslationConfig:
    target_language: str
    min_translate_level: float

@dataclass
class MongoDBConfig:
    username: str
    password: str
    host: str
    port: int
    db_name: str
    collection_name: str

@dataclass
class AppConfig:
    video: VideoConfig
    cefr: CefrLevel
    dictionary_api: DictionaryApiConfig
    translation: TranslationConfig
    mongodb: MongoDBConfig

def load_config(path: str) -> AppConfig:
    with open(path, 'r') as f:
        raw = yaml.safe_load(f)
    return AppConfig(
        video=VideoConfig(**raw['video']),
        cefr=CefrLevel(**raw['cefr']),
        dictionary_api=DictionaryApiConfig(**raw['dictionary_api']),
        translation=TranslationConfig(**raw['translation']),
        mongodb=MongoDBConfig(**raw['mongodb'])  # Uncomment if MongoDB config is needed
    )
