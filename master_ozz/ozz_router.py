from fastapi import status, Body
import ipdb
import openai
from dotenv import load_dotenv
import os
import json

from fastapi.responses import JSONResponse
from master_ozz.ozz_query import ozz_query
from master_ozz.utils import ozz_master_root

from fastapi import APIRouter
router = APIRouter(
    prefix="/api/data",
    tags=["auth"]
)
# from fastapi import FastAPI
# router = FastAPI()

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

# setting up FastAPI

# Loading the environment variables

@router.get("/test", status_code=status.HTTP_200_OK)
def load_ozz_voice():
    json_data = {'msg': 'test'}
    return JSONResponse(content=json_data)

@router.post("/voiceGPT", status_code=status.HTTP_200_OK)
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...)): #, client_user=Body(...)):
    # print(client_user)
    # Test Queries with user and assistant and saving in conversation history as well as json file
    # text = [{"role": "system", "content": "You are a cute and smart assistant for kids."},
    #         {'role':'user','content': 'hey hootie tell me a story'}]
    # text = [  # future state
    #         {"role": "system", "content": "You are a cute and smart assistant for kids."},
    #         {'role':'user', 'content': 'hey hootie tell me a story'}, {'role':'assistant','content': 'what story would you like to hear'}, 
    #         {'role':'user','content': 'any kind of kid related'}
    #        ]


    json_data = ozz_query(text, self_image)
    return JSONResponse(content=json_data)