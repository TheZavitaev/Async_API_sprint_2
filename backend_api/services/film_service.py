from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from services.base_sevice import BaseService


class FilmService(BaseService):
    index = "movies"
    model = Film
    fields = [
        "title",
        "description",
        "genres_names",
        "actors_names",
        "writers_names",
        "directors_names",
    ]


@lru_cache
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
