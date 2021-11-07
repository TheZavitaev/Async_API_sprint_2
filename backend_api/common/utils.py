import logging
import json
from typing import Any

from fastapi_cache.coder import Coder, JsonEncoder, object_hook
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
