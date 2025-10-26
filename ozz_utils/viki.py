import streamlit as st
import os
from bs4 import BeautifulSoup
from ozz_auth import all_page_auth_signin
from pages.Characters import hoots_and_hootie
from master_ozz.utils import get_last_eight, load_local_json, refreshAsk_kwargs, ozz_master_root_db, init_user_session_state, return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, ozz_characters, CreateEmbeddings, Retriever, init_constants
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
    # ccc=os.path.join(st.session_state['db_root'], 'conversation_history.json')
    # conv = load_local_json(ccc)
    # conv = [conv[0]]
    characters = ozz_characters()
    st.session_state['characters'] = characters
    self_image = 'viki'  #st.sidebar.selectbox("Speak To", options=characters.keys(), key='self_image')
    st.session_state['self_image'] = self_image

    if st.sidebar.toggle("sy_prompt"):
        header_prompt = st.text_area("System_Prompt", characters[self_image].get('main_prompt'))
    else:
        header_prompt = characters[st.session_state.get('self_image')].get('main_prompt')
    
    refresh_ask = refreshAsk_kwargs(header_prompt=header_prompt)

    root_db = ozz_master_root_db()

    st.session_state['page_refresh'] = True
    constants = init_constants()

    db_root = st.session_state['db_root']
    session_state_file_path = os.path.join(db_root, 'session_state.json')

    # st.session_state['hh_vars']['self_image'] = st.session_state['self_image']

    # width=st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    # height=st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image= st.session_state['self_image'] # st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else f"{st.session_state.get('self_image')}.png"
    # face_recon=False #st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    # show_video=st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    # input_text=st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    # show_conversation=st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    # no_response_time=st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 4
    # refresh_ask=st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else {}

    show_video = st.toggle("Chat Only", False, help="Turn OFF Voice")
    hoots_and_hootie(
        # width=width,
        # height=height,
        self_image=self_image,
        # face_recon=face_recon,
        show_video=show_video,
        # input_text=input_text,
        # show_conversation=show_conversation,
        # no_response_time=no_response_time,
        refresh_ask=refresh_ask,
        use_embeddings=False,
        )


    root_db = ozz_master_root_db()
    db_DB_audio = os.path.join(root_db, 'audio')
    audio_files = list_files_by_date(db_DB_audio)
    selected_audio_file=st.empty()
    llm_audio=st.empty()

    with selected_audio_file.container():
        audio_path = st.selectbox("Select Audio File", [os.path.basename(file[0]) for file in audio_files])
    # st.write(master_text_audio[-1])
    # st.write([i for i in st.session_state])
    # st.write(st.session_state['conversation_history.json'])
    response=requests.get(f"{st.session_state['ip_address']}/api/data/{audio_path}")
    with llm_audio.container():
        # st.info(kw)
        st.audio(response.content, format="audio/mp3")  

if __name__ == '__main__':
    force_db_root=True
    authenticator = all_page_auth_signin(force_db_root).get('authenticator')
    ozz()

