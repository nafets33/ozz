from fastapi import status, Body
import ipdb
import openai
from dotenv import load_dotenv
import os
import json

from fastapi.responses import JSONResponse
from master_ozz.ozz_query import Scenarios
from master_ozz.utils import ozz_master_root, generate_audio, save_audio

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
def load_ozz_voice(api_key=Body(...), text=Body(...), self_image=Body(...)):
    # Test Queries with user and assistant and saving in conversation history as well as json file
    # text = [{"role": "system", "content": "You are a cute and smart assistant for kids."},
    #         {'role':'user','content': 'hey hootie tell me a story'}]
    # text = [  # future state
    #         {"role": "system", "content": "You are a cute and smart assistant for kids."},
    #         {'role':'user', 'content': 'hey hootie tell me a story'}, {'role':'assistant','content': 'what story would you like to hear'}, 
    #         {'role':'user','content': 'any kind of kid related'}
    #        ]
    # ipdb.set_trace()

    # /Users/stefanstapinski/ENV/ozz/ozz/custom_voiceGPT/frontend/build/
    def handle_image(text, self_image):
        # based on LLM response handle image if needs to change
        self_image = 'hootsAndHootie.png'

        return self_image
    def handle_audio(response, new_audio=True, filename='temp_audio.mp3', audio_dir='/Users/stefanstapinski/ENV/ozz/ozz/custom_voiceGPT/frontend/build/'):
        if new_audio:
            audio = generate_audio(query=response)
            save_audio(os.path.join(audio_dir, filename), audio)
            # print("Audio Saved ", filename)
        return filename

    def handle_response(text : str):
        # Kids or User question
        # ipdb.set_trace()
        text_obj = text[-1]['user'] # user query
        
        conversation_history_file_path = 'master_ozz/conversation_history.json'

        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'r') as conversation_history_file:
            conversation_history = json.load(conversation_history_file)

        #Conversation History to chat back and forth
        conversation_history : list = [] if len(text) <= 1 else conversation_history
        conv_history = True # if len(conversation_history) > 0 else False
        first_ask = True if len(conversation_history) == 0 else False
        print('f-ask', first_ask)

        # Call the Scenario Function and get the response accordingly
        response, conversation_history = Scenarios(text_obj,conversation_history, first_ask=first_ask, conv_history=conv_history)
        
        # handle audio respon
        audio_file = handle_audio(response, new_audio=True)

        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'w') as conversation_history_file:
            json.dump(conversation_history,conversation_history_file)


        # update reponse to self   !!! well we are not using class methods so self doesn't work we just simply need to return response 
        # as functional based prototyping but if you have rest of the code then it will work according to the code
        text[-1].update({'resp': response})
        # text[-1] = response  # for normal response return without class

        return {'text': text, 'audio_file': audio_file}

    self_image = handle_image(text, self_image)
    
    resp = handle_response(text)
    text = resp.get('text')
    audio_file = resp.get('audio_file')


    # print(text)
    print(self_image)
    print(audio_file)
    
    page_direct= None # 'http://localhost:8501/heart'
    listen_after_reply = False
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': page_direct, 'self_image': self_image, 'listen_after_reply': listen_after_reply}


    return JSONResponse(content=json_data)