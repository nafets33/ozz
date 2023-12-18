import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import sac_menu_main, sac_menu_buttons, hoots_and_hootie, return_app_ip, init_text_audio_db, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv

def ozz():
    main_root = ozz_master_root()  # os.getcwd()
    # load_dotenv(os.path.join(main_root, ".env"))

    set_streamlit_page_config_once()
    # sac_menu = sac_menu_buttons()
    # sac_menu_main(sac_menu)

    ip_address, streamlit_ip = return_app_ip("http://localhost:8501")
    print(ip_address)

    if not sign_in_client_user():
        st.stop()

    client_user = st.session_state['client_user']

    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')


    # START
    st.title('Hoots & Hootie')

    hoots_and_hootie()
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