from master_ozz import ozz_router
from master_ozz.utils import ozz_master_root, get_ip_address, ozzapi_script_Parser
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request
import argparse

# from fastapi import APIRouter
# router = APIRouter() 
app = FastAPI()

import os
main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))


origins = []


app.include_router(ozz_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(HTTPSRedirectMiddleware) # returned 307 temporary redirect but did not work

# @app.route('/{_:path}')
# async def https_redirect(request: Request):
#     return RedirectResponse(request.url.replace(scheme='https'))

@app.get("/", status_code=status.HTTP_200_OK, tags=["API Check"])
def check():
    return {
        "message": "Hello Ozz"
    }

# from starlette.responses import Response

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

# from redis import asyncio as aioredis

# app = FastAPI()


# @cache()
# async def get_cache():
#     return 1


# @app.get("/")
# @cache(expire=60)
# async def index():
#     return dict(hello="world")


# @app.on_event("startup")
# async def startup():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == '__main__':

    parser = ozzapi_script_Parser()
    namespace = parser.parse_args()
    ip_address = namespace.ip
    port=int(namespace.port)

    uvicorn.run(app, host=ip_address, port=port) # '10.3.144.157'