import http
from jsonschema import validate

import pytest

API_URL = "/genres/"
pytestmark = pytest.mark.asyncio

async def test_genres_get_by_id(
    make_get_request, initialize_environment, expected_schema
):
    some_id = "64623db7-f97a-459b-a5eb-5c5cf97f1f69"
    response = await make_get_request(f"{API_URL}{some_id}", {})
    assert response.status == http.HTTPStatus.OK
    assert validate(response.body, expected_schema) is None
    assert some_id == response.body["id"]


async def test_genres_get_all(make_get_request, initialize_environment):
    response = await make_get_request(f"{API_URL}")
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 3


@pytest.mark.parametrize(
    (
            "page", "size", "expected_count"
    ),
    (
            (1, 10000, 3),
            (1, 10, 3),
            (1, 2, 2),
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


async def test_genres_cache(make_get_request, initialize_environment, es_client):
    request = (f"{API_URL}", {"page[number]": 1, "page[size]": 1})
    cache_response = await make_get_request(*request)
    assert cache_response.status == http.HTTPStatus.OK
    await es_client.indices.delete(index="genres", ignore=[http.HTTPStatus.BAD_REQUEST, http.HTTPStatus.NOT_FOUND])

    response = await make_get_request(*request)
    assert response.status == http.HTTPStatus.OK
    assert response.body == cache_response.body