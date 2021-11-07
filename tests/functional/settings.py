from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    es_host: str = Field("test_es", env="ES_HOST")
    es_port: str = Field("9200", env="ES_PORT")
    api_host: str = Field("http://127.0.0.1:8000", env="API_HOST")
    redis_host: str = Field("test_redis", env="REDIS_HOST")
    redis_port: str = Field("6379", env="REDIS_PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    es_schemas_dir: Path = Field("tests/functional/testdata/schemes")
    fake_data_dir: Path = Field("tests/functional/testdata")
    es_indexes: tuple = Field(("movies", "genres", "persons"))
    api_url: str = Field("/v1")
    service_url: str = Field("test_api:8000")
    expected_response_dir: Path = Field("/tests/functional/testdata/expected_response")
    expected_schema_dir: Path = Field("/tests/functional/testdata/schemes")
