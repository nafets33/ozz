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
import base64
import ipdb
from pydub import AudioSegment
import io
import time

print("OZZ START")

main_root = ozz_master_root()  # os.getcwd()
load_dotenv(os.path.join(main_root, ".env"))

# Create a function to listen for the keyword
def listen_for_keyword(hey_hooty, timeout=23, phrase_time_limit=2):
    kw_found = False
    keyword = None

    while not keyword or not keyword.strip():
        with sr.Microphone() as source:
            with listening.container():
                st.info("Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            # print(vars(recognizer))

        try:
            # Recognize the keyword
            keyword = recognizer.recognize_google(audio)
            print(keyword)
            st.session_state['query'] = keyword

            # Check if the keyword is non-empty before further processing
            if keyword and keyword.strip():
                for kw in hey_hooty:
                    if kw in keyword:
                        kw_found = True
                        # with keywordfound.container():
                        #     st.success("Keyword detected!")

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            break  # Break out of the loop on request error

    print("NOTHING HERE")
    return kw_found, keyword


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


def play_audio(response):
    # Get the duration of the audio
    audio_content = io.BytesIO(response.content)
    audio = AudioSegment.from_file(audio_content)
    audio_duration = audio.duration_seconds

    # Play the audio in the Streamlit app
    audio_base64 = base64.b64encode(response.content).decode('utf-8')
    audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
    st.markdown(audio_tag, unsafe_allow_html=True)

    # Introduce a delay to wait for audio playback to finish
    time.sleep(audio_duration)

    return True

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
with st.sidebar:
    st.write(f"force db, {force_db_root}")
client_user = st.session_state['client_user']
prod = setup_instance(client_username=client_user, switch_env=False, force_db_root=force_db_root, queenKING=True, init=True, prod=True)

db_name, master_text_audio=init_text_audio_db()

ip_address, streamlit_ip = return_app_ip() # "http://localhost:8501"
# print([i for i, v in st.session_state.items()])

recognizer = sr.Recognizer()

listening = st.empty()
cols = st.columns(2)

# with cols[0]:
#     output = st.empty()
# with cols[1]:
#     keywordfound = st.empty()

with st.sidebar:
    llm_audio = st.empty()


hey_hooty = hoots_and_hootie_keywords()

with st.sidebar:
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


# cols = st.columns(2)
# with cols[0]:
st.title('Hoots & Hootie')
# with cols[1]:
st.header("Click And Ask!")

def listen_and_respond(hey_hooty, self_image, refresh_ask, client_user, phrase_time_limit=3):
    kw_found, kw = listen_for_keyword(hey_hooty, phrase_time_limit)
    with listening.container():
        st.warning("One Sec, Thinking...")

    text = [{'user': kw}]
    ozz_response = ozz_query(text, self_image, refresh_ask, client_user)
    hoots_reponse = ozz_response.get('text')[-1]['resp']
    audio_url = ozz_response.get('audio_path')
    
    st.session_state['query'] = kw
    st.session_state['resp'] = hoots_reponse
    
    response=requests.get(f"{st.session_state['ip_address']}/api/data/{audio_url}")
    
    with llm_audio.container():
        # st.info(kw)
        st.audio(response.content, format="audio/mp3")  # Adjust the format based on your audio file type
        # st.session_state['llm_audio_response'] = response.content

    listening.empty()

    return ozz_response, response



# Buttons
cols = st.columns(4)
with cols[0]:
    ask_hoots_button = st.button("Ask Hoots", use_container_width=True)

with cols[1]:
    st.button("Story Time", use_container_width=True)
with cols[2]:
    st.button("Directtions", use_container_width=True)
with cols[3]:
    st.button("?", use_container_width=True)

st.session_state['page_refresh_count']+=1
with st.sidebar:
    st.warning(f"page refresh count: , {st.session_state['page_refresh_count']}")


if sac_menu == 'Ozz':
    ozz()
elif sac_menu == 'Lab':
    lab()

if 'current_youtube_search' in st.session_state and st.session_state['current_youtube_search'] != False:
    youtube()



if ask_hoots_button:
    ozz_response, response = listen_and_respond(hey_hooty, self_image, refresh_ask, client_user)
    if response:
        play_audio(response)

    if ozz_response.get('listen_after_reply'):
        with listening.container():
            st.warning("Speak Up Please")
        ozz_response, response = listen_and_respond(hey_hooty, self_image, refresh_ask, client_user, phrase_time_limit=5)
        if response:
            play_audio(response)


