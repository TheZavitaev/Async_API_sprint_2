import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache.decorator import cache
from api.v1.constants import PAGE_PARAM, SIZE_PARAM
from models.film import Film, FilmShort
from services.film_service import FilmService, get_film_service
from common.utils import ModelCoder
from core.config import FIVE_MIN

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{film_id}", response_model=Film)
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="film not found")
    return film


@router.get("/", response_model=list[FilmShort])
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def film_search(
    query: Optional[str] = Query(""),
    filter_genre: Optional[str] = Query(None, alias="filter[genre]"),
    sort: Optional[str] = Query(None, regex="^-?[a-zA-Z_]+$"),
    page: int = PAGE_PARAM,
    size: int = SIZE_PARAM,
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    films = await film_service.search(
        query=query, sort=sort, filter=str(filter_genre) if filter_genre else None, size=size, page=page
    )
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="films not found")

    return [FilmShort(id=film.id, title=film.title, description=film.description) for film in films]
