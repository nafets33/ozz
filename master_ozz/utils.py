import streamlit as st

import speech_recognition as sr
import time 
from dotenv import load_dotenv
import os
import pickle
import time
from datetime import datetime
import streamlit as st
import pandas as pd
import socket
import ipdb
import sys
import json
import random
import requests 
from PIL import Image

from elevenlabs import set_api_key
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import save

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import  UnstructuredMarkdownLoader, UnstructuredWordDocumentLoader, PyPDFLoader, PythonLoader, CSVLoader, TextLoader, UnstructuredHTMLLoader, UnstructuredExcelLoader
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from langchain.prompts import PromptTemplate
import openai


from pydub import AudioSegment

from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder

from bs4 import BeautifulSoup
import re
from streamlit_extras.switch_page_button import switch_page
import hashlib

import boto3
from botocore.exceptions import NoCredentialsError

# import replicate ### ??????
import replicate as rp


# from youtubesearchpython import *
#### AUTH UTILS #####

def hash_string(string):
    # Hash the string
    hashed_string = hashlib.sha256(string.encode()).hexdigest()
    # Convert the hash to an integer ID
    id = int(hashed_string, 16) % (10 ** 8)
    return id

def return_db_root(client_username):
    def client_dbs_root():
        client_dbs = os.path.join(ozz_master_root(), "client_user_dbs")
        return client_dbs
    client_user_pqid = hash_string(client_username)
    client_user = client_username.split("@")[0]
    db_name = f'db__{client_user}_{client_user_pqid}'
    db_root = os.path.join(client_dbs_root(), db_name)

    return db_root

def init_clientUser_dbroot(client_username, force_db_root=False, queenKING=False):

    if force_db_root:
        db_root = os.path.join(ozz_master_root(), "ozz_db/sneakpeak")
    # elif client_username in ['stefanstapinski@gmail.com']:  ## admin
    #     db_root = os.path.join(hive_master_root(), "db")
    else:
        db_root = return_db_root(client_username=client_username)
        if os.path.exists(db_root) == False:
            os.mkdir(db_root)
            os.mkdir(os.path.join(db_root, "logs"))
    
    if queenKING:
        st.session_state['db_root'] = db_root
        st.session_state["admin"] = True if client_username == "stefanstapinski@gmail.com" else False

    return db_root

def init_pollen_dbs(db_root, prod, queens_chess_pieces=['queen_king.json'], queenKING=False, init=True, db_return={}):
    # db_return = {f'{queens_chess_piece}': f'{queens_chess_piece}'}
    for queens_chess_piece in queens_chess_pieces:
        # WORKERBEE don't check if file exists, only check on init
        if prod:
            PB_QUEEN_Pickle = os.path.join(db_root, f'{queens_chess_piece}')
        else:
            # print("My Queen Sandbox")
            PB_QUEEN_Pickle = os.path.join(db_root, f'sandbox_{queens_chess_piece}')
        if init:
            if os.path.exists(PB_QUEEN_Pickle) == False:
                print(f"Init {PB_QUEEN_Pickle}")
                if queens_chess_piece == 'session_state.json': # master_conv_history, conv_history
                    save_json(PB_QUEEN_Pickle, {})
                elif queens_chess_piece == 'master_conv_history.json': # master_conv_history
                    True
                elif queens_chess_piece == 'conv_history.json': # master_conv_history
                    True
                else:
                    save_json(PB_QUEEN_Pickle, [])

        if queenKING:
            st.session_state[queens_chess_piece] = PB_QUEEN_Pickle
        
        db_return[queens_chess_piece] = queens_chess_piece


    return db_return

def live_sandbox__setup_switch(pq_env, switch_env=False):

    try:
        prod = pq_env.get('env')

        prod_name = (
            "LIVE"
            if prod
            else "Sandbox"
        )
        
        st.session_state["prod_name"] = prod_name
        st.session_state["production"] = prod

        if switch_env:
            if prod:
                prod = False
                st.session_state["production"] = prod
                prod_name = "Sanbox"
                st.session_state["prod_name"] = prod_name
            else:
                prod = True
                st.session_state["production"] = prod
                prod_name = "LIVE"
                st.session_state["prod_name"] = prod_name
            # save
            pq_env.update({'env': prod})
            PickleData(pq_env.get('source'), pq_env)

        return prod
    except Exception as e:
        print_line_of_error("live sb switch")

def setup_instance(client_username, switch_env, force_db_root, queenKING, prod=None, init=False):
    client_dbs = os.path.join(ozz_master_root(), "client_user_dbs")
    if os.path.exists(client_dbs) == False:
        print("INIT CLIENT DB")
        os.mkdir(client_dbs)

    queens_chess_pieces=['conversation_history.json', 'session_state.json', 'master_conversation_history.json']
    try:
        db_root = init_clientUser_dbroot(client_username=client_username, force_db_root=force_db_root, queenKING=queenKING)  # main_root = os.getcwd() // # db_root = os.path.join(main_root, 'db')
        if prod is not None:
            init_pollen_dbs(db_root, prod, queens_chess_pieces, queenKING, init)
            return prod
        else:
            # Ensure Environment
            PB_env_PICKLE = os.path.join(db_root, f'{"queen_king"}{"_env"}.pkl')
            if os.path.exists(PB_env_PICKLE) == False:
                PickleData(PB_env_PICKLE, {'source': PB_env_PICKLE,'env': False})
            
            pq_env = ReadPickleData(PB_env_PICKLE)
            prod = live_sandbox__setup_switch(pq_env, switch_env)
            
            init_pollen_dbs(db_root, prod, queens_chess_pieces, queenKING, init)
            
            st.session_state['prod'] = prod
            st.session_state['client_user'] = client_username
            return prod
    except Exception as e:
        print_line_of_error(f"setup instance {e}")

def kingdom():
    allowed_emails=['stefanstapinski@gmail.com']
    return allowed_emails

