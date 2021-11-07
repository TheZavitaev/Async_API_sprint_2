from uuid import UUID

from models.base import BaseModel
from models.film import FilmShort


class Genre(BaseModel):
    """
    Genre model.
    """

    name: str


class GenreDetail(BaseModel):
    name: str
    filmworks: list[FilmShort] = []
