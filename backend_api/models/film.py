from enum import Enum
from typing import Optional

from models.base import BaseModel
from models.person import Person


class FilmWorkTypeEnum(str, Enum):
    """
    Expandable model of possible types of film productions.
    """
    movie = 'movie'
    serial = 'serial'
    tv_show = 'tv_show'


class MPAA_AgeRatingType(str, Enum):
    G = "general"
    PG = "parental_guidance"
    PG_13 = "parental_guidance_strong"
    R = "restricted"
    NC_17 = "no_one_17_under"


class Film(BaseModel):
    """
    Film model.
    """
    title: str
    description: str
    imdb_rating: Optional[float] = 0.0
    genres: list[str] = []
    directors: list[Person] = []
    actors: list[Person] = []
    writers: list[Person] = []


class FilmShort(BaseModel):
    title: str
    description: str
    imdb_rating: Optional[float]