def init_user_session_state():
    ss_file  = os.path.join(st.session_state['db_root'], 'session_state.json')
    ss_data = load_local_json(ss_file)
    for k,v in ss_data.items():
        st.session_state[k] = v
    
    return True

#### AUTH UTILS #####

# search_google_images, define when to set true and when it does it will display the images in slider form auto flipping each image every 3 seconds until user clicks and then it will stop slider from moving


def ozz_master_root(info='\ozz\ozz'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

def ozz_master_root_db(info='\ozz\ozz\ozz_db'):
    script_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(os.path.dirname(script_path)), 'ozz_db')


def init_constants():
    ROOT_PATH = ozz_master_root()
    OZZ_DB = ozz_master_root_db()
    DATA_PATH = f"{ROOT_PATH}/DATA"
    PERSIST_PATH = f"{ROOT_PATH}/STORAGE"
    OZZ_BUILD_dir = f"{ROOT_PATH}/custom_voiceGPT/frontend/build"
    OZZ_db_audio = f"{OZZ_DB}/audio"
    OZZ_db_images = f"{OZZ_DB}/images"

    return {'DATA_PATH': DATA_PATH,
            'PERSIST_PATH':PERSIST_PATH,
            'OZZ_BUILD_dir': OZZ_BUILD_dir,
            "OZZ_db_audio": OZZ_db_audio,
            "OZZ_db_images": OZZ_db_images}

ROOT_PATH = ozz_master_root()
OZZ_DB = ozz_master_root_db()

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')
OZZ_BUILD_dir = constants.get('OZZ_BUILD_dir')
OZZ_db_audio = constants.get('OZZ_db_audio')
OZZ_db_images = constants.get('OZZ_db_images')


load_dotenv(os.path.join(ozz_master_root(),'.env'))
set_api_key(os.environ.get("api_elevenlabs"))


def text_audio_fields(file_path, text, user_query=None, self_image=None, s3_filepath=None):
    if not self_image:
        self_image = file_path.split("/")[-1].split(".")[0] # name of file without extension

    return {'file_path': file_path, 
            'text': text, 
            'self_image': self_image,
            'datetime': datetime.now().strftime("%B %d, %Y %H:%M"),
            'user_query': user_query,
            's3_filepath': s3_filepath,}

def text_image_fields(file_path, text, user_query=None, self_image=None):
    if not self_image:
        self_image = file_path.split("/")[-1].split(".")[0] # name of file without extension

    return {'file_path': file_path, 
            'text': text, 
            'self_image': self_image,
            'datetime': datetime.now().strftime("%B %d, %Y %H:%M"),
            'user_query': user_query}

def load_local_json(file_path):
    with open(file_path, 'r') as filee:
        data = json.load(filee)
        
    return data

def save_json(db_name, data):
    if db_name:
        with open(db_name, 'w') as file:
            json.dump(data, file)

def init_text_audio_db(db_name='master_text_audio.json'):
    master_text_audio_file_path = os.path.join(OZZ_DB, db_name)
    if os.path.exists(master_text_audio_file_path):
        master_text_audio = load_local_json(master_text_audio_file_path)
        return db_name, master_text_audio
    
    print("INIT DB")
    audio_db = os.path.join(OZZ_DB, 'audio')
    master_text_audio = []
    for audio in os.listdir(audio_db):
        try:
            audio_source = os.path.join(audio_db, audio)
            text = transcribe_audio_mp3(audio_source)
            input_save = text_audio_fields(audio_source, text)
            master_text_audio.append(input_save)
        except Exception as e:
            print_line_of_error(e)
    
    save_json(master_text_audio_file_path, master_text_audio)

    return db_name, master_text_audio


def init_text_image_db(db_name='master_text_image.json'):
    file_path = os.path.join(OZZ_DB, db_name)
    if os.path.exists(file_path):
        master_text_image = load_local_json(file_path)
        return master_text_image
    else:
        master_text_image = {'source': file_path, 'data': []}

    return master_text_image

def ReadPickleData(pickle_file):
    # Check the file's size and modification time
    prev_size = os.stat(pickle_file).st_size
    prev_mtime = os.stat(pickle_file).st_mtime
    stop = 0
    e = None
    while True:
        # Get the current size and modification time of the file
        curr_size = os.stat(pickle_file).st_size
        curr_mtime = os.stat(pickle_file).st_mtime

        # Check if the size or modification time has changed
        if curr_size != prev_size or curr_mtime != prev_mtime:
            pass
            # print(f"{pickle_file} is currently being written to")
            # logging.info(f'{pickle_file} is currently being written to')
        else:
            try:
                with open(pickle_file, "rb") as f:
                    pf = pickle.load(f)
                    pf['source'] = pickle_file
                    return pf
            except Exception as e:
                print('pkl read error: ', os.path.basename(pickle_file), e, stop)
                # logging.error(f'{e} error is pickle load')
                if stop > 3:
                    print("CRITICAL read pickle failed ", e)
                    # logging.critical(f'{e} error is pickle load')
                    # send_email(subject='CRITICAL Read Pickle Break')
                    return ''
                stop += 1
                time.sleep(0.033)

        # Update the previous size and modification time
        prev_size = curr_size
        prev_mtime = curr_mtime

        # Wait a short amount of time before checking again
        time.sleep(0.033)


def PickleData(pickle_file, data_to_store):
    if pickle_file:
        if len(data_to_store) > 0:
            with open(pickle_file, "wb+") as dbfile:
                pickle.dump(data_to_store, dbfile)
        else:
            return False
    else:
        return False

    return True


def print_line_of_error(e='print_error_message'):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(e, exc_type, exc_tb.tb_lineno)
    return exc_type, exc_tb.tb_lineno


