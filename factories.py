import random

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from movies.models import (
    Filmwork,
    FilmWorkGenre,
    FilmWorkPerson,
    FilmworkType,
    Genre,
    MPAA_AgeRatingType,
    Person,
    RoleType,
)

# Defining a factory


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.Faker("name")


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Faker("company")


class FilmworkFactory(DjangoModelFactory):
    class Meta:
        model = Filmwork

    title = factory.Faker("bs")
    description = factory.Faker("sentence", nb_words=128, variable_nb_words=True)
    rating = factory.LazyAttribute(lambda x: random.randrange(1, 11))
    mpaa_age_rating = FuzzyChoice(MPAA_AgeRatingType)
    type = FuzzyChoice(FilmworkType)
    file_path = factory.Faker("file_path")


class FilmWorkPersonFactory(DjangoModelFactory):
    class Meta:
        model = FilmWorkPerson

    role = FuzzyChoice(RoleType)
    film_work_id = factory.SubFactory(FilmworkFactory)
    person_id = factory.SubFactory(PersonFactory)


class FilmWorkGenreFactory(DjangoModelFactory):
    class Meta:
        model = FilmWorkGenre

    film_work_id = factory.SubFactory(FilmworkFactory)
    genre_id = factory.SubFactory(GenreFactory)
