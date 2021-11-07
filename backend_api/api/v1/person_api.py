from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache
from starlette import status

from api.v1.constants import PAGE_PARAM, SIZE_PARAM
from common.utils import ModelCoder
from core.config import FIVE_MIN
from models.person import Person
from services.persons_service import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id:uuid}', response_model=Person)
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def person_details(person_id: UUID,
                         person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='person not found')

    return person


@router.get('/', response_model=list[Person])
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def person_search(
        query: Optional[str] = Query(''),
        sort: Optional[str] = Query(None, regex='^-?[a-zA-Z_]+$'),
        page: int = PAGE_PARAM,
        size: int = SIZE_PARAM,
        person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.search(
        query=query, sort=sort, size=size, page=page
    )
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='person not found')

    return [Person(id=person.id, name=person.name, roles=person.roles, film_ids=person.film_ids)
            for person in persons]
