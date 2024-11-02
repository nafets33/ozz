import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import ozz_characters, save_json, init_text_audio_db, ozz_master_root_db, init_user_session_state, hoots_and_hootie_keywords, return_app_ip, ozz_master_root, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants, refreshAsk_kwargs
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
import requests
import base64
from ozz_auth import all_page_auth_signin

# from custom_button import cust_Button
load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####

def hoots_and_hootie(width=350, height=350, 
                     self_image="hootsAndHootie.png", 
                     face_recon=True, 
                     show_video=True, 
                     input_text=True, 
                     show_conversation=True, 
                     no_response_time=3,
                     refresh_ask={},
                     use_embeddings=[],
                     before_trigger={},
                     phrases=[],):
    
    to_builder = VoiceGPT_options_builder.create()
    to = to_builder.build()

    force_db_root = True if 'force_db_root' in st.session_state and st.session_state['force_db_root'] else False

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
        force_db_root=force_db_root,
        before_trigger={'how are you': 'hoots_waves__272.mp3', 'phrases': phrases},
        api_audio=f"{st.session_state['ip_address']}/api/data/",
        # use_embeddings=use_embeddings,
        commands=[{
            "keywords": phrases, # keywords are case insensitive
            "api_body": {"keyword": "hey hoots"},
        }, {
            "keywords": ["bye Hoots"],
            "api_body": {"keyword": "bye hoots"},
        }
        ]
    )

    return True

def ozz():

    cols = st.columns((3,2))
    with cols[0]:
        col_1 = st.empty()
    with cols[1]:
        col_2 = st.empty()

    user_session_state = init_user_session_state()

    characters = ozz_characters()
    st.session_state['characters'] = characters
    with col_2.container():
        self_image = st.selectbox("Speak To", options=characters.keys(), key='self_image')
    
    tabs = st.tabs([f"{self_image.split('.')[0]}", 'System Prompt'])

    with tabs[1]:
        header_prompt = st.text_area("System_Prompt", characters[st.session_state.get('self_image')].get('main_prompt'), height=500)
    
    refresh_ask = refreshAsk_kwargs(header_prompt=header_prompt)
    st.session_state['page_refresh'] = True
    client_user = st.session_state['client_user']
    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')
    
    db_root = st.session_state['db_root']
    session_state_file_path = os.path.join(db_root, 'session_state.json')

    st.session_state['hh_vars']['self_image'] = st.session_state['self_image']

    width=st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    height=st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image=st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else f"{st.session_state.get('self_image')}.png"
    face_recon=st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    show_video=st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    input_text=st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    show_conversation=st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    no_response_time=st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3
    refresh_ask=st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else refreshAsk_kwargs()
    
    embedding_default = []
    if self_image == 'stefan.png':
        with col_1.container():
            st.header(f"Stefans '''~Conscience'''...")

        embedding_default = ['stefan']
        user_session_state['use_embeddings'] = embedding_default
        save_json(session_state_file_path, user_session_state)

        text = "...Well sort of, it's WIP...Responses may be delay'd, ⚡faster-thinking and processing always costs more 💰"
        st.write(text)
        # with cols[0]:
        #     st.markdown(f'<span style="color: red;">{text}</span>', unsafe_allow_html=True)

    else:
        embedding_default = []
        user_session_state['use_embeddings'] = embedding_default
        save_json(session_state_file_path, user_session_state)


    with st.sidebar:
        embeddings = os.listdir(os.path.join(ozz_master_root(), 'STORAGE'))
        embeddings = ['None'] + embeddings
        use_embeddings = st.multiselect("use embeddings", default=embedding_default, options=embeddings)
        st.session_state['use_embedding'] = use_embeddings
        if st.button("save"):
            user_session_state['use_embeddings'] = use_embeddings
            save_json(session_state_file_path, user_session_state)
            st.info("saved")
    

    with st.sidebar:
        # rep_output = st.empty()
        selected_audio_file=st.empty()
        llm_audio=st.empty()


    phrases = hoots_and_hootie_keywords(characters, self_image.split(".")[0])

    with tabs[0]:
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
            use_embeddings=use_embeddings,
            phrases=phrases,
            )

    if self_image == 'stefan.png':
        with st.expander("3 Ways to chat", True):
            cols = st.columns((3,3))
            with cols[0]:
                st.info("1: RECOMMENDED --> Click And Ask Button: Each time you click you can speak your question")
                st.info("2: Conversational Mode Button: Once you click, use Keyword 'Stefan', ex: 'Stefan How Are you today' (If stefan responds with a question you can directly answer it and don't need to say his name)")
                st.info("3: Chat Form: Type your questions and hit enter")
            with cols[1]:
                st.error("Speach ONLY works on Desktop and does not work on Mobile")
                st.error("Please note: Sometimes questions may be misunderstood and the response may result in inchorent manner.")
                st.error("The LLM that uses RAG (i.e. this one) needs extra context to undestand each new query from user, Having responses tailor more accurately requires more engineering")

    def list_files_by_date(directory):
        files = []
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                files.append((filepath, os.path.getmtime(filepath)))
        files.sort(key=lambda x: x[1], reverse=True)
        return files
    
    # # Options for the selectbox
    # options = ['Option 1', 'Option 2', 'Option 3', 'Custom Input']
    # # Create a selectbox with an additional option for custom input
    # selected_option = st.selectbox("Session Type", options)
    # # If 'Custom Input' is selected, show a text input field
    # if selected_option == 'Custom Input':
    #     custom_input = st.text_input("Enter your custom input")
    #     st.write(f"You entered: {custom_input}")
    # else:
    #     st.write(f"You selected: {selected_option}")


    # Get list of audio files sorted by modification date
    db_name, master_text_audio=init_text_audio_db()

    root_db = ozz_master_root_db()
    db_DB_audio = os.path.join(root_db, 'audio')
    audio_files = list_files_by_date(db_DB_audio)
    with selected_audio_file.container():
        audio_path = st.selectbox("Select Audio File", [os.path.basename(file[0]) for file in audio_files])
    # st.write(master_text_audio[-1])
    # st.write([i for i in st.session_state])
    # st.write(st.session_state['conversation_history.json'])
    response=requests.get(f"{st.session_state['ip_address']}/api/data/{audio_path}")
    with llm_audio.container():
        # st.info(kw)
        st.audio(response.content, format="audio/mp3")  




    def local_gif(gif_path, width="33", height="33", sidebar=False, url=False):
        if url:
            data_url = data_url
        else:
            with open(gif_path, "rb") as file_:
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
            if sidebar:
                st.sidebar.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" width={width} height={height} alt="bee">',
                    unsafe_allow_html=True,
                )

        return True


    # st.write(client_user)
    if client_user == 'stefanstapinski@gmail.com':
        with st.sidebar:
            st.write("Admin Only")
            st.write(st.session_state)
if __name__ == '__main__':
    ozz()

