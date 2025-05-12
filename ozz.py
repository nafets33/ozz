import streamlit as st
import os
# from bs4 import BeautifulSoup
# import re
from dotenv import load_dotenv
from ozz_auth import all_page_auth_signin
from master_ozz.utils import (ozz_characters, load_local_json, init_user_session_state, setup_instance, 
                              return_app_ip, init_text_audio_db, 
                              ozz_master_root, sign_in_client_user, 
                              print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, 
                              init_constants, check_fastapi_status, run_pq_fastapi_server
)
# from master_ozz.ozz_query import ozz_query
from pages.Characters import ozz
from pages.Lab import lab
from pages.YouTube import youtube
# import speech_recognition as sr
# import requests
import streamlit_antd_components as sac
# import base64
# import ipdb
# from pydub import AudioSegment
# import io
# import time
import pandas as pd
import time
from datetime import datetime
import pytz
import ipdb
est = pytz.timezone('US/Eastern')

print("OZZ START")

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))


def sac_menu_buttons_func(main='Ozz'):
    if main=='Ozz':
        # sac_menu_buttons = sac.buttons([
        #     sac.ButtonsItem(label='Ozz', icon='robot'),
        #     sac.ButtonsItem(label='Lab', icon='backpack4-fill'),
        #     # sac.ButtonsItem(label='Ozz', icon='wechat', href=f'{st.session_state["streamlit_ip"]}/ozz'),
        #     sac.ButtonsItem(label='Client Models', disabled=True),
        #     sac.ButtonsItem(label='Account', icon='share-fill'),
        # ], 
        # format_func='title', align='end', type='text')
        sac_menu_buttons = sac.buttons(
            items=['Ozz', 'Lab', 'Client Models', 'Account'],
            index=0,
            format_func='title',
            align='center',
            direction='horizontal',
            radius='lg',
            # compact=False,
            return_index=False,
        )

    return sac_menu_buttons


force_db_root = st.session_state.get('force_db_root')
authenticator = all_page_auth_signin(force_db_root).get('authenticator')
user_session_state = init_user_session_state()
ip_address, streamlit_ip = return_app_ip() # "http://localhost:8501"

# if not check_fastapi_status(ip_address=ip_address):
#     if st.button("API"):
#         run_pq_fastapi_server()
#         time.sleep(3)
#         st.rerun()

if force_db_root and 'ozz_guest' in st.session_state:
    st.switch_page('pages/stefan.py')

with st.sidebar:
    st.write(f"force db, {force_db_root}")
        
client_user = st.session_state['username']

db_name, master_text_audio=init_text_audio_db()

cols = st.columns((3,2))

with st.sidebar:
    sac_menu = sac_menu_buttons_func()

if sac_menu == 'Ozz':
    ozz()
elif sac_menu == 'Lab':
    lab()

if 'current_youtube_search' in st.session_state and st.session_state['current_youtube_search'] != False:
    youtube()

db_root = st.session_state['db_root']
if st.session_state.get('admin'):
    st.warning("ADMIN")
    constants = init_constants()
    OZZ_DB = constants.get('OZZ_DB')
    master_conversation_history_file_path = os.path.join(db_root, 'master_conversation_history.json')
    MConvHistory = load_local_json(master_conversation_history_file_path)

    # conversation_history_file_path = os.path.join(db_root, 'conversation_history.json')
    # session_state_file_path = os.path.join(db_root, 'session_state.json')
    master_text_audio_filepath = os.path.join(OZZ_DB, 'master_text_audio.json') 
    # load db

    conversation_history_file_path = os.path.join(db_root, 'conversation_history.json')
    print(conversation_history_file_path)
    CVH = load_local_json(conversation_history_file_path)
    st.write("curent conversation history")
    st.write(pd.DataFrame(CVH))

    master_text_audio = load_local_json(master_text_audio_filepath)
    with st.expander("All Conversational History"):
        df_mch = pd.DataFrame(MConvHistory)
        df_mch['datetime'] = pd.to_datetime(df_mch['datetime'], format="%Y-%m-%d %H-%M-%S %p %Z", errors='coerce')
        today = datetime.now(est).replace(hour=0)
        print(today)
        # df_mch[df_mch['datetime'] > today]
        st.dataframe(df_mch)
    with st.expander("SneakPeak Master Conv"):
        db_root = os.path.join(OZZ_DB, 'sneakpeak')
        sp_mastet_conv_history = load_local_json(master_conversation_history_file_path)
        master_conversation_history_file_path = os.path.join(db_root, 'master_conversation_history.json')
        df = pd.DataFrame(sp_mastet_conv_history)
        st.dataframe(df)
    with st.expander("Master Text Audio"):
        # check master    
        df = pd.DataFrame(master_text_audio)
        st.dataframe(df)

