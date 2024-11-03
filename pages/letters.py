# great now redo 1st grade with same concept as 2nd grade. but reduce length per letter to 8-15 range
import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import llm_assistant_response, ozz_characters,handle_prompt, get_last_eight, init_constants, page_line_seperator, load_local_json, ozz_master_root, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, generate_visual_prompt
from streamlit_extras.switch_page_button import switch_page
from ozz_auth import all_page_auth_signin
from streamlit_tags import st_tags
import requests
from pages.Images import gen_images
# from custom_button import cust_Button
from streamlit_extras.stoggle import stoggle

def themes(action='adventure', subject='travling to a queens castle'):
    return {'action': action, 'subject': subject}
# {'adventure', 'sharing', 'helping others', 'learning', 'mystery', 'friendship'}

def create_letters_prompt(
    character_name='ozzy', 
    character_2_name='vivi', 
    character_type1='Gnome', 
    character_type2='Owl', 
    stage='kindergarten', 
    n_letters=20, 
    min_length=8, 
    max_length=20, 
    # themes={'action': 'adventure', 'subject': 'traveling to a queen’s castle'},
    theme_action='adventure',
    theme_subject='traveling to a queen’s castle',
    site_words=[
        "I", "a", "can", "is", "in", "on", "it", "we", "go", "the", 
        "my", "up", "no", "to", "yes", "me", "see", "run", "at", "big",
        "am", "if", "be", "by", "do", "he", "us", "an", "as", "so"
    ],
    create_template='yes',
    first_letters='yes',
    start_letter = 1,
):
    """    
    Creates a detailed prompt for generating engaging letters for kids, incorporating various themes and stages.
    """
    header = f"""
    Generate {n_letters} engaging letters for {stage} students, written by {character_name}, a {character_type1}, with {character_2_name}, an {character_type2}. 
    Each letter should be tailored to {stage}. 
    For each level, ensure the letters are suitable for the following educational stages:
    """

    header_details = f"""
        <Have the letters tell like a story, for example, letter 1 would go to a place, letter 2 would then talk about the place and the encounters with a follow up question to the reader>
    <Incorporate the following words into the letters: {', '.join(site_words)}>
    <Letters are to be in the range of {min_length} to {max_length} characters.>
    """

    if first_letters:
        first_letters="Make letters 1-3 about the characters introducing themselves to the reader, explain they are a magical pen pale and they're told by the magic world to write to the reader"
        start_letter = 4

    # # Update theme_prompts using n_letters
    # theme_length = max(1, n_letters // len(themes))  # Ensure each theme covers a segment of letters
    # theme_prompts = ''
    # for key, value in themes.items():
    #     end_letter = min(start_letter + theme_length - 1, n_letters)
    #     theme_prompts += f"Make letter {start_letter} to {end_letter} about an {key} of {value}.\n"
    #     start_letter = end_letter + 1  # Move to the next segment
    
    if create_template:
        create_template = '<MAKE SURE YOU> return the output Letters as a dictionary, and (character_name, character_2_name, character_type1, character_type2) so those attributes are reflected in brackets within each letter. dictionary will be as letter_number: letter_contents'
        header = f"""
    Generate {n_letters} engaging letters for {stage} students, written by the following attributes, return those attributes in dictionary brackets, attributes are character_name, character_type1, character_2_name, and character_type2. 
    Each letter should be tailored to {stage}. 
    """
    prompt = f"""
    Main Details
    {header}

    Letter Details to Consider:
    {header_details}

    - Mention both characters in only half of the letters.
    - Reflect the current stage's {stage} complexity and understanding.
    - Be captivating and educational, encouraging children to engage with different themes.
    - Ask follow-up questions in 50% of the letters.
    - Be funny when possible.
    - Speak in the first person.
    - Do not be repetitive between the letters 
    - {first_letters}

    Themes to include:
    - The letters are to be about the theme {theme_action}
    - The letters are will also be about {theme_subject}

    Please make sure each letter is slightly different then
    Please ensure that each letter fits within the range of appropriate length and complexity for the given stage.

    - Special Instructions:
    {create_template}
    """

    return prompt