def transcribe_audio_mp3(audio_file_path):
    recognizer = sr.Recognizer()

    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_file_path)

    # Convert audio to a compatible format (16-bit PCM WAV)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # Export the audio to a temporary WAV file
    temp_wav_file = "temp.wav"
    audio.export(temp_wav_file, format="wav")

    with sr.AudioFile(temp_wav_file) as source:
        audio_data = recognizer.record(source)

    # Transcribe the audio
    try:
        transcribed_text = recognizer.recognize_google(audio_data)
        return transcribed_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")

    return None


def append_audio(input_file1, input_file2, output_file):
    # Load audio segments
    audio_segment1 = AudioSegment.from_file(input_file1)
    audio_segment2 = AudioSegment.from_file(input_file2)

    # Concatenate audio segments
    final_audio = audio_segment1 + audio_segment2

    # Export the concatenated audio to a file
    final_audio.export(output_file, format="mp4")  #


def base_content():
    def content_type(name, url, tags):
        return {name, url, tags}

    main_return = {
        'youtube': [content_type(name='sleeping beatuy', url='https://www.youtube.com/watch?v=-DHqDPVezRc', tags={}),
                    content_type(name='snow white', url='https://www.youtube.com/watch?v=W8EXJ8Gqf0c', tags={})
                    ]
    }

    return main_return


def save_audio(filename, audio, response, user_query, self_image=False, db_name='master_text_audio.json', s3_filepath=None):
    try:
        ## all saving should happen at end of response return WORKERBEE
        master_text_audio_file_path = os.path.join(OZZ_DB, db_name)
        master_text_audio_file_path, master_text_audio = init_text_audio_db()
        master_text_audio.append(text_audio_fields(filename, response, user_query, self_image, s3_filepath))
        save_json(master_text_audio_file_path, master_text_audio)

        local_path = filename=os.path.join(OZZ_db_audio, filename) 
        save(
            audio=audio,               # Audio bytes (returned by generate)
            filename=local_path                # Filename to save audio to (e.g. "audio.wav")
        )
        
        #upload to s3 bucket
        print("FIX Master DB FIRST before s3 upload")
        # upload_to_s3(local_file=local_path, bucket='ozzz', s3_file=s3_filepath)

        # del file?

        return local_path
    except Exception as e:
        print_line_of_error(e)
        return False

def generate_audio(query="Hello Story Time Anyone?", voice='Mimi', use_speaker_boost=True, settings_vars={'stability': .71, 'similarity_boost': .5, 'style': 0.0}, model_id='eleven_monolingual_v1'):
    try:
        # 'eleven_monolingual_v1' # eleven_multilingual_v2, eleven_turbo_v2
        # 'Mimi', #'Charlotte', 'Fin'
        audio = generate(
            model=model_id,
            text=query,
            voice=voice,
            # voice=Voice(
            # voice_id='zrHiDhphv9ZnVXBqCLjz', # mimi
            # settings=VoiceSettings(stability=0.8, similarity_boost=0.7, style=0.0, use_speaker_boost=True)
            # ),
        )

        return audio
    except Exception as e:
        print_line_of_error(e)
        return None

def conversational_phrases(your_name, Hobby, Interest, Location, City, Place):

    conversational_phrases = {
        # Group 1: Greetings
        {"greeting_1": "Hello"},
        {"greeting_2": "Hi there"},
        {"greeting_3": "Hey"},
        {"greeting_4": "Good morning"},
        {"greeting_5": "Good afternoon"},
        {"greeting_6": "Good evening"},
        {"greeting_7": "How's it going?"},
        {"greeting_8": "Hey, what's up?"},
        {"greeting_9": "Yo!"},
        {"greeting_10": "Greetings"},

        # Group 2: Farewells
        {"farewell_1": "Goodbye"},
        {"farewell_2": "See you later"},
        {"farewell_3": "Take care"},
        {"farewell_4": "Farewell"},
        {"farewell_5": "Until next time"},
        {"farewell_6": "Catch you later"},
        {"farewell_7": "Have a great day!"},
        {"farewell_8": "Bye for now"},
        {"farewell_9": "Adios"},
        {"farewell_10": "So long"},

        # Group 3: Thanks
        {"thanks_1": "Thank you"},
        {"thanks_2": "Thanks a lot"},
        {"thanks_3": "I appreciate it"},
        {"thanks_4": "You're a lifesaver"},
        {"thanks_5": "Much obliged"},
        {"thanks_6": "I owe you one"},
        {"thanks_7": "Thanks a million"},
        {"thanks_8": "You rock"},
        {"thanks_9": "Gracias"},
        {"thanks_10": "I'm grateful"},

        # Group 4: Apologies
        {"apology_1": "I'm sorry"},
        {"apology_2": "My apologies"},
        {"apology_3": "I didn't mean that"},
        {"apology_4": "Forgive me"},
        {"apology_5": "I messed up"},
        {"apology_6": "It's my fault"},
        {"apology_7": "Please accept my apology"},
        {"apology_8": "I'm in the wrong"},
        {"apology_9": "I feel bad about it"},
        {"apology_10": "I regret that"},

        # Group 5: Introduction
        {"introduction_1": "My name is f'{your_name}'"},
        {"introduction_2": "I'm f'{your_name}'"},
        {"introduction_3": "Nice to meet you, I'm f'{your_name}'"},
        {"introduction_4": "Allow me to introduce myself, I'm f'{your_name}'"},
        {"introduction_5": "I go by f'{your_name}'"},
        {"introduction_6": "Hi, I'm f'{your_name}'"},
        {"introduction_7": "Pleased to make your acquaintance, I'm f'{your_name}'"},
        {"introduction_8": "Call me f'{your_name}'"},
        {"introduction_9": "I'm f'{your_name}', and I'm here to assist you"},
        {"introduction_10": "Greetings, I'm f'{your_name}'"},

        # Group 6: Interests
        {"interests_1": "I like f'{Hobby}'"},
        {"interests_2": "I'm interested in f'{Topic}'"},
        {"interests_3": "One of my hobbies is f'{Hobby}'"},
        {"interests_4": "I have a passion for f'{Interest}'"},
        {"interests_5": "In my free time, I enjoy f'{Hobby}'"},
        {"interests_6": "I'm a fan of f'{Interest}'"},
        {"interests_7": "I love to f'{Hobby}'"},
        {"interests_8": "One of my favorite things to do is f'{Hobby}'"},
        {"interests_9": "I'm into f'{Interest}'"},
        {"interests_10": "I'm a f'{Hobby}' enthusiast"},

        # Group 7: Location
        {"location_1": "I'm from f'{Location}"},
        {"location_2": "I live in f'{City}'"},
        {"location_3": "I'm based in f'{Place}'"},
        {"location_4": "My hometown is f'{Location}"},
        {"location_5": "I call f'{City}' my home"},
        {"location_6": "I reside in f'{Place}'"},
        {"location_7": "You can find me in f'{Location}"},
        {"location_8": "I'm currently in f'{City}'"},
        {"location_9": "I'm a native of f'{Location}"},
        {"location_10": "I'm located in f'{Place}'"},
    }

    charcters = ['mimi', 'fin']
    main_root = ozz_master_root()
    charcter_dirs = os.listdir(os.path.join(main_root, 'utils/character_db'))
    for charcter in charcters:
        for k_ey, convo in conversational_phrases.items():
            if charcter not in charcter_dirs:
                os.mkdir(charcter)
            
            filename = os.path.join(charcter, f'{charcter}{k_ey}.wav')

            audio = generate(
            text=convo,
            stream=False,
            voice= 'Fin', #'Charlotte', 'Fin'
            )
            save(
                audio=audio,               # Audio bytes (returned by generate)
                filename=filename               # Filename to save audio to (e.g. "audio.wav")
            )


