from fastapi import status, Body
from fastapi.responses import JSONResponse, FileResponse

import ipdb
import openai
from dotenv import load_dotenv
import os
import json

from master_ozz.ozz_query import ozz_query
from master_ozz.utils import ozz_master_root, init_constants

from fastapi import APIRouter
router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)
# from fastapi import FastAPI
# router = FastAPI()

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

@router.get("/{file_name}")
def get_file(file_name: str):
    constants = init_constants()
    OZZ_db_audio = constants.get('OZZ_db_audio')
    OZZ_db_images = constants.get('OZZ_db_images')
    file_path = os.path.join(OZZ_db_audio, file_name)
    
    # Determine the media type based on the file extension
    media_type = "application/octet-stream"
    if file_name.lower().endswith(".mp3"):
        media_type = "audio/mp3"
        file_path = os.path.join(OZZ_db_audio, file_name)
    elif file_name.lower().endswith(".png"):
        media_type = "image/png"
        file_path = os.path.join(OZZ_db_images, file_name)
    elif file_name.lower().endswith(".gif"):
        media_type = "image/gif"
        file_path = os.path.join(OZZ_db_images, file_name)

    return FileResponse(file_path, media_type=media_type)

@router.get("/test", status_code=status.HTTP_200_OK)
def load_ozz_voice():
    json_data = {'msg': 'test'}
    return JSONResponse(content=json_data)

@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...), refresh_ask=Body(...), face_data=Body(...), client_user=Body(...), force_db_root=Body(...), session_listen=Body(...), before_trigger_vars=Body(...), tigger_type=Body(...)):
    # print(f'face data {face_data}')
    print(f'trig TYPE: {tigger_type} {before_trigger_vars}')
    
    if api_key != os.environ.get("ozz_key"): # fastapi_pollenq_key
        print("Auth Failed", api_key)
        # Log the trader WORKERBEE
        return "NOTAUTH"

    json_data = ozz_query(text, self_image, refresh_ask, client_user, force_db_root, session_listen, before_trigger_vars)
    return JSONResponse(content=json_data)