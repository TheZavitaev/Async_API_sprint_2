import http
import logging
from jsonschema import validate

import pytest

API_URL = "/persons/"

LOGGER = logging.getLogger(__name__)
pytestmark = pytest.mark.asyncio

async def test_persons_get_by_id(
    make_get_request, initialize_environment, expected_schema
):
    some_id = "f8720aab-2fff-4d1d-a430-215314af4204"
    response = await make_get_request(f"{API_URL}{some_id}", {})
    assert response.status == http.HTTPStatus.OK
    assert validate(response.body, expected_schema) is None
    assert some_id == response.body["id"]


async def test_persons_get_all(make_get_request, initialize_environment):
    response = await make_get_request(f"{API_URL}")
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 3