def set_streamlit_page_config_once():
    try:
        main_root = ozz_master_root()

        jpg_root = os.path.join(main_root, "misc")
        queenbee = os.path.join(jpg_root, "woots_jumps_once.gif")
        page_icon = Image.open(queenbee)
        st.set_page_config(
            page_title="Ozz",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state='collapsed',
            #  menu_items={
            #      'Get Help': 'https://www.extremelycoolapp.com/help',
            #      'Report a bug': "https://www.extremelycoolapp.com/bug",
            #      'About': "# This is a header. This is an *extremely* cool app!"
            #  }
        )            
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            # ignore this error
            return True
        raise e



def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def return_app_ip(streamlit_ip="http://localhost:8501", ip_address=None):
    
    ip_address = st.session_state.get('ip_address')
    
    if ip_address:
        return ip_address, streamlit_ip
    else:
        ip_address = get_ip_address()
    
    if ip_address == os.environ.get('gcp_ip'):
        # print("IP", ip_address, os.environ.get('gcp_ip'))
        ip_address = "https://api.divergent-thinkers.com"
        streamlit_ip = ip_address
    else:
        ip_address = "http://127.0.0.1:8000"

    st.session_state['ip_address'] = ip_address
    st.session_state['streamlit_ip'] = streamlit_ip

    return ip_address, streamlit_ip


def LoadMultipleFiles(files):
    extension = files.split(".")[-1]
    if extension == 'pdf':
        data = PyPDFLoader(files)
        pages = data.load()
        return pages
    elif extension == 'csv':
        data = CSVLoader(files)
        pages = data.load()
        return pages
    elif extension == 'md':
        data = UnstructuredMarkdownLoader(files)
        pages = data.load()
        return pages
    elif extension == 'docx' or extension == 'doc':
        data = UnstructuredWordDocumentLoader(files)
        pages = data.load()
        return pages
    elif extension == 'html':
        data = UnstructuredHTMLLoader(files)
        pages = data.load()
        return pages
    elif extension == 'xlsx' or extension == 'xls':
        data = UnstructuredExcelLoader(files)
        pages = data.load()
        return pages
    elif extension == 'py':
        data = PythonLoader(files)
        pages = data.load()
        return pages
    elif extension == 'txt':
        data = TextLoader(files)
        pages = data.load()
        return pages
    else:
        return None
    

# Function to load all the files and append them into a single documents
def Directory(directory : str):
    documents = []
    for file_path in os.listdir(directory):
        file_path = os.path.join(directory, file_path)
        document = LoadMultipleFiles(file_path)
        if document:
            documents.append(document)
        else:
            print("ERROR: ", file_path)
    return documents


#Function to create chunks of documents
def CreateChunks(documents : str):
    chunks = []
    for docs in documents:
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
        )
        chunk = text_splitter.split_documents(docs)
        chunks.extend(chunk)
    return chunks


# Function to create embeddings
def CreateEmbeddings(textChunks :str ,persist_directory : str):
    # Check if persist directory exists otherwise create it
    if not os.path.exists(persist_directory):
            os.mkdir(persist_directory)
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = FAISS.from_documents(documents=textChunks, embedding=embeddings)
    vector_store.save_local(persist_directory)
    return vector_store



# Function to fetch the answers from FAISS vector db 
def Retriever(query : str, persist_directory : str, search_kwards_num=4):
    try:
        s = datetime.now()

        embeddings = OpenAIEmbeddings()
        # memory = ConversationBufferMemory()
        # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectordb = FAISS.load_local(persist_directory,embeddings=embeddings)
        retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": search_kwards_num})

        # For OpenAI ChatGPT Model
        qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model='gpt-3.5-turbo-16k',max_tokens=10000), chain_type='stuff', retriever=retriever, return_source_documents=True)

        result = qa_chain({"query": query})

        print('retervier:', (datetime.now() - s).total_seconds())

        return result
    except Exception as e:
        print_line_of_error(e)


