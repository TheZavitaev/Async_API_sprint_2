import logging
import json
from typing import Any

from fastapi_cache.coder import Coder, JsonEncoder, object_hook
from starlette.authentication import AuthCredentials

from core import permissions

logger = logging.getLogger(__name__)


class ModelCoder(Coder):
    @classmethod
    def encode(cls, value: Any):
        if isinstance(value, list):
            return json.dumps([obj.dict() for obj in value], cls=JsonEncoder)
        return json.dumps(value, cls=JsonEncoder)

    @classmethod
    def decode(cls, value: Any):
        return json.loads(value, object_hook=object_hook)


def can_read_suspicious(auth: AuthCredentials) -> bool:
    logger.info(f'can_read_suspicious, scopes: {auth.scopes}')
    return permissions.Permissions.SUSPICIOUS_READ in auth.scopes
