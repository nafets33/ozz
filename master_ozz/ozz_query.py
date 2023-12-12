import json
import os
import openai
from dotenv import load_dotenv
import shutil

from master_ozz.utils import print_line_of_error, ozz_master_root, ozz_master_root_db, generate_audio, save_audio, Retriever, init_constants
import ipdb

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSITS_PATH')

# Loading the json common phrases file and setting up the json file
json_file = open('master_ozz/greetings.json','r')
common_phrases = json.load(json_file)


root_db = ozz_master_root_db()

# Setting up the llm for conversation with conversation history
def llm_assistant_response(message,conversation_history):

    # response = Retriever(message, PERSIST_PATH)
    
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

def copy_and_replace_rename(source_path, destination_directory, build_file_name='temp_audio'):
    try:
        # Extract the file name and extension
        file_name, file_extension = os.path.splitext(os.path.basename(source_path))

        # Construct the new file name (e.g., 'xyz.txt')
        new_file_name = build_file_name + file_extension

        # Construct the full destination path
        destination_path = os.path.join(destination_directory, new_file_name)

        # Copy the file from source to destination
        shutil.copy(source_path, destination_path)
        
        print(f"File copied from {source_path} to {destination_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {source_path}")

    except PermissionError:
        print(f"Error: Permission denied while copying to {destination_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
    # # Example usage
    # source_file = 'path/to/source/file.txt'
    # destination_directory = 'path/to/destination/'

    # copy_and_replace(source_file, os.path.join(destination_directory, os.path.basename(source_file)))

def Scenarios(current_query : str , conversation_history : list , first_ask=False, conv_history=True, session_state={}, audio_file=None):

    def scenario_return(response, conversation_history, audio_file, session_state):
        return {'response': response,
                'conversation_history': conversation_history,
                'audio_file': audio_file,
                'session_state': session_state,}
        
    def handle_prompt(first_ask, conversation_history):
        main_prompt = """
        Your name is Hoots, you are an smart owl that can teach people about almost anything. 
        You specialize in kids development and story telling, you are an educator.
        You love to tell stories and hang out with your favorite owl family, Hootie. She is the greatest Owl is the world.
        Both you know live in Hoot Couture, currently a kids clothing shop, but its growing into so much more, cafe maybe, play space, learning center.
        You can help with whats around the store, help find a great item for any kid, the store has clothes for all seasons, shoes are of highest quality, thats also the stores moto, quality for kids. 
        You love to have a cup of tea, the british way, sit down with anyone who may be around and tell stories.
        """
        if first_ask:
            
            conversation_history.append({"role": "system", "content": main_prompt})

        return conversation_history

    def handle_audio(response, audio_file=None, audio_dir='/Users/stefanstapinski/ENV/ozz/ozz/custom_voiceGPT/frontend/build/'):
        db_DB_audio = os.path.join(root_db, 'audio')
        if audio_file: # if 
            source_file = os.path.join(db_DB_audio, audio_file)
            destination_directory = audio_dir
            copy_and_replace_rename(source_file, os.path.join(destination_directory, os.path.basename(source_file)))

            return audio_file
        else:
            audio_file = 'temp_audio.mp3'
            audio = generate_audio(query=response)

            if audio:
                save_audio(os.path.join(audio_dir, audio_file), audio)
            else:
                audio_file = "techincal_errors.mp3"
                source_file = os.path.join(db_DB_audio, audio_file)
                destination_directory = audio_dir
                copy_and_replace_rename(source_file, os.path.join(destination_directory, os.path.basename(source_file)))

            return audio_file

    def query_func_response(current_query, session_state, returning_question=False):
        try:
            response=None
            audio_file=None
            
            story_asks = ["tell a story", "share a tale", "share a tail", "story please", "tell me a story", "tell the kids a story", "tell the story"]
            story_db = {'calendar_story_1.mp3': ['calendar story'],
                        'owl_story_1.mp3': ['owl story'],}
            
            if returning_question:
                for audio_file, story_tags in story_db.items():
                    find_story = [i for i in story_tags if i in ask]
                    if find_story:
                        response = "story_time"
                        audio_file = audio_file
                        break
                    else:
                        response = "What Story would you like to hear?"
                        session_state['response_type'] = 'question' 
            
            for ask in story_asks:
                if ask in current_query:
                    for audio_file, story_tags in story_db.items():
                        find_story = [i for i in story_tags if i in ask]
                        if find_story:
                            response = "story_time"
                            audio_file = audio_file
                            break
                        else:
                            response = "What Story would you like to hear?"
                            session_state['response_type'] = 'question'
            
            return {'response': response, 'audio_file': audio_file, 'session_state': session_state}
        except Exception as e:
            print_line_of_error(e)
    
    
    # For first we will always check if anything user asked is like common phrases and present in our local json file then give response to that particular query
    conversation_history = handle_prompt(first_ask, conversation_history)

    # Appending the user question from json file
    conversation_history.clear() if not conv_history else conversation_history.append({"role": "user", "content": current_query})

    resp_func = query_func_response(current_query, session_state)
    if resp_func.get('response'):
        response = resp_func.get('response')
        audio_file = resp_func.get('audio_file')
        session_state = resp_func.get('session_state')
        conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
        audio_file = handle_audio(response, audio_file=audio_file)
        return scenario_return(response, conversation_history, audio_file, session_state)

    # Common Phrases
    for query, response in common_phrases.items():
        if query.lower() == current_query.lower():
            print("QUERY already found in db: ", query)

            # Appending the response from json file
            conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
            ## find audio file to set to new_audio False
            audio_file = handle_audio(response, audio_file=audio_file) 
            return scenario_return(response, conversation_history, audio_file, session_state)
    
    # print("calling llm")
    response = llm_assistant_response(current_query,conversation_history)

    conversation_history.clear() if not conv_history else conversation_history.append({"role": "assistant", "content": response})
    audio_file = handle_audio(response=response, audio_file=audio_file)
    return scenario_return(response, conversation_history, audio_file, session_state)

def ozz_query(text, self_image):
    
    def handle_image(text, self_image):
        # based on LLM response handle image if needs to change
        self_image = 'hootsAndHootie.png'

        return self_image
    
    def handle_response(text : str):

        text_obj = text[-1]['user'] # user query
        
        conversation_history_file_path = 'master_ozz/conversation_history.json'
        session_state_path = 'master_ozz/session_state.json'

        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'r') as conversation_history_file:
            conversation_history = json.load(conversation_history_file)
        with open(session_state_path, 'r') as session_state_path_file:
            session_state = json.load(session_state_path_file)

        # Session State    
        session_state = session_state if session_state else {'response_type': 'response', 'returning_question': Faxlse}
        print(session_state)

        #Conversation History to chat back and forth
        conversation_history : list = [] if len(text) <= 1 else conversation_history
        conv_history = True # if len(conversation_history) > 0 else False
        first_ask = True if len(conversation_history) == 0 else False

        # Call the Scenario Function and get the response accordingly
        scenario_resp = Scenarios(text_obj, conversation_history, first_ask, conv_history, session_state)
        response = scenario_resp.get('response')
        conversation_history = scenario_resp.get('conversation_history')
        audio_file = scenario_resp.get('audio_file')
        session_state = scenario_resp.get('session_state')

        if "?" in response:
            session_state['returning_question'] = True
            session_state['response_type'] = 'question'
        else:
            session_state['returning_question'] = False
            session_state['response_type'] = 'response'

        # For saving a chat history for current session in json file
        with open(session_state_path, 'w') as session_state_file:
            json.dump(session_state,session_state_file)
        
        # For saving a chat history for current session in json file
        with open(conversation_history_file_path, 'w') as conversation_history_file:
            json.dump(conversation_history,conversation_history_file)
        
        # update reponse to self   !!! well we are not using class methods so self doesn't work we just simply need to return response 
        # as functional based prototyping but if you have rest of the code then it will work according to the code
        text[-1].update({'resp': response})
        # text[-1] = response  # for normal response return without class

        return {'text': text, 'audio_file': audio_file, 'session_state': session_state}

    self_image = handle_image(text, self_image)
    
    resp = handle_response(text)
    text = resp.get('text')
    audio_file = resp.get('audio_file')
    session_state = resp.get('session_state')

    
    page_direct= None # 'http://localhost:8501/heart'
    listen_after_reply = True if session_state.get('response_type') == 'question' else False
    
    json_data = {'text': text, 'audio_path': audio_file, 'page_direct': page_direct, 'self_image': self_image, 'listen_after_reply': listen_after_reply}

    return json_data

