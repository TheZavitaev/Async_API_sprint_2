import logging

import aioredis
import jwt
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from jwt import PyJWTError
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware

from api.v1 import film_api, genre_api, person_api
from core import config
from core.logger import LOGGING
from core.permissions import Permissions
from core.registry import filter_suspicious
from db import elastic
from db import redis_bd


class JWTAuthBackend(AuthenticationBackend):
    def __init__(
            self, secret_key: str = config.JWT_PUBLIC_KEY,
            algorithm: str = config.JWT_ALGORITHM,
            prefix: str = config.JWT_PREFIX
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str):
        try:
            scheme, token = authorization.split()
            if scheme.lower() != prefix.lower():
                logging.debug('not bearer auth')
                raise AuthenticationError(f'Authorization scheme {scheme} is not supported')

        except ValueError:
            logging.debug(f'Invalid authorization header: {authorization}')
            raise AuthenticationError('Invalid authorization')

        if not token:
            logging.debug('no token')
            return None

        return token

    async def authenticate(self, request):
        if 'Authorization' not in request.headers:
            logging.debug('user no auth')
            return None

        authorization = request.headers['Authorization']
        token = self.get_token_from_header(authorization=authorization, prefix=self.prefix)

        try:
            jwt_decoded = jwt.decode(token, key=str(self.secret_key), algorithms=self.algorithm)

        except PyJWTError as err:
            logging.error(str(err))
            logging.exception('invalid token, user is unauthenticated')
            raise AuthenticationError('Invalid credentials')

        permissions = jwt_decoded['permissions']

        if Permissions.SUSPICIOUS_READ in permissions:
            filter_suspicious.set(False)

        logging.debug(f'token is valid, user: {jwt_decoded["sub"]} permissions: {permissions}, jwt: {jwt_decoded}')

        return AuthCredentials(permissions), SimpleUser(jwt_decoded['sub'])


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

# https://fastapi.tiangolo.com/advanced/middleware/
app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())


@app.on_event("startup")
async def startup():
    redis_bd.redis = aioredis.from_url(f"redis://{config.REDIS_HOST}:6379", encoding="utf8", decode_responses=True)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
    FastAPICache.init(RedisBackend(redis_bd.redis), prefix="fastapi-cache")


app.include_router(film_api.router, prefix="/v1/films", tags=["films"])
app.include_router(genre_api.router, prefix="/v1/genres", tags=["genres"])
app.include_router(person_api.router, prefix="/v1/persons", tags=["persons"])


@app.on_event("shutdown")
async def shutdown():
    await redis_bd.redis.close()
    await elastic.es.close()


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                log_config=LOGGING,
                log_level=logging.DEBUG,
                reload=True)
