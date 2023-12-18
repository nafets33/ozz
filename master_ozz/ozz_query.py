import json
import os
import openai
from dotenv import load_dotenv
import shutil
import string
import pandas as pd
from datetime import datetime
import pytz
import re


est = pytz.timezone("US/Eastern")

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from master_ozz.utils import init_text_audio_db, print_line_of_error, ozz_master_root, ozz_master_root_db, generate_audio, save_audio, Retriever, init_constants
import ipdb

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')
OZZ_BUILD_dir = constants.get('OZZ_BUILD_dir')
# OZZ_db_audio = constants.get('OZZ_db_audio')
# OZZ_db_images = constants.get('OZZ_db_images')

# Loading the json common phrases file and setting up the json file
json_file = open('master_ozz/greetings.json','r')
common_phrases = json.load(json_file)

root_db = ozz_master_root_db()

# Setting up the llm for conversation with conversation history
def llm_assistant_response(message,conversation_history):

    # response = Retriever(message, PERSIST_PATH)
    s = datetime.now()
    try:
        conversation_history.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            api_key=os.getenv('ozz_api_key')
        )
        assistant_reply = response.choices[0].message["content"]
        print('LLM Call:', (datetime.now() - s).total_seconds())

        return assistant_reply
    except Exception as e:
        print(e)

