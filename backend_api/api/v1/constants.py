from fastapi import Query

# Default api query params
PAGE_PARAM = Query(default=1, ge=1)
SIZE_PARAM = Query(default=10, ge=1)