def MergeIndexes(db_locations : list, new_location : str = None):
    embeddings = OpenAIEmbeddings()
    """taking first database for merging all the databases
        so that we can return a single database after merging"""
    

    dbPrimary = FAISS.load_local(db_locations[0],embeddings=embeddings)
    for db_location in db_locations:
        if db_location == db_locations[0]:
            # if again we got first database then we skip it as we already have marked it as primary
            continue
        dbSecondary = FAISS.load_local(db_location,embeddings=embeddings)
        dbPrimary.merge_from(dbSecondary)

    # Return the merged database or we can store it as new db name as well 
    # dbPrimary.save_local(new_location)  Location where we have to save the merged database  
    return dbPrimary.docstore._dict


def sign_in_client_user():
    if 'client_user' not in st.session_state:
        st.info("Enter email to continue")
        with st.form("Your Name, use Email"):
            enter_name = st.text_input('email')
            if st.form_submit_button('save'):
                st.session_state['client_user'] = enter_name
                st.rerun()
        return False
    else:
        return True



# TRAINING FUNCTIONS #

def is_html(data):
    # Use BeautifulSoup to check if the data is HTML
    try:
        soup = BeautifulSoup(data, 'html.parser')
        return soup.html is not None
    except:
        return False

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text()
    return text_content

def clean_text(text):
    # Remove non-alphanumeric characters and extra whitespaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = re.sub(' +', ' ', cleaned_text)  # Remove extra whitespaces
    return cleaned_text

def clean_data(data):
    if is_html(data):
        # If it's HTML, clean the HTML content first
        cleaned_text = clean_html(data)
        # Then, clean the text
        cleaned_text = clean_text(cleaned_text)
        return cleaned_text
    else:
        # If it's not HTML, just clean the text
        return clean_text(data)



def generate_image(text="2 cute owls in a forest, Award-Winning Art, Detailed, Photorealistic, Fanart", size="256x256", save_img=True, use_llm_enhance=True, gen_source='replicate'): 
    
    if gen_source == 'replicate':
        # import replicate as rp
        REPLICATE_API_TOKEN = os.environ.get('replicate_key')
        replicate = rp.Client(api_token=REPLICATE_API_TOKEN)
        prompt = generate_image_prompt(text)

        rr = replicate.run(
        "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        input={
            "width": 768,
            "height": 768,
            "prompt": prompt,
            "scheduler": "K_EULER",
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
        )

        # rr = replicate.run(
        # "playgroundai/playground-v2-1024px-aesthetic:42fe626e41cc811eaf02c94b892774839268ce1994ea778eba97103fe1ef51b8",
        # input={
        #     "width": 1024,
        #     "height": 1024,
        #     "prompt": prompt,
        #     "scheduler": "K_EULER_ANCESTRAL",
        #     "guidance_scale": 3,
        #     "apply_watermark": False,
        #     "negative_prompt": "",
        #     "num_inference_steps": 50
        # }
        # )

        # update to save as gif !!! create gifs from existing images
        # rr = replicate.run(
        # "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
        # input={
        #     "cond_aug": 0.02,
        #     "decoding_t": 7,
        #     "input_image": "https://replicate.delivery/pbxt/JvLi9smWKKDfQpylBYosqQRfPKZPntuAziesp0VuPjidq61n/rocket.png",
        #     "video_length": "14_frames_with_svd",
        #     "sizing_strategy": "maintain_aspect_ratio",
        #     "motion_bucket_id": 127,
        #     "frames_per_second": 6
        # }
        # )


        image_urls = rr
    else:
        openai.api_key=os.getenv("OPENAI_API_KEY")
        prompt = generate_image_prompt(text)

        res = openai.Image.create( 
            # text describing the generated image 
            prompt=prompt, 
            # number of images to generate  
            n=3, 
            # size of each generated image 
            size=size, 
        ) 
        # returning the URL of one image as  
        # we are generating only one image 
        
        image_urls = [img["url"] for img in res["data"]]
       
    db_name = 'master_text_image.json'
    MT_Image_path = os.path.join(OZZ_DB, db_name)
    MT_Image = init_text_image_db(db_name)

    # Save data for each image in the database
    image_responses = {}
    for i, url in enumerate(image_urls):
        response, file_path = save_image(url, gen_source)
        image_responses[file_path] = response
        data = text_image_fields(file_path=file_path, text=prompt)
        MT_Image.append(data)
    
    save_json(MT_Image_path, MT_Image)

    return image_responses


def save_image(url1, gen_source='dalle'):
    response = requests.get(url1) 
    # saving the image in PNG format
    images_len = len(os.listdir(OZZ_db_images))
    fname = f'{gen_source}_{images_len}.png'
    filepath = os.path.join(OZZ_db_images, fname)
    with open(filepath, "wb") as f: 
        f.write(response.content) 

    return response, fname