if __name__ == '__main__':
    constants = init_constants()
    character_selection = os.path.join(constants.get('OZZ_DB'), 'characters')

    all_page_auth_signin()
    stoggle("How to Create your Personal Letters",
            """Follow the Tabs Below, Give your Characters Names, Personality, And Create Your Letters!""")

    tabs = st.tabs(["Character Details", "Stage - Site Words", "Theme", "Extras", 'Select your Character', 'Letter Style'])

    with tabs[5]:
        cols = st.columns(3)
        with cols[0]:
            background_image_url = f"{st.session_state['ip_address']}/api/data/luck.png"
            st.image(background_image_url, use_column_width=True)


    with tabs[4]:
        cols = st.columns(3)
        with cols[0]:
            background_image_url = f"{st.session_state['ip_address']}/api/data/gnome_luck.png"
            img_1 = st.button('Select Lucky', use_container_width=True)
            img_1 = st.image(background_image_url, use_column_width=True)
        with cols[1]:
            background_image_url = f"{st.session_state['ip_address']}/api/data/hootsAndHootie.png"
            img_2 = st.button('Select Hoots & Hootie', use_container_width=True)
            img_2 = st.image(background_image_url, use_column_width=True)
        with cols[2]:
            background_image_url = f"{st.session_state['ip_address']}/api/data/gnome8.png"
            img_3 = st.button('Select Jeppy', use_container_width=True)
            img_3 = st.image(background_image_url, use_column_width=True)


    with tabs[0]:
        character_name = st.text_input("Character Name", value="ozzy")
        character_type1 = st.text_input("Character Type 1", value="Nom")
        character_2_name = st.text_input("Character 2 Name", value="vivi")
        character_type2 = st.text_input("Character Type 2", value="Owl")
    
    with tabs[1]:
        cols = st.columns(2)
        with cols[0]:
            stage = st.selectbox("Stage", ["kindergarten", "1st grade", "2nd grade"], index=0)
        with cols[1]:
            stage_level = st.selectbox("site words", options=['Level 1', 'Level 2', 'Level 3'])

        # Initialize site_words in session state if not already present
        if 'site_words' not in st.session_state:
            st.session_state['site_words'] = []

        # Update site_words in session state based on the selection
        if stage == 'kindergarten':
            st.session_state['site_words'] = [
                "I", "a", "can", "is", "in", "on", "it", "we", "go", "the", 
                "my", "up", "no", "to", "yes", "me", "see", "run", "at", "big", 
                "am", "if", "be", "by", "do", "he", "us", "an", "as", "so"
            ]
        elif stage == '1st grade':
            st.session_state['site_words'] = ['my', 'mother']
        else:
            st.session_state['site_words'] = ['']
        
        keywords = st.multiselect("Site Words", options=st.session_state['site_words'], default=st.session_state['site_words'])

    with tabs[2]:
        theme_list = ['adventure', 'explore', 'holidays', 'school', 'summer', 'winter', 'spring']
        cols = st.columns((2,4))
        with cols[0]:
            theme_action = st.selectbox("Theme for Action", options=theme_list, index=theme_list.index('adventure'))
        with cols[1]:
            theme_subject = st.text_area("Theme for Subject", value="traveling to a queen’s castle")
    
    with tabs[3]:
        min_length = st.number_input("Minimum Letter Length", min_value=1, max_value=100, value=8)
        create_template = st.radio("Create Template?", options=["yes", "no"], index=0)
        max_length = st.number_input("Maximum Letter Length", min_value=1, max_value=100, value=20)
        first_letters = st.radio("Include First Letters?", options=["yes", "no"], index=0)
        start_letter = st.slider("Start Letter", min_value=1, max_value=20, value=1)
        n_letters = st.number_input("Number of Letters", min_value=1, max_value=50, value=20)




    page_line_seperator('5')

    st.header("Generate Letters")
    if st.button('Generate Letters'):
        prompt = create_letters_prompt(
                character_name=character_name, 
                character_2_name=character_2_name, 
                character_type1=character_type1, 
                character_type2=character_type2, 
                stage=stage, 
                n_letters=n_letters, 
                min_length=min_length, 
                max_length=max_length, 
                theme_action=theme_action,
                theme_subject=theme_subject,
                site_words=[
                    "I", "a", "can", "is", "in", "on", "it", "we", "go", "the", 
                    "my", "up", "no", "to", "yes", "me", "see", "run", "at", "big",
                    "am", "if", "be", "by", "do", "he", "us", "an", "as", "so"
                ],
                create_template='yes',
                first_letters='yes',
                start_letter = 1,
        )
        st.write(prompt)


    """ IMAGES """

    # images_ = os.listdir(character_selection)
    # images_ = sorted(images_, key=lambda x: os.path.getmtime(os.path.join(character_selection, x)), reverse=True)
    # st.header("Characters")
    # self_image = st.sidebar.selectbox("Select Image", options=images_)
    # if self_image:
    #     file_path = os.path.join(character_selection, self_image)
    #     if os.path.exists(file_path):
    #         st.image(file_path, caption=f'Saved Image {file_path}', use_column_width=False, width=250)
    
    # Define the background image URL (can be a local file path or a URL)

    # Example dictionary of letters
    letters = {
        1: "Hello! <br> I am Ozzy. <br>I love adventures. Do you?",
        2: "Vivi and I went to a magical forest. What do you think we found?",
        3: "We saw a big tree! Can you imagine how tall it was?"
    }

    # Choose the letter number
    # letter_num = st.selectbox("Choose a letter", options=list(letters.keys()))

    # Get the letter content from the dictionary
    letter_content = letters[1]

    background_image_url = f"{st.session_state['ip_address']}/api/data/luck.png" #"https://via.placeholder.com/500x300.png?text=Background+Image"

    # Create a container with background image and formatted text
    with st.sidebar:
        bg_color = st.color_picker("Choose Background Color", value='#FFFFFF')  # Default white
        text_color = st.color_picker("Choose Text Color", value='#000000')      # Default black
        no_bg_color = st.checkbox("No Background Color", value=False)
        if no_bg_color:
            bg_color = 'transparent'  # or use 'rgba(0, 0, 0, 0)' for full transparency

        font_size = st.selectbox("Choose Font Size", options=["36px", "20px", "24px", "28px", "32px"], index=1)  # Default is 24px
        # Font style selection
        font_styles = ["Arial", "Courier New", "Georgia", "Times New Roman", "Verdana"]
        font_style = st.selectbox("Choose Font Style", options=font_styles, index=0)  # Default is Arial

    # Create the styled HTML block
