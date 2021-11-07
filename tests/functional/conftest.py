import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime

import aiofiles
import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch._async.helpers import async_bulk
from multidict import CIMultiDictProxy
from redis import Redis

from .settings import Settings

settings = Settings()
API_URL = settings.api_url
SERVICE_URL = settings.service_url

logger = logging.getLogger(__name__)

PENDING = 30


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def es_client(settings):
    client = AsyncElasticsearch([{"host": f"{settings.es_host}", "port": f"{settings.es_port}"}])
    yield client
    await client.close()


@pytest.fixture(scope="session", autouse=True)
async def redis_client(settings) -> Redis:
    host = f"{settings.redis_host}:{settings.redis_port}"
    host = "redis://" + host
    redis = aioredis.from_url(
        host, max_connections=10, encoding="utf8", decode_responses=True
    )
    yield redis
    redis.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        url = f"http://{SERVICE_URL}{API_URL}{method}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture(scope="session")
def clear_cache(redis_client):
    """
    Очистить Redis cache
    """
    redis_client.flushall()


async def initialize_es_index(es_client, index_name, settings):
    await create_index(es_client, index_name, settings)
    await load_data_in_index(es_client, index_name, settings)


async def create_index(es_client, index_name, settings):
    index_path = settings.es_schemas_dir.joinpath(f"{index_name}.json")
    index = read_json_file(index_path)
    await es_client.indices.create(index=index_name, body=index, ignore=400)


async def load_data_in_index(es_client, index_name, settings):
    data_path = settings.fake_data_dir.joinpath(f"{index_name}.json")
    data = read_json_file(data_path)
    await async_bulk(es_client, data, index=index_name)

    items = {}
    start_time = datetime.now()

    while not items.get("count"):
        items = await es_client.count(index=index_name)
        seconds = (datetime.now() - start_time).seconds

        if seconds >= PENDING:
            raise TimeoutError(f"Time-out for loading data into ES index {index_name}.")


@pytest.fixture(scope="session")
async def initialize_environment(es_client, redis_client, settings):
    for index in settings.es_indexes:
        await initialize_es_index(es_client, index, settings)
    yield
    for index in settings.es_indexes:
        await es_client.indices.delete(index=index, ignore=[400, 404])

@pytest.fixture(scope="function")
async def expected_schema(request):
    logger.info(request)
    file = Settings().expected_schema_dir.joinpath(f"{request.node.name}.json")
    async with aiofiles.open(file) as f:
        content = await f.read()
        response = json.loads(content)
    return response

@pytest.fixture(scope="function")
async def expected_json_response(request):
    file = Settings().expected_response_dir.joinpath(f"{request.node.name}.json")
    async with aiofiles.open(file) as f:
        content = await f.read()
        response = json.loads(content)
    return response


def read_json_file(file_path):
    with open(file_path) as json_file:
        json_data = json.load(json_file)
    return json_data
