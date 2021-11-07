from datetime import date
from typing import Optional
from uuid import UUID

from models.base import BaseModel


class Person(BaseModel):
    """
    Person model.
    Describes a person, contains a list of works in which he participated in a specific position.
    """

    name: str
    birth_date: Optional[date] = None
    roles: list[UUID] = []
    film_ids: list[UUID] = []
