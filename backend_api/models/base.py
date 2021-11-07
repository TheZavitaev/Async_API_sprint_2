from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel, Field
import orjson


def orjson_dumps(v, *, default) -> str:
    """
    Speeds up serialization.

    Docs: https://github.com/ijl/orjson
    """

    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    """
    Base model.

    Changing pydantic base model:
    https://pydantic-docs.helpmanual.io/usage/model_config/#change-behaviour-globally
    """

    id: UUID = Field(default_factory=uuid4)

    class Config:
        arbitrary_types_allowed = True
        json_loads = orjson.loads
        json_dumps = orjson.dumps