def copy_and_replace_rename(source_path, destination_directory, build_file_name='temp_audio'):
    try:
        # Extract the file name and extension
        file_name, file_extension = os.path.splitext(os.path.basename(source_path))

        # Construct the new file name (e.g., 'xyz.txt')
        new_file_name = build_file_name + file_extension

        # Construct the full destination path
        destination_path = os.path.join(destination_directory, new_file_name)

        # Copy the file from source to destination, overwriting if it exists
        shutil.copy2(source_path, destination_path)
        
        # print(f"File copied from {source_path} to {destination_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {source_path}")

    except PermissionError:
        print(f"Error: Permission denied while copying to {destination_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def process_response(response):
    # Convert the response to lowercase
    response_lower = response.lower()

    # Remove special characters, including question marks
    response_cleaned = ''.join(char for char in response_lower if char.isalnum() or char.isspace())

    # # Example usage
    # input_response = "What's are you doing?"
    # processed_response = process_response(input_response)
    # print(processed_response)
    return response_cleaned


def calculate_similarity(response1, response2):
    # Create a CountVectorizer to convert responses to vectors
    vectorizer = CountVectorizer().fit_transform([response1, response2])

    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(vectorizer)

    # Extract the cosine similarity score
    similarity_score = similarity_matrix[0, 1]

    # # Example usage
    # response1 = "What are you doing?"
    # response2 = "What are you"

    # similarity_score = calculate_similarity(response1, response2)
    # print(f"Cosine Similarity: {similarity_score}")
    return similarity_score

def return_timestamp_string(format="%Y-%m-%d %H-%M-%S %p {}".format(est), tz=est):
    return datetime.now(tz).strftime(format)

def Scenarios(current_query : str , conversation_history : list , first_ask=False, conv_history=True, session_state={}, audio_file=None, self_image='hootsAndHootie.png'):
    
    def scenario_return(response, conversation_history, audio_file, session_state, self_image=None):
        return {'response': response,
                'conversation_history': conversation_history,
                'audio_file': audio_file,
                'session_state': session_state,
                'self_image': self_image,}
        
    def handle_prompt(first_ask, conversation_history):
        main_prompt = """
        Your name is Hoots, you are an smart owl that can teach people about almost anything. 
        You specialize in kids development and story telling, you are an educator.
        You love to tell stories and hang out with your favorite owl family, Hootie. She is the greatest Owl is the world.
        Both you know live in Hoot Couture, currently a kids clothing shop, but its growing into so much more, cafe maybe, play space, learning center.
        You can help with whats around the store, help find a great item for any kid, the store has clothes for all seasons, shoes are of highest quality, thats also the stores moto, quality for kids. 
        You love to have a cup of tea, the british way, sit down with anyone who may be around and tell stories. Please always tell short stories for little kids.
        """
        if first_ask:
            
            conversation_history.append({"role": "system", "content": main_prompt})

        return conversation_history

    def find_audio(response, master_text_audio, audio_file = False):
        # if response in audio db or 95% in audio db, return audio file
        s = datetime.now()

        df = pd.DataFrame(master_text_audio)
        audio_text = dict(zip(df['file_path'], df['text'])) # audio, text
        if master_text_audio:
            # response = process_response(response)
            for db_audio_file, ozz_reponse in audio_text.items():
                # ozz_reponse = process_response(ozz_reponse)
                if calculate_similarity(response, ozz_reponse) > .95:
                    # print("audio found")
                    return db_audio_file
        print('findaudio:', (datetime.now() - s).total_seconds())

        return audio_file

    def handle_audio(user_query, response, audio_file=None, self_image=None):
        s = datetime.now()
        
        master_text_audio = init_text_audio_db().get('master_text_audio')
        df = pd.DataFrame(master_text_audio)
        audio_text = dict(zip(df['file_path'], df['text'])) # audio, text
        fnames = len(audio_text)
        db_DB_audio = os.path.join(root_db, 'audio')
        
        # check is response already in audio db per character WORKERBEE
        if not audio_file:
            audio_file = find_audio(response, master_text_audio)

        if audio_file: # if
            print("AUDIO FOUND ", audio_file)
            source_file = os.path.join(db_DB_audio, audio_file)
            destination_directory = OZZ_BUILD_dir
            copy_and_replace_rename(source_file, destination_directory)

            return audio_file
        else:
            ## NEW AUDIO
            fname_image = self_image.split('.')[0]
            filename = f'{fname_image}__{fnames}.mp3'
            audio_file = filename #os.path.join(db_DB_audio, filename)
            print("NEW AUDIO", audio_file)
            audio = generate_audio(query=response)

            if audio:
                save_audio(filename, audio, response, user_query, self_image)
            else:
                audio_file = "techincal_errors.mp3"
                source_file = os.path.join(db_DB_audio, audio_file)
                destination_directory = OZZ_BUILD_dir
                copy_and_replace_rename(source_file, destination_directory)

        print('audiofunc:', (datetime.now() - s).total_seconds())

        return audio_file

    def query_func_response(current_query, session_state, returning_question=False):
        try:
            s = datetime.now()
            response=None
            audio_file=None
            
            story_asks = ["tell a story", "share a tale", "share a tail", "story please", "tell me a story", "tell the kids a story", "tell the story"]
            story_db = {'calendar_story_1.mp3': ['calendar story'],
                        'owl_story_1.mp3': ['owl story'],}
            tell_phrases = ['tell me', 'tell the', 'please tell']
            for k, v in story_db.items():
                for tag in v:
                    for tell_phrase in tell_phrases:
                        sa = f'{tell_phrase} {tag}' 
                        story_asks.append(sa)
            
            if returning_question:
                for audio_file, story_tags in story_db.items():
                    find_story = [i for i in story_tags if i in ask]
                    if find_story:
                        response = "story_time"
                        audio_file = audio_file
                    #     break
                    # else:
                    #     print("Could not Find Story")
                    #     response = "What Story would you like to hear?"
                    #     session_state['response_type'] = 'question' 
            
            # ipdb.set_trace()
            story_ask = [ask for ask in story_asks if ask in current_query]
            print(story_ask)
            for ask in story_asks:
                if ask in current_query:
                    print("ask in query ", ask)
                    story_ask = [ask]

            if story_ask:
                ask = story_ask[0]
                for audio_file, story_tags in story_db.items():
                    find_story = [i for i in story_tags if i in ask]
                    if find_story:
                        print("STORY FOUND")
                        response = "story_time"
                        audio_file = audio_file
                        break
                    else:
                        print("Could not Find Story")
                        response = "What Story would you like to hear?"
                        session_state['response_type'] = 'question'
                        audio_file = None
            # ipdb.set_trace()
            print('queryfunc:', (datetime.now() - s).total_seconds())
            return {'response': response, 'audio_file': audio_file, 'session_state': session_state}
        except Exception as e:
            print_line_of_error(e)
            return None
    
    
    print('query ', current_query)
    print('sstate ', session_state)
    user_query = current_query
    # For first we will always check if anything user asked is like common phrases and present in our local json file then give response to that particular query
    conversation_history = handle_prompt(first_ask, conversation_history)

    # Appending the user question from json file
    conversation_history.clear() if not conv_history else conversation_history.append({"role": "user", "content": current_query})

    ### WATER FALL RESPONSE ###
    resp_func = query_func_response(current_query, session_state)
    if resp_func.get('response'):
        print("func response found")
        response = resp_func.get('response')
        audio_file = resp_func.get('audio_file')
        session_state = resp_func.get('session_state')
        conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
        audio_file = handle_audio(user_query, response, audio_file=audio_file, self_image=self_image)
        return scenario_return(response, conversation_history, audio_file, session_state, self_image)

    # Common Phrases # WORKERBEE Add check against audio_text DB
    print("common phrases")
    s = datetime.now()
    for query, response in common_phrases.items():
        if query.lower() == current_query.lower():
            print("QUERY already found in db: ", query)

            # Appending the response from json file
            conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
            ## find audio file to set to new_audio False
            # return audio file
            audio_file = handle_audio(user_query, response, audio_file=audio_file, self_image=self_image) 
            print('common phrases:', (datetime.now() - s).total_seconds())

            return scenario_return(response, conversation_history, audio_file, session_state, self_image)
    
    # LLM
    print("LLM")
    # are we asking LLM to find answer in db or reteriver?
    def determine_embedding(current_query):
        s = datetime.now()
        print("EMBEDDINGS")

        db_name={}
        our_embeddings_phrases = ['where is', 'looking for', 'hoot couture', 'hoot couture kids', 'hootcouturekids', 'hoots store', 'something about the store', 'in the store', 'clothes do you have', 'do you have']
        question_conv_sayings = ['what', 'what about', 'tell me about', 'tell me', 'tell us something about the store']
        for phrase in our_embeddings_phrases:
            if phrase in current_query:
                print("EMBEDDING FOUND")
                our_embeddings = True
                db_name = 'db1'
                break
        # for cs in question_conv_sayings:
        #     for phrase in our_embeddings_phrases:
        #         our_embeddings_phrases.append(f'{cs} {phrase}')
        
        # for em_phrases in our_embeddings_phrases:
        #     if em_phrases in current_query:
        #         print("EMBEDDING FOUND")
        #         our_embeddings = True
        #         db_name = 'db1'
        #         break
        print('detemine embedding:', (datetime.now() - s).total_seconds())

        print("embedding", db_name)
        return {'db_name': db_name}

    use_our_embeddings = determine_embedding(current_query)
    if use_our_embeddings.get('db_name'):
        db_name = use_our_embeddings.get('db_name')
        print("USE EMBEDDINGS: ", db_name)
        Retriever_db = os.path.join(PERSIST_PATH, db_name)
        response = Retriever(current_query, Retriever_db).get('result')
    else:
        print("CALL LLM")
        response = llm_assistant_response(current_query, conversation_history)

    conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
    audio_file = handle_audio(user_query, response=response, audio_file=audio_file, self_image=self_image)
    return scenario_return(response, conversation_history, audio_file, session_state, self_image)


def remove_exact_string(string_a, string_b):
    # Split string_a by string_b
    split_strings = string_a.split(string_b)
    
    # Join the split strings without the occurrences of string_b
    final_string_a = ''.join(split_strings)

    return final_string_a

def ozz_query(text, self_image):
    
    def ozz_query_json_return(text, self_image, audio_file, page_direct, listen_after_reply=False):
        json_data = {'text': text, 
                    'audio_path': audio_file, 
                    'self_image': self_image, 
                    'page_direct': page_direct, 
                    'listen_after_reply': listen_after_reply}
        return json_data
    
    def clean_current_query_from_previous_ai_response(text):
        last_text = text[-1]
        current_query = text[-1]['user'] # user query
        # take previous ai response and remove if it found in current_query
        if 'assistant' in last_text:
            ai_last_resp = text[-1]['assistant']
        else:
            ai_last_resp = None
        
        if ai_last_resp:
            current_query = remove_exact_string(string_a=current_query, string_b=ai_last_resp)

        # WORKERBEE confirm is senitentment of phrase is outside bounds of responding to

        return text, current_query

    def handle_response(text : str, self_image : str):

        text, current_query = clean_current_query_from_previous_ai_response(text)

        if len(current_query) == 0:
            return ozz_query_json_return(text, self_image, audio_file=None, page_direct=None, listen_after_reply=False)

        conversation_history_file_path = 'master_ozz/conversation_history.json'
        session_state_path = 'master_ozz/session_state.json'

        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'r') as conversation_history_file:
            conversation_history = json.load(conversation_history_file)
        with open(session_state_path, 'r') as session_state_path_file:
            session_state = json.load(session_state_path_file)

        # Session State    
        session_state = session_state if session_state else {'response_type': 'response', 'returning_question': False}
        print(session_state)

        #Conversation History to chat back and forth
        conversation_history = [] if len(text) == 0 else conversation_history
        conv_history = True # if len(conversation_history) > 0 else False
        first_ask = True if len(conversation_history) == 0 else False
        print("CONV HIST", conversation_history)
        # Call the Scenario Function and get the response accordingly
        scenario_resp = Scenarios(current_query, conversation_history, first_ask, conv_history, session_state, self_image=self_image)
        response = scenario_resp.get('response')
        conversation_history = scenario_resp.get('conversation_history')
        audio_file = scenario_resp.get('audio_file')
        session_state = scenario_resp.get('session_state')
        self_image = scenario_resp.get('self_image')

        print("handle")
        print(response)
        print(audio_file)
        print(self_image)
        
        text[-1].update({'resp': response})

        audio_file='temp_audio.mp3'
        
        #
        #  if "?" in response:
        #     session_state['returning_question'] = True
        #     session_state['response_type'] = 'question'
        # else:
        #     session_state['returning_question'] = False
        #     session_state['response_type'] = 'response'
        
        session_state['returning_question'] = False
        session_state['response_type'] = 'response'
        session_state['text'] = text

        # For saving a chat history for current session in json file
        with open(session_state_path, 'w') as session_state_file:
            json.dump(session_state,session_state_file)
        
        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'w') as conversation_history_file:
            json.dump(conversation_history,conversation_history_file)
        

        return {'text': text, 'audio_file': audio_file, 'session_state': session_state, 'self_image': self_image}
    
    resp = handle_response(text, self_image)
    text = resp.get('text')
    audio_file = resp.get('audio_file')
    session_state = resp.get('session_state')
    self_image = resp.get('self_image')

    print("handle2")
    # print(response)
    print(audio_file)
    print(self_image)
    
    page_direct= False # if redirect, add redirect page into session_state
    listen_after_reply = False # True if session_state.get('response_type') == 'question' else False

    return ozz_query_json_return(text, self_image, audio_file, page_direct, listen_after_reply)

## db 

## def save_interaction(client_user, what_said, date, ai_respone, ai_image) # fact table

## def embedd_the_day()

## short term memory vs long term memory