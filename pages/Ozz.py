import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import init_user_session_state, hoots_and_hootie_keywords, return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder

load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####

def hoots_and_hootie(width=350, height=350, 
                     self_image="hootsAndHootie.png", 
                     face_recon=True, 
                     show_video=True, 
                     input_text=True, 
                     show_conversation=True, 
                     no_response_time=3,
                     refresh_ask=True):
    
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()

    custom_voiceGPT(
        api=f"{st.session_state['ip_address']}/api/data/voiceGPT",
        api_key=os.environ.get('ozz_key'),
        client_user=st.session_state['client_user'],
        self_image=self_image,
        width=width,
        height=height,
        hello_audio="test_audio.mp3",
        face_recon=face_recon, # True False, if face for 4 seconds, trigger api unless text being recorded trigger api, else pass
        show_video=show_video, # True False, show the video on page
        # listen=listen, # True False if True go into listen mode to trigger api
        input_text=input_text,
        show_conversation=show_conversation,
        no_response_time=no_response_time,
        refresh_ask=refresh_ask,
        before_trigger={'how are you': 'hoots_waves__272.mp3'},
        api_audio='http://127.0.0.1:8000/api/data/',
        commands=[{
            "keywords": hoots_and_hootie_keywords(), # keywords are case insensitive
            "api_body": {"keyword": "hey hoots"},
        }, {
            "keywords": ["bye Hoots"],
            "api_body": {"keyword": "bye hoots"},
        }
        ]
    )

    return True

def ozz():
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


    width=st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    height=st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image=st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else "hootsAndHootie.png"
    face_recon=st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    show_video=st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    input_text=st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    show_conversation=st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    no_response_time=st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3
    refresh_ask=st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else False
    cols = st.columns((5,3,3))
    with cols[1]:
        user_output = st.empty()
    with cols[2]:
        rep_output = st.empty()
    
    with cols[0]:
        st.write("Say Hey Hoots OR Hey Hootie")
        hoots_and_hootie(
            width=width,
            height=height,
            self_image=self_image,
            face_recon=face_recon,
            show_video=show_video,
            input_text=input_text,
            show_conversation=show_conversation,
            no_response_time=no_response_time,
            refresh_ask=refresh_ask,
            )


    if 'query' in st.session_state:
        with user_output.container():
            name = client_user.split("@")[0]
            st.info(f"{name}: {st.session_state['query']}")
    if 'resp' in st.session_state:
        with rep_output.container():
            st.warning(f"Hoots: {st.session_state['resp']}")

if __name__ == '__main__':
    ozz()




## did not work??
# Layout for the form 
# with st.form("myform"):

#     "### A form"

#     # These exist within the form but won't wait for the submit button
#     placeholder_for_selectbox = st.empty()
#     placeholder_for_optional_text = st.empty()

#     # Other components within the form will actually wait for the submit button
#     radio_option = st.radio("Select number", [1, 2, 3], horizontal=True)
#     submit_button = st.form_submit_button("Submit!")

# # Create selectbox
# with placeholder_for_selectbox:
#     options = [f"Option #{i}" for i in range(3)] + ["Another option..."]
#     selection = st.selectbox("Select option", options=options)

# # Create text input for user entry
# with placeholder_for_optional_text:
#     if selection == "Another option...":
#         otherOption = st.text_input("Enter your other option...")

# # Code below is just to show the app behavior
# with st.sidebar:

#     "#### Notice that our `st.selectbox` doesn't really wait for `st.form_submit_button` to be clicked to update its value"
#     st.warning(f"`st.selectbox` = *{selection}*")

#     "#### But the other components within `st.form` do wait for `st.form_submit_button` to be clicked to update their value"
#     st.info(f"`st.radio` = {radio_option}")

#     "----"
#     "#### It's better to condition the app flow to the form_submit_button... just in case"
#     if submit_button:
#         if selection != "Another option...":
#             st.info(
#                 f":white_check_mark: The selected option is **{selection}** and the radio button is **{radio_option}**")
#         else:
#             st.info(
#                 f":white_check_mark: The written option is **{otherOption}** and the radio button is **{radio_option}** ")
#     else:
#         st.error("`st.form_submit_button` has not been clicked yet")