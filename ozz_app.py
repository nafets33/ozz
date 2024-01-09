import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from ozz_auth import signin_main
from master_ozz.utils import hoots_and_hootie_keywords, init_user_session_state, setup_instance, return_app_ip, init_text_audio_db, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from master_ozz.ozz_query import ozz_query
from pages.Ozz import ozz
from pages.Lab import lab
from pages.YouTube import youtube
import speech_recognition as sr
import requests
import streamlit_antd_components as sac

import ipdb
# ipdb.set_trace()

print("OZZ START")

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

# Create a function to listen for the keyword
def listen_for_keyword(hey_hooty, conv=False):
    with sr.Microphone() as source:
        with listening.container():
            st.info("Listening...")
        audio = recognizer.listen(source, timeout=23, phrase_time_limit=2)
        # print(vars(recognizer))

    try:
        # Recognize the keyword
        keyword = recognizer.recognize_google(audio)
        print(keyword)

        if conv:
            return keyword

        keyword_l = keyword.split()[0]
        kw_found = False
        for kw in hey_hooty:
            if kw in keyword:
                with keywordfound.container():
                    st.success("Keyword detected!")

                return keyword

        return False


    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    return False


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
# print(ip_address)
# print([i for i, v in st.session_state.items()])
recognizer = sr.Recognizer()
output = st.empty()
listening = st.empty()
keywordfound = st.empty()
hey_hooty = hoots_and_hootie_keywords()

sac_menu = sac_menu_buttons_func()

init_user_session_state()

width=st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
height=st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
self_image=st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else "hootsAndHootie.png"
face_recon=st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
show_video=st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
input_text=st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
show_conversation=st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
no_response_time=st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3
refresh_ask=st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else False

json_voiceGPT_data={
'api:': f"{st.session_state['ip_address']}/api/data/voiceGPT",
'api_key:': os.environ.get('ozz_key'),
'text': {},
'refresh_ask': refresh_ask,
'face_data': [],
'client_user:': st.session_state['client_user'],
'self_image:': self_image,
}


if st.button("Ask Hoots"):
    kw = listen_for_keyword(hey_hooty)
    st.info(kw)
    print(kw)
    if kw:
        print("CALL FASTAPI")
        json_voiceGPT_data['text'] = {'user': kw}
        text = {}
        print(json_voiceGPT_data)
        # response = requests.post(f"{st.session_state['ip_address']}/api/data/voiceGPT", 
        #                         data=json_voiceGPT_data,
        #                         headers={"Content-Type": "application/json"},
        #                         )
        response = ozz_query(text, self_image, refresh_ask, client_user)
        print(response)

    listening.empty()

if sac_menu == 'Ozz':
    ozz()
elif sac_menu == 'Lab':
    lab()

if 'current_youtube_search' in st.session_state and st.session_state['current_youtube_search'] != False:
    youtube()


st.button("refresh")
st.session_state['page_refresh_count']+=1
st.warning(f"page refresh count: , {st.session_state['page_refresh_count']}")


