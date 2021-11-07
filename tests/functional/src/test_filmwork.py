import http
import logging
from jsonschema import validate

import pytest

API_URL = "/films/"
logger = logging.getLogger(__name__)
pytestmark = pytest.mark.asyncio

async def test_film_get_by_id(
    make_get_request, initialize_environment, expected_schema
):
    some_id = "ad567e37-9f36-4328-8583-995461f0cbbc"
    response = await make_get_request(f"{API_URL}{some_id}", {})
    assert response.status == http.HTTPStatus.OK
    assert validate(response.body, expected_schema) is None
    assert some_id == response.body["id"]


async def test_film_get_all(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {})
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 2


async def test_film_filter_unknown_genre(make_get_request, initialize_environment):
    response = await make_get_request(API_URL, {"filter[genre]": "rewrwerewr"})
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    (
            "page", "size", "expected_count"
    ),
    (
            (1, 10000, 2),
            (1, 10, 2),
            (1, 1, 1),
    )
)
async def test_search_genre_pagination(make_get_request,
                                       initialize_environment,
                                       page,
                                       size,
                                       expected_count):
    response = await make_get_request(f"{API_URL}",
                                      params={
                                          "page": page,
                                          "size": size}
                                      )
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == expected_count


@pytest.mark.parametrize(
    (
            "page_number", "page_size"
    ),
    (
            (1, 0),
            (-1, 1),
            (-1, -1),
            ("_", 1),
            (1, "_"),
    )
)
async def test_search_person_pagination_invalid_input(make_get_request,
                                                      initialize_environment,
                                                      page_number,
                                                      page_size):
    response = await make_get_request(f"{API_URL}",
                                      params={
                                          "page": page_number,
                                          "size": page_size}
                                      )
    assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY

async def test_film_search(make_get_request,
                           initialize_environment,
                           expected_json_response):
    response = await make_get_request(
        f"{API_URL}",
        {"query": "embrace"}
    )
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body == expected_json_response


async def test_film_filter_invalid(make_get_request, initialize_environment):
    response = await make_get_request(
        f"{API_URL}",
        {"filter[genre]": "fdsfdsfdsfdf"}
    )
    assert response.status == http.HTTPStatus.NOT_FOUND


async def test_film_cache(make_get_request, initialize_environment, es_client):
    request = (f"{API_URL}", {"page[number]": 1, "page[size]": 1})
    cache_response = await make_get_request(*request)
    assert cache_response.status == http.HTTPStatus.OK
    await es_client.indices.delete(index="movies", ignore=[http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.NOT_FOUND])

    response = await make_get_request(*request)
    assert response.status == http.HTTPStatus.OK
    assert response.body == cache_response.body
