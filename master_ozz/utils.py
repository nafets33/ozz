import streamlit as st
import speech_recognition as sr
import time 
from dotenv import load_dotenv
import os
from elevenlabs import set_api_key
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import generate, stream
from elevenlabs import save
import pickle
import psycopg2
from PIL import Image

import asyncio
import os
import pickle
import sqlite3
import sys
import time
from datetime import datetime
import streamlit as st
import hashlib
import shutil
import pandas as pd
import aiohttp
import pytz
import socket
import ipdb


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import  UnstructuredMarkdownLoader, UnstructuredWordDocumentLoader, PyPDFLoader, PythonLoader, CSVLoader, TextLoader, UnstructuredHTMLLoader, UnstructuredExcelLoader
import os


from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv
import os
import openai


from youtubesearchpython import *
import streamlit as st
import os

def ozz_master_root(info='\ozz\ozz'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

load_dotenv(os.path.join(ozz_master_root(),'.env'))
set_api_key(os.environ.get("api_elevenlabs"))


def init_constants():
    ROOT_PATH = ozz_master_root()
    DATA_PATH = f"{ROOT_PATH}/DATA"
    PERSIST_PATH = f"{ROOT_PATH}/STORAGE"

    return {'DATA_PATH': DATA_PATH,
            'PERSIST_PATH':PERSIST_PATH,}

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


def search_youtube():
    channelsSearch = ChannelsSearch('NoCopyrightSounds', limit = 10, region = 'US')

    print(channelsSearch.result())

    video = Video.get('https://www.youtube.com/watch?v=z0GKGpObgPY', mode = ResultMode.json, get_upload_date=True)
    print(video)
    videoInfo = Video.getInfo('https://youtu.be/z0GKGpObgPY', mode = ResultMode.json)
    print(videoInfo)
    videoFormats = Video.getFormats('z0GKGpObgPY')
    print(videoFormats)



    channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
    playlist = Playlist(playlist_from_channel_id(channel_id))

    print(f'Videos Retrieved: {len(playlist.videos)}')

    while playlist.hasMoreVideos:
        print('Getting more videos...')
        playlist.getNextVideos()
        print(f'Videos Retrieved: {len(playlist.videos)}')

    print('Found all the videos.')


def base_content():
    def content_type(name, url, tags):
        return {name, url, tags}

    main_return = {
        'youtube': [content_type(name='sleeping beatuy', url='https://www.youtube.com/watch?v=-DHqDPVezRc', tags={}),
                    content_type(name='snow white', url='https://www.youtube.com/watch?v=W8EXJ8Gqf0c', tags={})
                    ]
    }

    return main_return


def save_audio(filename, audio):
    save(
        audio=audio,               # Audio bytes (returned by generate)
        filename=filename               # Filename to save audio to (e.g. "audio.wav")
    )

def generate_audio(query="Hello Story Time Anyone?", voice='Mimi', use_speaker_boost=True, settings_vars={'stability': .71, 'similarity_boost': .5, 'style': 0.0}):
    # 'Mimi', #'Charlotte', 'Fin'
    audio = generate(
        text=query,
        voice=voice, #'Charlotte', 'Fin'
    )

    # audio = generate(
    #     text="Hello! My name is Bella.",
    #     voice=Voice(
    #         voice_id='EXAVITQu4vr4xnSDxMaL',
    #         settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
    #     )
    # )

    return audio

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
            page_title="QuantQueen",
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
            return
        raise e

    # {
    #   "hi":"Yes! How may i help you today :)",
    #   "hello":"Yes! How may i help you today :)",
    #   "hey":"Yup! Tell me",
    #   "helloo":"Yes! How may i help you today :)",
    #   "hellooo":"Yes! How may i help you today :)",
    #   "g morining":"Good Morning to you to",
    #   "gmorning":"Good Morning to you to",
    #   "good morning":"Good Morning to you to",
    #   "morning":"Good Morning to you to",
    #   "good day":"Have a nice day to you to",
    #   "good afternoon":"Good afternoon",
    #   "good evening":"Good afternoon",
    #   "greetings":"Hello what's up",
    #   "greeting":"Hello what's up",
    #   "good to see you":"You can't see me :P",
    #   "its good seeing you":"You can't see me :P",
    #   "how are you":"I'm fine. what bout you",
    #   "how're you":"good",
    #   "how are you doing":"nothing just responding to you",
    #   "how ya doin'":"pulling out in my rs6",
    #   "how ya doin":"pulling out in my rs6 with kerosene",
    #   "how is everything":"going fine",
    #   "how is everything going":"it's good going",
    #   "how's everything going":"it's good",
    #   "how is you":"not bad",
    #   "how's you":"not bad",
    #   "how are things":"not bad they are good",
    #   "how're things":"not bad they are good",
    #   "how is it going":"not bad",
    #   "how's it going":"not bad",
    #   "how's it goin'":"not bad",
    #   "how's it goin":"not bad",
    #   "how is life been treating you":"good than i thought",
    #   "how's life been treating you":"good than i thought",
    #   "how have you been":"good than i thought",
    #   "how've you been":"good than i thought",
    #   "what is up":"good than i thought",
    #   "what's up":"good than i thought",
    #   "what is cracking":"nothing just doing my jobs",
    #   "what's cracking":"nothing just doing my jobs",
    #   "what is good":"good is good",
    #   "what's good":"good is good",
    #   "what is happening":"nothing special",
    #   "what's happening":"nothing special",
    #   "what is new":"nothing special",
    #   "what's new":"nothing special",
    #   "what is neww":"nothing special",
    #   "g’day":"to you to",
    #   "howdy":"rowdy :p"
    # }

def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def return_app_ip(streamlit_ip="http://localhost:8502"):
    ip_address = get_ip_address()
    if ip_address == os.environ.get('gcp_ip'):
        # print("IP", ip_address, os.environ.get('gcp_ip'))
        ip_address = "https://api.quantqueen.com"
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
    

# Function to load all the files and append them into a single documents
def Directory(directory : str):
    documents = []
    for file_path in os.listdir(directory):
        file_path = os.path.join(directory, file_path)
        document = LoadMultipleFiles(file_path)
        documents.append(document)
    return documents


#Function to create chunks of documents
def CreateChunks(documents : str):
    chunks = []
    for docs in documents:
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=6000,
        chunk_overlap=100,
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
def Retriever(query : str, persist_directory : str):
    embeddings = OpenAIEmbeddings()
    # memory = ConversationBufferMemory()
    # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = FAISS.load_local(persist_directory,embeddings=embeddings)
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 3})

    # For OpenAI ChatGPT Model
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model='gpt-3.5-turbo-16k',max_tokens=10000), chain_type='stuff', retriever=retriever, return_source_documents=True)

    result = qa_chain({"query": query})
    return result


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