def generate_image_prompt(query="2 owls sleeping", enhancements=[]):
    # Default prompt
    prompt = f"Create an image of {query}."

    # Enhancement categories with real artist-inspired attributes
    enhancement_categories = {
        'realism': [
            "Emulate the meticulous realism of Chuck Close.",
            "Capture the lifelike details seen in the works of Audrey Flack.",
            "Achieve a photographic level of realism reminiscent of Roberto Bernardi."
        ],
        'impressionism': [
            "Infuse the scene with the enchanting brushstrokes characteristic of Claude Monet.",
            "Evoke the light and color techniques used by Camille Pissarro.",
            "Channel the dreamlike essence of Edgar Degas' impressionistic style."
        ],
        'surrealism': [
            "Explore the fantastical realms of Salvador Dalí through surrealistic elements.",
            "Incorporate dreamlike and bizarre elements inspired by René Magritte.",
            "Create a whimsical narrative akin to the surreal worlds crafted by Yves Tanguy."
        ],
        'abstract': [
            "Embrace non-representational forms reminiscent of Wassily Kandinsky's abstract works.",
            "Explore geometric abstraction inspired by Kazimir Malevich.",
            "Capture the essence of abstract expressionism seen in Joan Mitchell's paintings."
        ],
        'colorful': [
            "Infuse the composition with vibrant colors similar to the palettes of Wassily Kandinsky.",
            "Create a bold and colorful composition inspired by Sonia Delaunay.",
            "Explore the use of intense hues reminiscent of Fauvist master André Derain."
        ],
        'monochrome': [
            "Convey a powerful visual impact through a monochromatic palette, inspired by Franz Kline.",
            "Explore the emotional depth of black and white compositions, akin to Anselm Kiefer's works.",
            "Create a dramatic atmosphere using grayscale tones, influenced by the photography of Ansel Adams."
        ],
        'vintage': [
            "Evoke the nostalgia of vintage photography with sepia tones inspired by Dora Maar.",
            "Create a retro atmosphere inspired by the vintage aesthetics of Edward Hopper.",
            "Infuse the composition with a timeless quality reminiscent of the works of Norman Rockwell."
        ],
        'futuristic': [
            "Explore a futuristic cityscape inspired by the visionary architecture of Zaha Hadid.",
            "Capture the sleek and modern aesthetic seen in the works of Santiago Calatrava.",
            "Incorporate cutting-edge technology and design elements inspired by Syd Mead."
        ],
        'minimalism': [
            "Embrace simplicity and clean lines in the style of Donald Judd's minimalistic sculptures.",
            "Explore the use of negative space and simplicity inspired by Agnes Martin.",
            "Create a visually serene composition reminiscent of the minimalistic works of Yayoi Kusama."
        ],
        'expressionism': [
            "Infuse the composition with emotional intensity reminiscent of Egon Schiele's expressionistic portraits.",
            "Capture the bold and expressive brushstrokes inspired by Ernst Ludwig Kirchner.",
            "Explore the raw and emotive qualities of expressionism seen in the works of Chaim Soutine."
        ]
    }

    # Apply enhancements
    if enhancements:
        for category in enhancements:
            if category in enhancement_categories:
                prompt += f" {random.choice(enhancement_categories[category])},"
    # print(prompt)
    return prompt.rstrip(',') + "."

    # # Example usage:
    # query = "a cityscape"
    # enhancements = ['futuristic', 'realism', 'impressionism']

    # prompt = generate_image_prompt(query, enhancements)
    # print(prompt)



def upload_to_s3(local_file, bucket, s3_file):
    """
    Upload a file to an S3 bucket.

    :param local_file: Path to the local file you want to upload
    :param bucket: S3 bucket name
    :param s3_file: S3 key (path) where the file will be stored
    :return: True if the file was uploaded successfully, False otherwise
    """
    try:
        # Create an S3 client
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('s3_access_key'),
                          aws_secret_access_key=os.environ.get('s3_secret'))

        # Upload the file
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

        # # Example usage
        # audio_file_path = 'your_audio_file_path.mp3'
        # bucket_name = 'ozzz'
        # s3_key = 'audios/filename.mp3'

        # upload_to_s3(audio_file_path, bucket_name, s3_key)


def hoots_and_hootie_keywords():
    return ["hey Hoots", "hey Hoot", "hey Hootie", 'morning Hoots', 'morning Hootie']


def hoots_and_hootie_vars(width=350, height=350, self_image="hootsAndHootie.png", face_recon=False, show_video=False, input_text=True, show_conversation=True, no_response_time=3, refresh_ask=True):
    return {'width':width,
     'height':height,
     'self_image':self_image, 
     'face_recon':face_recon,
     'show_video':show_video,
     'input_text':input_text,
     'show_conversation':show_conversation,
     'no_response_time':no_response_time,
     'refresh_ask':refresh_ask}


