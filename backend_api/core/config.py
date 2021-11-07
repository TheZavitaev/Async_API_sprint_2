import os
from datetime import timedelta
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "es")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Standard cache time
FIVE_MIN = int(timedelta(minutes=5).total_seconds())

JWT_PUBLIC_KEY: str = os.getenv('JWT_PUBLIC_KEY')
JWT_ALGORITHM: str = 'RS256'
