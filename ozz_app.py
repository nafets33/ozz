import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from master_ozz.utils import sac_menu_main, sac_menu_buttons, return_app_ip, init_text_audio_db, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from pages.Ozz import ozz
from pages.Lab import lab

main_root = ozz_master_root()  # os.getcwd()
# load_dotenv(os.path.join(main_root, ".env"))

set_streamlit_page_config_once()

master_text_audio=init_text_audio_db()

ip_address, streamlit_ip = return_app_ip() # "http://localhost:8501"
print(ip_address)
print(st.session_state)
if not sign_in_client_user():
    st.stop()


client_user = st.session_state['client_user']


constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')


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



# STARTst.write('Ozz')
st.write('Ozz')

sac_menu = sac_menu_buttons()
st.info(sac_menu)
# sac_menu_main(sac_menu)
if sac_menu == 'Ozz':
    ozz()
elif sac_menu == 'Lab':
    lab()

st.write('Ozz')

st.button("refresh")