from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi_cache.decorator import cache

from api.v1.constants import PAGE_PARAM, SIZE_PARAM
from common.utils import ModelCoder
from core.config import FIVE_MIN
from models.genre import Genre, GenreDetail
from services.genre_service import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}',
            response_model=Genre,
            summary='Search by genre',
            description='Search for a genre by its id (uuid)',
            response_description='Dictionary with genre attributes',
            tags=['Search by id'])
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def genre_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Provides information about a genre by its id

    :param genre_id: genre ID
    :param genre_service: service for working with ES
    """

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return genre


@router.get('/', response_model=list[GenreDetail])
@cache(expire=FIVE_MIN, coder=ModelCoder)
async def genres_all(
        page: int = PAGE_PARAM,
        size: int = SIZE_PARAM,
        genre_service: GenreService = Depends(get_genre_service)) -> list[GenreDetail]:
    return await genre_service.get_all(page, size)

