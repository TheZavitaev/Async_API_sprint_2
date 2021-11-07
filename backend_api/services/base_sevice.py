import logging
from typing import Optional
from uuid import UUID
from urllib3.exceptions import HTTPError

import backoff
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError, ElasticsearchException
from elasticsearch_dsl import Q, Search
from models.base import BaseModel

logger = logging.getLogger(__name__)

class BaseService:

    index: str
    model: BaseModel
    fields: list

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(ElasticsearchException, HTTPError),
    )
    async def get_by_id(self, item_id: UUID) -> Optional[BaseModel]:
        """
        Получение одной записи по id
        :param item_id: идентификатор записи
        :return: экземпляра модели
        """
        item = await self._get_from_elastic(item_id)
        if not item:
            return None
        logger.info(item)
        return self.model(**item)

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(ElasticsearchException, HTTPError),
    )
    async def get_all(self, page: int, size: int):
        """
        Получение всех записей с пагинацей
        :param page: номер страницы
        :param size: количество элементов на странице
        :return: массив экземпляров модели
        """
        return await self.search(page, size)

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(ElasticsearchException, HTTPError)
    )
    async def search(
            self,
            page: int,
            size: int,
            query: Optional[str] = None,
            filter: Optional[str] = None,
            sort: Optional[str] = None,
    ):
        """
        Поиск по параметрам
        :param page: номер страницы
        :param size: количество элементов на странице
        :param query: запрос
        :param filter: фильтр
        :param sort: сортировка
        :return: массив экземпляров модели
        """

        search_query = Search(using=self.elastic, index=self.index)
        start = (page - 1) * size
        search_query = search_query[start: start + size]
        if query:
            search_query = search_query.query("multi_match", query=query, fields=self.fields)
        if filter:
            search_query = search_query.query("bool", filter=Q("term", genre=filter))
        if sort:
            search_query = search_query.sort(sort)
        items = await self._search_elastic(search_query.to_dict())
        return [self.model(**item["_source"]) for item in items]

    async def _get_from_elastic(self, item_id: UUID) -> Optional[BaseModel]:
        """
        Получение записи по id из elastic
        :param item_id: id для поиска
        :return: экземпляра модели
        """
        try:
            doc = await self.elastic.get(self.index, item_id)
            return doc["_source"]
        except NotFoundError:
            return None

    async def _search_elastic(self, data: dict) -> list[BaseModel]:
        """
        Поиск в elastic
        :param data:
        :return: массив найденных элементов
        """
        docs = await self.elastic.search(index=self.index, body=data)
        return docs["hits"]["hits"]
