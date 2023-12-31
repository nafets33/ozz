import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from ozz_auth import signin_main
from master_ozz.utils import setup_instance, return_app_ip, init_text_audio_db, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from pages.Ozz import ozz
from pages.Lab import lab
from pages.YouTube import youtube

import streamlit_antd_components as sac

print("OZZ START")

main_root = ozz_master_root()  # os.getcwd()
# load_dotenv(os.path.join(main_root, ".env"))


def sac_menu_buttons_func(main='Ozz'):
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


import ipdb
# ipdb.set_trace()

set_streamlit_page_config_once()

if 'page_refresh_count' not in st.session_state:
    st.session_state['page_refresh_count'] = 0
print(st.session_state['page_refresh_count'])

authenticator = signin_main()
force_db_root=False
if st.session_state['authentication_status'] != True: ## None or False
    force_db_root = True
    if not sign_in_client_user():
        st.stop()

client_user = st.session_state['client_user']
prod = setup_instance(client_username=client_user, switch_env=False, force_db_root=force_db_root, queenKING=True, init=True, prod=True)

master_text_audio=init_text_audio_db()

ip_address, streamlit_ip = return_app_ip() # "http://localhost:8501"
print(ip_address)
print([i for i, v in st.session_state.items()])


# STARTst.write('Ozz')
st.write('Ozz')

sac_menu = sac_menu_buttons_func()
st.info(sac_menu)
# sac_menu_main(sac_menu)
if sac_menu == 'Ozz':
    ozz()
elif sac_menu == 'Lab':
    lab()

if 'current_youtube_search' in st.session_state and st.session_state['current_youtube_search'] != False:
    youtube()

st.write('Ozz')

st.button("refresh")
st.session_state['page_refresh_count']+=1