import streamlit as st
from ozz_auth import all_page_auth_signin

import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import init_text_image_db, init_user_session_state, generate_image, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
import pandas as pd

load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####


def gen_images():
    main_root = ozz_master_root()  # os.getcwd()
    # load_dotenv(os.path.join(main_root, ".env"))
    set_streamlit_page_config_once()

    auth_ = all_page_auth_signin()

    init_user_session_state()
    
    refresh_ask = True if 'page_refresh' not in st.session_state else False
    st.session_state['page_refresh'] = True
    client_user = st.session_state['client_user']

    constants = init_constants()
    OZZ_DB = constants.get('OZZ_DB')
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')
    OZZ_db_images = constants.get('OZZ_db_images')
    images_ = os.listdir(OZZ_db_images)
    images_ = sorted(images_, key=lambda x: os.path.getmtime(os.path.join(OZZ_db_images, x)), reverse=True)

    def generate_visual_prompt(category="nature", subcategory="forest", details="tall trees with sunlight filtering through", mood="serene", color_palette="earthy tones", lighting="soft morning light", perspective="eye-level", style="realistic", action="leaves rustling in the wind"):
        prompt = f"Create a {mood} {style} image of a {subcategory} in {category}, featuring {details}. "
        prompt += f"The scene should be captured from a {perspective} perspective, using a {color_palette} color palette with {lighting}. "
        if action:
            prompt += f"Include dynamic elements like {action}. "
        prompt += "Ensure the image is visually cohesive and striking."
        return prompt

    # Example usage:
    visual_prompt = generate_visual_prompt()


    # START
    st.title('Create Images')

    # st.image(fn)
    gen_im_text = st.text_area("generate Images", value=visual_prompt)
    gen_source = st.sidebar.selectbox('image gen source', options=['replicate', 'dalle'], index=['replicate', 'dalle'].index('dalle'))
    # Assuming you call the function somewhere in your Streamlit script
    image_name = st.text_input("Image Name")
    image_name = None if len(image_name) == 0 else image_name
    print(image_name)
    if st.button("generate images"):
        image_responses = generate_image(text=gen_im_text, gen_source=gen_source, image_name=image_name)

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

    MT_Image = init_text_image_db('master_text_image.json')
    df = pd.DataFrame(MT_Image)
    st.write(df)

if __name__ == '__main__':
    gen_images()
