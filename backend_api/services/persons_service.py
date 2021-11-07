from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person
from services.base_sevice import BaseService


class PersonService(BaseService):
    index = 'persons'
    model = Person
    fields = [
        'name',

    ]


def get_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(elastic)
