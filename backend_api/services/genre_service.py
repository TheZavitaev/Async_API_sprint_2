from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.genre import Genre
from services.base_sevice import BaseService


class GenreService(BaseService):
    """
    Accesses ElasticSearch and returns genre information
    """
    index = 'genres'
    model = Genre
    fields = [
        'name',
    ]




@lru_cache
def get_genre_service(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:

    return GenreService(elastic)
