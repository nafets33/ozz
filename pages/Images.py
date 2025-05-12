import streamlit as st
from ozz_auth import all_page_auth_signin

import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import init_text_image_db, init_user_session_state, generate_image, ozz_master_root, generate_visual_prompt, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from dotenv import load_dotenv
import pandas as pd

load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####

# def generate_visual_prompt(category="nature", subcategory="forest", details="tall trees with sunlight filtering through", 
#                            mood="serene", color_palette="earthy tones", lighting="soft morning light", 
#                            perspective="eye-level", style="realistic", action="leaves rustling in the wind"):
#     prompt = f"Create a {mood} {style} image of a {subcategory} in {category}, featuring {details}. "
#     prompt += f"The scene should be captured from a {perspective} perspective, using a {color_palette} color palette with {lighting}. "
#     if action:
#         prompt += f"Include dynamic elements like {action}. "
#     prompt += "Ensure the image is visually cohesive and striking."
#     return prompt

def show_image_history():
    MT_Image = init_text_image_db('master_text_image.json')
    df = pd.DataFrame(MT_Image)
    df = df.sort_index(ascending=False)
    st.write(df)

def saved_images(OZZ_db_images):
    st.header("Saved Images")
    images_ = os.listdir(OZZ_db_images)
    images_sorted = sorted(
        images_,
        key=lambda x: os.path.getmtime(os.path.join(OZZ_db_images, x)),
        reverse=True
    )
    self_image = st.selectbox("Select Image", options=images_sorted, key='pic')
    file_path = os.path.join(OZZ_db_images, self_image)
    if os.path.exists(file_path):
        st.image(file_path, caption=f'Saved Image {file_path}', use_container_width=False, width=250)

def gen_images(visual_prompt=None, OZZ_db_images=None):
    # main_root = ozz_master_root()  # os.getcwd()
    # START
    if not OZZ_db_images:
        constants = init_constants()
        OZZ_db_images = constants.get('OZZ_db_images')

    if not visual_prompt:
        visual_prompt = generate_visual_prompt()
    with st.form("create image"):
        st.title('Create Images')
        gen_im_text = st.text_area("generate Images", value=visual_prompt)
        gen_source = st.sidebar.selectbox('image gen source', options=['replicate', 'dalle'], index=['replicate', 'dalle'].index('dalle'))
        # Assuming you call the function somewhere in your Streamlit script
        image_name = st.text_input("Image Name")
        image_name = None if len(image_name) == 0 else image_name

        if st.form_submit_button("generate images"):
            image_responses = generate_image(text=gen_im_text, gen_source=gen_source, image_name=image_name)
            for file_path, image_reponse in image_responses.items():
                file_path_ = os.path.join(OZZ_db_images, file_path)
                st.image(file_path_, caption=f'Generated Image {file_path}', use_container_width=False, width=250)


    saved_images(OZZ_db_images)
    show_image_history()

if __name__ == '__main__':
    # load_dotenv(os.path.join(main_root, ".env"))
    all_page_auth_signin()

    init_user_session_state()

    gen_images()

    
