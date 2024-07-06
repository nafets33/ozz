import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import init_user_session_state, generate_image, return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv

load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####


def gen_images():
    main_root = ozz_master_root()  # os.getcwd()
    # load_dotenv(os.path.join(main_root, ".env"))
    set_streamlit_page_config_once()

    ip_address, streamlit_ip = return_app_ip()

    if not sign_in_client_user():
        st.stop()

    init_user_session_state()
    
    refresh_ask = True if 'page_refresh' not in st.session_state else False
    st.session_state['page_refresh'] = True
    client_user = st.session_state['client_user']

    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')
    OZZ_db_images = constants.get('OZZ_db_images')
    images_ = os.listdir(OZZ_db_images)




    # START
    st.title('Create Images')

    # st.image(fn)
    gen_im_text = st.text_input("generate Images")
    gen_source = st.selectbox('image gen source', options=['replicate', 'dalle'], index=['replicate', 'dalle'].index('replicate'))
    # Assuming you call the function somewhere in your Streamlit script
    if st.button("generate images"):
        image_responses = generate_image(text=gen_im_text, gen_source=gen_source)

        # Display the images in your Streamlit app
        cols = st.columns(3)
        col_count = 0
        for file_path, image_reponse in image_responses.items():
            with cols[col_count]:
                file_path_ = os.path.join(OZZ_db_images, file_path)
                st.image(file_path_, caption=f'Generated Image {file_path}', use_column_width=True)
            col_count+=1

    st.header("Saved Images")
    self_image = st.sidebar.selectbox("Select Image", options=images_, key='pic')
    if self_image:
        file_path = os.path.join(OZZ_db_images, self_image)
        if os.path.exists(file_path):
            st.image(file_path, caption=f'Saved Image {file_path}', use_column_width=True)

if __name__ == '__main__':
    gen_images()
