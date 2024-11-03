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
from custom_button import cust_Button
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
    if st.session_state['authentication_status'] != True:
        cust_Button("misc/fairy.png", hoverText='SignIn', key='signin', default=False, height=f'20px') # "https://cdn.onlinewebfonts.com/svg/img_562964.png"

    stoggle("How to Create your Personal Letters",
            """Follow the Tabs Below, Give your Characters Names, Personality, And Create Your Letters!""")