# # Connect to the PostgreSQL database
# conn = psycopg2.connect(
#     dbname="ozz_db",
#     user="stefanstapinski",
#     password="ozz",
#     host="localhost",
#     port=5432,
# )

# # Open the audio file
# with open("your_audio_file.mp3", "rb") as audio_file:
#     audio_data = audio_file.read()

# # Insert the audio data into the database
# cursor = conn.cursor()
# cursor.execute("INSERT INTO audio_files (audio_data) VALUES (%s)", (audio_data,))
# conn.commit()

# # Close the cursor and connection
# cursor.close()
# conn.close()


# # Database connection parameters
# db_params = {
#     "host": "localhost",
#     "database": "ozz_db",
#     "user": "stefanstapinski",
#     "password": "ozz",
#     "port": 5432
# }

# # SQL statement to create the audio files table
# create_table_sql = """
# CREATE TABLE audio_files (
#     id serial PRIMARY KEY,
#     title varchar(100),
#     audio_data bytea
# );
# """

# try:
#     # Connect to the database
#     conn = psycopg2.connect(**db_params)

#     # Create a cursor object
#     cursor = conn.cursor()

#     # Execute the SQL statement to create the table
#     cursor.execute(create_table_sql)

#     # Commit the changes
#     conn.commit()

#     # Close the cursor and connection
#     cursor.close()
#     conn.close()

#     print("Table 'audio_files' created successfully.")

# except psycopg2.Error as e:
#     print("Error creating table:", e)