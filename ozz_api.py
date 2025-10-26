from master_ozz import ozz_router
from master_ozz.utils import ozz_master_root, return_app_ip, ozzapi_script_Parser
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
    ip_address, streamlit_ip = return_app_ip()
    if ip_address == "https://api.divergent-thinkers.com":
        host = '127.0.0.1'
        port=8000
    else:
        ip_address = ip_address.split("//")[-1]
        host = ip_address.split(":")[0]
        port = int(ip_address.split(":")[-1])

        # """ TESTING for Other Devices """
        # host = '0.0.0.0'  # Allow external access
        # port = 8000       # Set your desired port (commonly 8000, 5000, or 3001)
    
    # update to handle both
    # parser = ozzapi_script_Parser()
    # namespace = parser.parse_args()
    # ip_address = namespace.ip # 127.0.0.1
    # port=int(namespace.port) # 8000

    uvicorn.run(app, host=host, port=port) # '10.3.144.157'