# Create the styled HTML block
    visual_prompt = generate_visual_prompt(category='at home', subcategory=f"{character_type1}, {character_type1} name is {character_name}", details=f'{theme_subject}', mood='happy', lighting='not too bright', style='artistic sketch', action='waving')
    gen_images(visual_prompt=visual_prompt)

    st.image(background_image_url, width=300)
    st.markdown(f"""
        <div style="
            background-image: url('{background_image_url}');
            background-size: cover;
            background-position: center;
            padding: 20px;
            height: 400px;
            width: 33%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {text_color}; /* Text color from selection */
            font-size: 24px;
            text-align: center;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        ">
            <p style="
                // background: {bg_color}; /* Background color from selection */
                background-position: center;
                padding: 5px;
                border-radius: 5px;
                color: {text_color}; /* Ensures text is readable */
            ">
                {letter_content}
            </p>
        </div>
    """, unsafe_allow_html=True)


    # from streamlit_extras.streaming_write import write 
    # import time
    # import numpy as np
    # import pandas as pd

    # def example():
    #     def stream_example():
    #         for word in "_LOREM_IPSUM".split():
    #             yield word + " "
    #             time.sleep(0.1)

    #         # Also supports any other object supported by `st.write`
    #         yield pd.DataFrame(
    #             np.random.randn(5, 10),
    #             columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    #         )

    #         for word in "_LOREM_IPSUM".split():
    #             yield word + " "
    #             time.sleep(0.05)

    #     if st.button("Stream data"):
    #         write(stream_example)
    # example()