import streamlit as st
import os
from bs4 import BeautifulSoup
from ozz_auth import all_page_auth_signin
from pages.Characters import hoots_and_hootie
from master_ozz.utils import setup_instance, save_json, refreshAsk_kwargs, ozz_master_root_db, init_user_session_state, return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, ozz_characters, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
import requests
import base64
import ipdb

# from custom_button import cust_Button
load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####


def list_files_by_date(directory):
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            files.append((filepath, os.path.getmtime(filepath)))
    files.sort(key=lambda x: x[1], reverse=True)
    return files

def ozz():

    force_db_root=True
    user_session_state = init_user_session_state()
    authenticator = all_page_auth_signin(force_db_root).get('authenticator')
    
    with st.sidebar:
        st.write(f"force db, {force_db_root}")
            
    client_user = st.session_state['ozz_guest']
    st.write(f"welcome {client_user}")
    
    characters = ozz_characters()
    st.session_state['characters'] = characters
    self_image = st.sidebar.selectbox("Speak To", options=characters.keys(), key='self_image')
    
    if st.sidebar.toggle("sy_prompt"):
        header_prompt = st.text_area("System_Prompt", characters[st.session_state.get('self_image')].get('main_prompt'))
    else:
        header_prompt = characters[st.session_state.get('self_image')].get('main_prompt')
    
    refresh_ask = refreshAsk_kwargs(header_prompt=header_prompt)

    if 'ozz_guest' in st.session_state:
        st.info("Welcome to Divergent Thinkers, you are granted to speak with Stefan, Follow Instructions")
        st.session_state['hh_vars']['self_image'] = 'stefan.png'

    root_db = ozz_master_root_db()
    db_DB_audio = os.path.join(root_db, 'audio')
    audio_files = list_files_by_date(db_DB_audio)

    characters = ['stefan', 'hootsAndHootie']
    
    st.session_state['page_refresh'] = True
    client_user = st.session_state['client_user']
    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')
    
    db_root = st.session_state['db_root']
    session_state_file_path = os.path.join(db_root, 'session_state.json')

    st.session_state['hh_vars']['self_image'] = st.session_state['self_image']

    width=st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    height=st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image=st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else f"{st.session_state.get('self_image')}.png"
    face_recon=st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    show_video=st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    input_text=st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    show_conversation=st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    no_response_time=st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3
    refresh_ask=st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else {}

    tabs = st.tabs(['Talk To Stefan', 'Cool Things I Build'])


    embedding_default = []
    with tabs[0]:
        if self_image == 'stefan.png':
            cols = st.columns((5,3))
            with cols[0]:
                st.header(f"Stefans '''~Conscience'''...")

            embedding_default = ['stefan']
            st.session_state['use_embeddings'] = embedding_default
            save_json(session_state_file_path, user_session_state)

            text="...Well sort of, it's WIP...Responses may be delay'd, ⚡faster-thinking and processing always costs more 💰"
            st.write(text)
        else:
            embedding_default = []
            user_session_state['use_embeddings'] = embedding_default
            save_json(session_state_file_path, user_session_state)

    with st.sidebar:
        embeddings = os.listdir(os.path.join(ozz_master_root(), 'STORAGE'))
        embeddings = ['None'] + embeddings
        use_embeddings = st.multiselect("use embeddings", default=embedding_default, options=embeddings)
        st.session_state['use_embedding'] = use_embeddings
        if st.button("save"):
            user_session_state['use_embeddings'] = use_embeddings
            save_json(session_state_file_path, user_session_state)
            st.info("saved")
    

    # cols = st.columns((5,3))
    # with cols[1]:
    #     user_output = st.empty()
    with st.sidebar:
        # rep_output = st.empty()
        selected_audio_file=st.empty()
        llm_audio=st.empty()
    
    with tabs[0]:
        hoots_and_hootie(
            width=width,
            height=height,
            self_image=self_image,
            face_recon=face_recon,
            show_video=show_video,
            input_text=input_text,
            show_conversation=show_conversation,
            no_response_time=no_response_time,
            refresh_ask=refresh_ask,
            use_embeddings=use_embeddings,
            )

    with tabs[1]:
        pollen = os.path.join(ozz_master_root(), 'pollen')
        fis = ['1', '2', '3']
        st.write("# My Latest Project, A AI Portfolio Manager 🤖")
        for fi in fis:
            if fi == '1':
                msg = "# 1. Setup A Portfolio♛"
            elif fi == '2':
                msg = "# 2. Watch it Make Money🤑"
            elif fi == '3':
                msg = "# 3. Trade alongside and Work Together, Manage your Investments with AI"

            st.write(msg)
            st.image(os.path.join(pollen, f'{fi}.png'))




    with selected_audio_file.container():
        audio_path = st.selectbox("Select Audio File", [os.path.basename(file[0]) for file in audio_files])
    # st.write(master_text_audio[-1])
    # st.write([i for i in st.session_state])
    # st.write(st.session_state['conversation_history.json'])
    response=requests.get(f"{st.session_state['ip_address']}/api/data/{audio_path}")
    with llm_audio.container():
        # st.info(kw)
        st.audio(response.content, format="audio/mp3")  


    with st.expander("3 Ways to chat", True):
        cols = st.columns((3,3))
        with cols[0]:
            st.info("1: RECOMMENDED --> Click And Ask Button: Each time you click you can speak your question")
            st.info("2: Conversational Mode Button: Once you click, use Keyword 'Stefan', ex: 'Stefan How Are you today' (If stefan responds with a question you can directly answer it and don't need to say his name)")
            st.info("3: Chat Form: Type your questions and hit enter")
        with cols[1]:
            st.error("Speach ONLY works on Desktop and does not work on Mobile")
            st.error("Please note: Sometimes questions may be misunderstood and the response may result in inchorent manner.")
            st.error("The LLM that uses RAG (i.e. this one) needs extra context to undestand each new query from user, Having responses tailor more accurately requires more engineering")


    if client_user == 'stefanstapinski@gmail.com':
        with st.sidebar:
            st.write("Admin Only")
            st.write(st.session_state)
if __name__ == '__main__':
    ozz()

