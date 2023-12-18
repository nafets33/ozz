import streamlit as st
import streamlit_antd_components as sac

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

from elevenlabs import set_api_key
from elevenlabs import Voice, VoiceSettings, generate
from elevenlabs import generate, stream
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


from PIL import Image

from pydub import AudioSegment

from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder

from bs4 import BeautifulSoup
import re
from streamlit_extras.switch_page_button import switch_page


from youtubesearchpython import *

def print_line_of_error(e='print_error_message'):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(e, exc_type, exc_tb.tb_lineno)
    return exc_type, exc_tb.tb_lineno

def ozz_master_root(info='\ozz\ozz'):
    script_path = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(script_path)) # \pollen\pollen

def ozz_master_root_db(info='\ozz\ozz\ozz_db'):
    script_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(os.path.dirname(script_path)), 'ozz_db')

load_dotenv(os.path.join(ozz_master_root(),'.env'))
set_api_key(os.environ.get("api_elevenlabs"))

ROOT_PATH = ozz_master_root()
DATA_PATH = f"{ROOT_PATH}/DATA"
PERSIST_PATH = f"{ROOT_PATH}/STORAGE"
OZZ_DB = ozz_master_root_db()

def init_constants():
    ROOT_PATH = ozz_master_root()
    DATA_PATH = f"{ROOT_PATH}/DATA"
    PERSIST_PATH = f"{ROOT_PATH}/STORAGE"

    return {'DATA_PATH': DATA_PATH,
            'PERSIST_PATH':PERSIST_PATH,}

def text_audio_fields(file_path, text, user_query=None, self_image=None):
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

def init_text_audio_db():
    text_audio_db = os.path.join(OZZ_DB, 'master_text_audio')
    file_path = f'{text_audio_db}.json'
    if os.path.exists(file_path):
        # master_text_audio = ReadPickleData(f'{text_audio_db}.pkl')
        master_text_audio = load_local_json(file_path)
        master_text_audio = {'master_text_audio': master_text_audio}
        return master_text_audio
    
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
    
    save_master_text_db(master_text_audio)

    return master_text_audio


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

def save_master_text_db(master_text_audio):
    text_audio_db = os.path.join(OZZ_DB, 'master_text_audio')
    PickleData(f'{text_audio_db}.pkl', {'master_text_audio': master_text_audio})
    with open(f'{text_audio_db}.json', 'w') as file:
        json.dump(master_text_audio, file)
    
    return True

def save_audio(filename, audio, response, user_query, self_image=False):
    ## all saving should happen at end of response return WORKERBEE

    master_text_audio = init_text_audio_db().get('master_text_audio')
    master_text_audio.append(text_audio_fields(filename, response, user_query, self_image))
    save_master_text_db(master_text_audio)

    # audio_db = os.path.join(OZZ_DB, 'audio')
    # db_file_name = os.path.join(audio_db, filename.split("/")[-1])
    save(
        audio=audio,               # Audio bytes (returned by generate)
        filename=filename               # Filename to save audio to (e.g. "audio.wav")
    )

    local_build_file = 'temp_audio.mp3'
    audio_dir='/Users/stefanstapinski/ENV/ozz/ozz/custom_voiceGPT/frontend/build/'
    save(
        audio=audio,               # Audio bytes (returned by generate)
        filename=os.path.join(audio_dir, local_build_file)               # Filename to save audio to (e.g. "audio.wav")
    )
    return True

def generate_audio(query="Hello Story Time Anyone?", voice='Mimi', use_speaker_boost=True, settings_vars={'stability': .71, 'similarity_boost': .5, 'style': 0.0}):
    try:
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

def return_app_ip(streamlit_ip="http://localhost:8502", ip_address="http://127.0.0.1:8000"):
    # ip_address = get_ip_address()
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
def Retriever(query : str, persist_directory : str, search_kwards_num=3):
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



def sac_menu_buttons(main='Ozz'):
    if main=='Ozz':
        sac_menu_buttons = sac.buttons([
            sac.ButtonsItem(label='Ozz', icon='robot'),
            sac.ButtonsItem(label='Lab', icon='backpack4-fill'),
            # sac.ButtonsItem(label='Ozz', icon='wechat', href=f'{st.session_state["streamlit_ip"]}/ozz'),
            sac.ButtonsItem(label='Client Models', disabled=True),
            sac.ButtonsItem(label='Account', icon='share-fill'),
        ], 
        format_func='title', align='end', type='text')
    elif main == 'Account':
        sac_menu_buttons = sac.buttons([
            sac.ButtonsItem(label='account', icon='key'),
            sac.ButtonsItem(label='Ozz', icon='house'),
            # sac.ButtonsItem(label='Log Out', icon='key'),
        ], format_func='title', align='end', type='text')

    return sac_menu_buttons

def sac_menu_main(sac_menu):
    if sac_menu == 'Lab':
        switch_page('Lab')

    if sac_menu == 'Ozz':
        switch_page('Ozz')


#### CHARACTERS ####
def hoots_and_hootie(width=350, height=350, self_image="hootsAndHootie.png", face_recon=True, show_video=True,input_text=True,show_conversation=True, no_response_time=3):
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()
    # if st.session_state['username'] not in users_allowed_queen_email
    custom_voiceGPT(
        api=f"{st.session_state['ip_address']}/api/data/voiceGPT",
        api_key=os.environ.get('ozz_key'),
        # client_user=client_user,
        self_image=self_image,
        width=width,
        height=height,
        hello_audio="test_audio.mp3",
        face_recon=face_recon,
        show_video=show_video,
        input_text=input_text,
        show_conversation=show_conversation,
        no_response_time=no_response_time,
        commands=[{
            "keywords": ["hey Hoots"], # keywords are case insensitive
            "api_body": {"keyword": "hey hoots"},
        }, {
            "keywords": ["bye Hoots", "bye Foods"],
            "api_body": {"keyword": "bye hoots"},
        }
        ]
    )

    return True