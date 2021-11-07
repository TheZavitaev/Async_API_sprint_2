from __future__ import annotations

from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch | None:
    return es