def init_stories():

    stories = {
        "1. Adventure in Candyland": "Embark on a sweet journey through a magical land made of candy!",
        "2. Talking Animal Friends": "Join kids as they befriend animals who can talk and share amazing stories.",
        "3. Treasure Hunt in Pirate Cove": "Set sail for a thrilling adventure to find hidden pirate treasures!",
        "4. Rainbow Kingdom Quest": "Explore a vibrant kingdom filled with rainbow magic and exciting surprises.",
        "5. Dinosaur Time Travel": "Travel back in time with kids and meet friendly dinosaurs in a prehistoric world.",
        "6. Magic School Days": "Attend a school where kids learn incredible spells and charms for magical fun.",
        "7. Friendly Alien Encounter": "Make friends with a kind extraterrestrial visitor and embark on space adventures!",
        "8. Quest for the Missing Teddy": "Join kids on a mission to find their lost teddy bear in a charming adventure.",
        "9. Enchanted Forest Expedition": "Discover the wonders of an enchanted forest, meeting magical creatures along the way.",
        "10. Superhero Training Camp": "Kids attend a camp to develop superpowers and become pint-sized superheroes.",
        "11. Winter Wonderland Quest": "Explore a snowy wonderland filled with ice castles, snowmen, and winter magic.",
        "12. Panda Pajama Party": "Join a group of playful pandas for a pajama party full of giggles and games.",
        "13. Space Adventure Squad": "Become part of a space crew on a mission to explore distant planets and make new friends.",
        "14. Mermaid Lagoon Discovery": "Dive into an underwater world to meet friendly mermaids and sea creatures.",
        "15. Robot Friends in Robo-City": "Kids build robot friends and embark on exciting adventures in a futuristic city.",
        "16. Dragon Egg Quest": "Embark on a quest to find and hatch a magical dragon egg, leading to mythical adventures.",
        "17. Jungle Safari Expedition": "Join an adventurous safari through the jungle, encountering wild animals and hidden treasures.",
        "18. Circus Spectacular": "Step into the magical world of a circus with acrobats, clowns, and daring feats.",
        "19. Detective Puppies Mystery": "A group of adorable detective puppies solves mysteries and cracks cases.",
        "20. Teddy Bear Tea Party": "Host a delightful tea party with teddy bears, complete with tea, treats, and tales.",
        "21. Rainbow Unicorn Parade": "Witness a spectacular parade of rainbow-colored unicorns spreading joy and magic.",
        "22. Pumpkin Patch Harvest": "Visit a magical pumpkin patch where pumpkins come to life, ready for a harvest celebration.",
        "23. Time-Traveling Playground": "Kids discover a playground that takes them to different time periods for fun adventures.",
        "24. Cupcake Decorating Extravaganza": "Join a baking competition where kids decorate cupcakes in a whimsical world of sweets.",
        "25. Moonlight Fairy Dance": "Dance under the moonlight with friendly fairies, creating a magical and enchanting evening.",
        "26. Galactic Ice Cream Adventure": "Embark on a space journey to collect special ingredients for the ultimate galactic ice cream.",
        "27. Teddy Bear Hospital": "Kids become doctors for a day, taking care of teddy bears and other stuffed animals.",
        "28. Jungle Gym Olympics": "Compete in a friendly jungle gym competition with twists, turns, and laughter.",
        "29. Pirate Pizza Party": "Sail the high seas in search of the perfect pizza recipe for a swashbuckling pizza party.",
        "30. Underwater Ballet Extravaganza": "Dive into an underwater world where sea creatures put on a mesmerizing ballet performance.",
        "31. Circus Animal Talent Show": "Animals from the circus showcase their unique talents in a dazzling talent show.",
        "32. Teddy Bear Picnic Parade": "Join a parade of teddy bears as they march through the forest to a delightful picnic spot.",
        "33. Penguin Winter Games": "Compete in winter games with adorable penguins, featuring ice-skating and snowball fights.",
        "34. Enchanted Tea Garden": "Discover a magical tea garden where tea leaves come to life, telling stories and secrets.",
        "35. Rainbow Kite Festival": "Soar through the sky with colorful kites in a joyful and uplifting kite festival.",
        "36. Dragonfly Express Adventure": "Hop aboard the Dragonfly Express for a whimsical journey through fantasy landscapes.",
        "37. Bubblegum Bubble Bonanza": "Join a bubblegum-blowing contest with fantastic bubbles and playful challenges.",
        "38. Teddy Bear Space Odyssey": "Teddy bears embark on a space odyssey to explore new planets and make cosmic friends.",
        "39. Candy Cane Forest Expedition": "Venture into a forest made of candy canes, meeting sweet creatures along the way.",
        "40. Panda Puzzle Party": "Solve puzzles and challenges with a group of clever pandas in a bamboo-filled paradise.",
        "41. Magic Carpet Ride": "Embark on a magical journey on flying carpets, visiting enchanted lands and meeting magical beings.",
        "42. Marshmallow Castle Quest": "Kids set out on a quest to build a castle made entirely of marshmallows.",
        "43. Arctic Penguin Parade": "Join a parade of penguins in the Arctic, showcasing their unique talents and dance moves.",
        "44. Teddy Bear Spa Day": "Pamper teddy bears with a spa day, featuring bubble baths, massages, and relaxation.",
        "45. Starry Night Stargazing": "Gaze at the stars on a starry night, uncovering constellations and mythical stories.",
        "46. Pancake Pancake Party": "Host a pancake party with a twist, where pancakes come to life with personalities.",
        "47. Mooncake Festival Adventure": "Celebrate the Mooncake Festival with an adventure filled with lanterns and mooncakes.",
        "48. Robot Toy Parade": "Join a parade of lively robot toys, marching through the city in a joyful celebration.",
        "49. Teddy Bear Train Adventure": "Hop aboard the Teddy Bear Train for a scenic journey through teddy bear landscapes.",
        "50. Lullaby Lighthouse": "Visit a magical lighthouse where lullabies are created, soothing all who hear them.",
        "51. Teddy Bear Talent Show": "Teddy bears showcase their unique talents in a charming and entertaining talent show.",
        "52. Bubble Bath Beach Day": "Enjoy a day at the bubble bath beach, where waves are made of bubbles and laughter.",
        "53. Rainbow Slide Spectacle": "Slide down a rainbow slide in a whimsical playground filled with surprises.",
        "54. Teddy Bear Birthday Bash": "Celebrate a teddy bear's birthday with a grand party featuring games and surprises.",
        "55. Dragonfly Ballet Recital": "Watch dragonflies perform a delightful ballet recital in a magical garden setting.",
        "56. Penguin Pizza Party": "Host a pizza party with penguins, complete with snowball fights and sledding.",
        "57. Jellybean Jungle Safari": "Embark on a safari through a jungle where trees are made of jellybeans and lollipops.",
        "58. Teddy Bear Train Picnic": "Pack a picnic and board the Teddy Bear Train for a scenic journey through nature.",
        "59. Bubblegum Bubble Ballet": "Dance along with bubblegum bubbles in a whimsical ballet performance.",
        "60. Snowflake Symphony": "Listen to a symphony of snowflakes as they create magical music in a winter wonderland.",
        "61. Pancake Pillow Fort": "Build a pillow fort with pancakes, creating a cozy and delicious play space.",
        "62. Magic Lantern Moonlit Adventure": "Embark on a moonlit adventure with magical lanterns guiding the way.",
        "63. Teddy Bear Tea Time": "Host a tea party with teddy bears, complete with tiny cups and delightful treats.",
        "64. Cupcake Castle Quest": "Embark on a quest to build a castle made entirely of cupcakes, filled with surprises.",
        "65. Penguin Playground Parade": "Join a parade of penguins in a playful procession through a snowy playground.",
        "66. Rainbow Popsicle Party": "Celebrate with a popsicle party featuring a rainbow of flavors and frozen fun.",
        "67. Teddy Bear Space Carnival": "Teddy bears create a space carnival with rides, games, and cosmic treats.",
        "68. Butterfly Ballet Recital": "Watch butterflies perform a graceful ballet recital in a blooming flower garden.",
        "69. Ice Cream Island Adventure": "Explore an island made of ice cream, discovering delicious flavors and sweet surprises.",
        "70. Penguin Pirate Party": "Join penguins for a pirate-themed party with treasure hunts and ship adventures.",
        "71. Gumball Garden Gathering": "Visit a garden where gumballs grow on trees, creating a colorful and tasty landscape.",
        "72. Teddy Bear Treetop Tea Party": "Host a treetop tea party with teddy bears, surrounded by branches and laughter.",
        "73. Rainbow Roller Coaster Ride": "Experience the thrill of a roller coaster ride on a rainbow-colored track.",
        "74. Penguin Playground Picnic": "Enjoy a picnic with penguins in a snowy playground, filled with snowy fun.",
        "75. Marshmallow Mountain Expedition": "Embark on a mountain expedition where mountains are made of fluffy marshmallows.",
        "76. Teddy Bear Treasure Hunt": "Go on a treasure hunt with teddy bears, solving puzzles and finding hidden treasures.",
        "77. Bubblegum Bubble Bath Day": "Celebrate a day of bubblegum bubble baths, making bath time extra bubbly and fun.",
        "78. Penguin Painting Party": "Join penguins for a painting party, creating colorful masterpieces on snowy canvases.",
        "79. Jellybean Jungle Gym Adventure": "Navigate through a jungle gym made of jellybeans, swinging and sliding with joy.",
        "80. Teddy Bear Toyland Parade": "Participate in a parade through Toyland with teddy bears and playful toys.",
        "81. Rainbow Robot Rodeo": "Join a robot rodeo with robots performing tricks and stunts in a rainbow-filled arena.",
        "82. Penguin Pillow Fight": "Engage in a friendly pillow fight with penguins, creating fluffy chaos and laughter.",
        "83. Gumball Galaxy Adventure": "Embark on a space adventure in a galaxy filled with gumballs and cosmic wonders.",
        "84. Teddy Bear Train Adventure": "Embark on a train adventure with teddy bears, traveling through magical landscapes.",
        "85. Cotton Candy Cloud Castle": "Build a castle in the clouds made of cotton candy, creating a sugary and dreamy world.",
        "86. Penguin Pizza Paradise": "Visit a paradise where pizza grows on trees, creating a delicious and cheesy landscape.",
        "87. Cupcake Carousel Celebration": "Celebrate on a cupcake carousel, twirling with delightful flavors and sweet decorations.",
        "88. Teddy Bear Treehouse Tea Time": "Host a tea party in a treehouse with teddy bears, enjoying tea and treetop views.",
        "89. Rainbow Rocket Launch": "Experience the excitement of a rocket launch in a colorful and vibrant rainbow sky.",
        "90. Penguin Playground Pancake Party": "Host a pancake party with penguins in a snowy playground, flipping pancakes with glee.",
        "91. Marshmallow Moonwalk": "Take a moonwalk on marshmallow clouds, bouncing and floating in a sweet and fluffy space.",
        "92. Teddy Bear Tug-of-War Tournament": "Participate in a tug-of-war tournament with teddy bears, showcasing strength and teamwork.",
        "93. Bubblegum Bubble Beehive": "Explore a beehive made of bubblegum bubbles, meeting friendly bees and buzzing with joy.",
        "94. Penguin Painted Playground": "Join penguins in a playground painted with colorful patterns and lively designs.",
        "95. Jellybean Jumping Jamboree": "Engage in a jumping jamboree on a trampoline made of jellybeans, bouncing with delight.",
        "96. Teddy Bear Talent Showcase": "Showcase talents in a grand talent show with teddy bears, featuring acts of all kinds.",
        "97. Rainbow Roller Skating Rink": "Skate in a roller rink with rainbow-colored tracks, gliding and twirling with joy.",
        "98. Penguin Parade Party": "Celebrate with a parade of penguins, marching through the snow with festive music and dance.",
        "99. Gumball Garden Gala": "Attend a garden gala where gumballs bloom in vibrant colors, creating a festive and sweet atmosphere.",
        "100. Teddy Bear Tea Tower": "Build a tower of tea cups with teddy" 
    }

    return stories



