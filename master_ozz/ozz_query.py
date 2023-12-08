import json
import os
import openai
from dotenv import load_dotenv
from master_ozz.utils import ozz_master_root, generate_audio, save_audio
# Loading environment variables
main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

# Loading the json common phrases file and setting up the json file
json_file = open('master_ozz/greetings.json','r')
common_phrases = json.load(json_file)

# Setting up the llm for conversation with conversation history
def llm_assistant_response(message,conversation_history):
    try:
        conversation_history.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            api_key=os.getenv('ozz_api_key')
        )
        assistant_reply = response.choices[0].message["content"]
        return assistant_reply
    except Exception as e:
        print(e)

# call_llm=True # goal is to set it to False and figure action/response using local phrases as required
# Now we are only using llm when we don't have response to the query in greetings.json
def Scenarios(current_query : str , conversation_history : list , first_ask=False, conv_history=True):
    # For first we will always check if anything user asked is like common phrases and present in our local json file then give response to that particular query
    if first_ask:
        ''' Appending the prompt for system when user asks for first time (is this first ask?) 
        also with json coz if user again tries to ask something and doesn't found in json then it will go to llm
        so llm needs to be already have the json conversation to understand the next query asked by user '''
        
        conversation_history.append({"role": "system", "content": "You are a cute and smart assistant for kids."})

    # Appending the user question from json file
    conversation_history.clear() if not conv_history else conversation_history.append({"role": "user", "content": current_query})
    
    for query, response in common_phrases.items():
        if query.lower() == current_query.lower():
            print("query already found in db: ", query)
            # Appending the response from json file
            conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
            return response, conversation_history
    
    ############## This code needs to run when the response is not present in the predefined json data ################
    # Appending the user question
    # conversation_history.clear() if not conv_history else conversation_history.append({"role": "user", "content": current_query})
    print("calling llm")
    assistant_response = llm_assistant_response(current_query,conversation_history)
    # assistant_response = 'thanks from llm'
    # Appending the response by llm
    conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": assistant_response})
    return assistant_response, conversation_history


def ozz_query(text):
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
    # print(self_image)
    # print(audio_file)
    
    page_direct= None # 'http://localhost:8501/heart'
    listen_after_reply = False
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': page_direct, 'self_image': self_image, 'listen_after_reply': listen_after_reply}

    return json_data

# Testing the functions    
# conversation_history = []
# print(Scenarios('hello buddy',conversation_history))
# print(conversation_history)