# Host
# ec2-3-230-24-12.compute-1.amazonaws.com
# Database
# dcp3airkvcc1u1
# User
# jdudpjkxggkbrv
# Port
# 5432
# Password
# c9db217ba584b1a549f9b35536fb52b6416b7c387e9cc3c49fab82614efb167f
# URI
# postgres://jdudpjkxggkbrv:c9db217ba584b1a549f9b35536fb52b6416b7c387e9cc3c49fab82614efb167f@ec2-3-230-24-12.compute-1.amazonaws.com:5432/dcp3airkvcc1u1
# Heroku CLI
# heroku pg:psql postgresql-cubic-10426 --app ozz


# def autoplay_audio(file_path: str):
#     with open(file_path, "rb") as f:
#         data = f.read()
#         b64 = base64.b64encode(data).decode()
#         md = f"""
#             <audio controls autoplay="true">
#             <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#             </audio>
#             """
#         st.markdown(
#             md,
#             unsafe_allow_html=True,
#         )


# st.write("# Auto-playing Audio!")

# autoplay_audio("local_audio.mp3")

# def llm_response(query, chat_history):
#     memory = ConversationBufferMemory(
#                                         memory_key="chat_history",
#                                         max_len=50,
#                                         return_messages=True,
#                                     )

#     prompt_template = '''
#     You are a Bioinformatics expert with immense knowledge and experience in the field. Your name is Dr. Fanni.
#     Answer my questions based on your knowledge and our older conversation. Do not make up answers.
#     If you do not know the answer to a question, just say "I don't know".

#     Given the following conversation and a follow up question, answer the question.

#     {chat_history}

#     question: {question}
#     '''

#     PROMPT = PromptTemplate.from_template(
#                 template=prompt_template
#             )


#     chain = ConversationalRetrievalChain.from_llm(
#                                                     chat_model,
#                                                     retriever,
#                                                     memory=memory,
#                                                     condense_question_prompt=PROMPT
#                                                 )

#     pp.pprint(chain({'question': q1, 'chat_history': memory.chat_memory.messages}))