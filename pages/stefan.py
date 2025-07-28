import streamlit as st
import os
from bs4 import BeautifulSoup
from ozz_auth import all_page_auth_signin
from pages.Characters import hoots_and_hootie
from master_ozz.utils import llm_response_to_html, save_json, refreshAsk_kwargs, ozz_master_root_db, init_user_session_state, return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, ozz_characters, CreateEmbeddings, Retriever, init_constants
from dotenv import load_dotenv
from custom_voiceGPT import custom_voiceGPT, VoiceGPT_options_builder
import requests
import base64
import ipdb

# from custom_button import cust_Button
load_dotenv(os.path.join(ozz_master_root(),'.env'))
#### CHARACTERS ####

def mark_down_text(
    text="Hello There",
    align="center",
    color="navy",
    fontsize="23",
    font="Arial",
    hyperlink=False,
    sidebar=False
):
    if hyperlink:
        st.markdown(
            """<a style='display: block; text-align: {};' href="{}">{}</a>
            """.format(
                align, hyperlink, text
            ),
            unsafe_allow_html=True,
        )
    else:
        if sidebar:
            st.sidebar.markdown(
                '<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text),unsafe_allow_html=True,)
        else:
            st.markdown(
            '<p style="text-align: {}; font-family:{}; color:{}; font-size: {}px;">{}</p>'.format(align, font, color, fontsize, text),unsafe_allow_html=True,)
    return True

def list_files_by_date(directory):
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            files.append((filepath, os.path.getmtime(filepath)))
    files.sort(key=lambda x: x[1], reverse=True)
    return files

def ozz():

    force_db_root=True
    st.session_state['force_db_root'] = force_db_root
    user_session_state = init_user_session_state()
    
    with st.sidebar:
        st.write(f"force db, {force_db_root}")
            
    client_user = st.session_state['ozz_guest']
    with st.sidebar:
        st.write(f"welcome {client_user}")
    
    st.title("Stefan Stapinski's ~Conscience")

    cols = st.columns((3,3))
    with cols[1]:
        mark_down_text("🗣️ Speach & Voice Recognitation 🎙️ ONLY works on a Computer ... I'll fix for Mobile eventually 🛠️", fontsize=15)
    with cols[0]:
        mark_down_text("Maybe one day :p .. It's just RAG. Responses may be delay'd, ⚡faster-thinking/processing costs more 💰", fontsize=15)
    
    characters = ozz_characters()
    st.session_state['characters'] = characters
    if 'ozz_guest' in st.session_state:
        # st.info("Welcome to Divergent Thinkers")
        st.session_state['self_image'] = 'stefan'
    else:
        self_image = st.sidebar.selectbox("Speak To", options=characters.keys(), key='self_image')
    
    if st.sidebar.toggle("sy_prompt"):
        header_prompt = st.text_area("System_Prompt", characters[st.session_state.get('self_image')].get('main_prompt'))
    else:
        header_prompt = characters[st.session_state.get('self_image')].get('main_prompt')
    
    refresh_ask = refreshAsk_kwargs(header_prompt=header_prompt)


    root_db = ozz_master_root_db()
    db_DB_audio = os.path.join(root_db, 'audio')
    audio_files = list_files_by_date(db_DB_audio)
    
    st.session_state['page_refresh'] = True
    client_user = st.session_state['client_user']
    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')
    
    db_root = st.session_state['db_root']
    session_state_file_path = os.path.join(db_root, 'session_state.json')

    width=350 #st.session_state['hh_vars']['width'] if 'hc_vars' in st.session_state else 350
    height=350# st.session_state['hh_vars']['height'] if 'hc_vars' in st.session_state else 350
    self_image=f"{st.session_state.get('self_image')}.png" #st.session_state['hh_vars']['self_image'] if 'hc_vars' in st.session_state else f"{st.session_state.get('self_image')}.png"
    face_recon= False # st.session_state['hh_vars']['face_recon'] if 'hc_vars' in st.session_state else False
    show_video=False #st.session_state['hh_vars']['show_video'] if 'hc_vars' in st.session_state else False
    input_text=True #st.session_state['hh_vars']['input_text'] if 'hc_vars' in st.session_state else True
    show_conversation=True #st.session_state['hh_vars']['show_conversation'] if 'hc_vars' in st.session_state else True
    no_response_time=3 #st.session_state['hh_vars']['no_response_time'] if 'hc_vars' in st.session_state else 3
    refresh_ask=refreshAsk_kwargs() #st.session_state['hh_vars']['refresh_ask'] if 'hc_vars' in st.session_state else refreshAsk_kwargs()

    tabs = st.tabs(['Talk To Stefan', 'Latest Project', '411'])


    embedding_default = []
    with tabs[0]:
        if self_image == 'stefan':
            cols = st.columns((5,3))
            embedding_default = ['stefan']
            st.session_state['use_embeddings'] = embedding_default
            save_json(session_state_file_path, user_session_state)
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
    
    with tabs[0]:
        show_video = st.toggle("Turn On Stefan's Real Voice", False, help="Toggles Turns On/Off the Real Voice for the responses, it will delay the response time")
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
            agent_actions=["Generate A Summary", "Create a Story", "Generate An Image"]
            )
        st.write("*** Note, if you click 'Start Conversation' use key phase 'Hey Stefan' to get a response from the Transcript")

    with tabs[1]:
        pollen = os.path.join(ozz_master_root(), 'pollen')
        fis = ['1', "1_1", '2', '3']
        # cols = st.columns((5,3))
        # with cols[0]:
        # st.write("# An AI Portfolio Manager")
        # with cols[0]:
        mark_down_text("My Latest side project -- An AI Portfolio Manager", color="navy", fontsize=25, font="Arial", align="left")
        # with cols[1]:
        st.markdown(
            '<h2 style="font-size:13px;">📄 <a <a href="https://quantqueen.com/LiveBot" target="_blank">Link to my Market-Trading-Engine -- Manage a Portfolio - Watch a Live Bot In Real Time</a>',
            unsafe_allow_html=True
        )
        
        for fi in fis:
            if fi == '1':
                msg = "1. Setup A Portfolio ♟️"
            elif fi == '1_1':
                msg = "2. Watch your Customized-AI-Manager Manage Your Account ⚙️"
            elif fi == '3':
                msg = "Monitor TimeSeries Calculated Price-Weighted-Poisitions ♚"
            else:
                msg = "3. Trade Alongside - Work Together, Customize the rules of your AI-Manager ♛"
            # if msg:
            #     mark_down_text(msg, fontsize=18, align="left")
            with st.expander(f"{msg}"):
                st.image(os.path.join(pollen, f'{fi}.png'))

    with tabs[2]:
        resume_path = os.path.join(pollen, 'resume_2.png')
        # Read the PDF file as binary
        # st.image(resume_path)
        # Header
        st.markdown("""
        # Stefan Stapinski  
        📞 (408) 693-1760 | 📧 StefanStapinski@gmail.com | 🌐 [Interview My AI](https://divergent-thinkers.com/stefan)  
        > _“We can do anything that we want to do.”_
        """)

        # Summary
        st.markdown("## SUMMARY")
        st.markdown("""
        **Systems Architect | Product Manager | Full-Stack Engineer | Revenue Accountant**  
        Innovative and pragmatic builder with 10+ years of experience leading the architecture, engineering, and product strategy behind scalable internal platforms and AI-driven tools. Proven track record in automating revenue systems, shipping products with lean teams, and bridging business needs with engineering execution. Self-taught in most technologies.
        """)

        # Technical Toolkit
        st.markdown("## TECHNICAL TOOLKIT")
        st.markdown("""
        **Languages & Frameworks:** Python, SQL, JavaScript, React, Node.js, Go, Rust, Django, VBA  
        **Infrastructure:** Docker, Kubernetes, Git, REST APIs, LLMs, OpenAI, RAG, Selenium, Gensim, Machin  
        **Data:** SQL, Postgres, Looker, Tableau, Excel, JSON, Power Query, MongoDB, Superset  
        **Business Systems:** Salesforce, NetSuite, JIRA, SharePointAPI, Revenue Recognition (ASC 606), Confluence  
        **Other:** MCP Agents, Master Excel Modeling, Automation, NLP, Custom GPT Agents, Google Cloud, VM Instances, Ngnix, VIM, Linux
        """)

        # Experience
        st.markdown("## EXPERIENCE")

        st.markdown("""
        ### **Roku Inc.** – *Senior Manager, Ad Revenue Operations (Solutions Engineering)*  
        **New York, NY | 2021 – Present**  
        - Built 3 full-stack internal platforms saving ~$5M/year and protected team headcount during layoffs  
        - Built AI agent assistant with vector search, NLP, Sharepoint, Slack & Confluence API integrations  
        - Architected Roku’s Ad Revenue Platform (8+ yrs active), oversaw rebuild with 1 PM & 7 engineers  
        - Created Publisher Revenue Share System, saving $2M/year for 5+ years

        ---

        ### **Roku Inc.** – *Ad Revenue Operations Manager*  
        **Los Gatos, CA | 2018 – 2021**  
        - Automated ASC 606 models, reducing manual effort by 25+ hrs/month  
        - Built ETL pipelines, cutting reconciliation time by 30+ hrs/month  
        - Streamlined campaign creation with Power Query + Python automation

        ---

        ### **Roku Inc.** – *Revenue Analyst*  
        **Los Gatos, CA | 2016 – 2018**  
        - Optimized Excel models to save 20+ hrs/month  
        - Led internal tool development and system integration

        ---

        ### **Daily.Jobs** – *Software Engineer*  
        **San Jose, CA | 2017 – 2020**  
        - Built NLP resume parser with Gensim  
        - Built scrapers & indexing systems via Selenium

        ---

        ### **RocketFuel Inc.** – *Revenue Analyst*  
        **Redwood City, CA | 2014 – 2016**  
        - Managed internal revenue tools and dashboards  
        - Reviewed contracts, ensured SOX compliance

        ---

        ### **EverView** – *Financial Analyst*  
        **Monterey, CA | 2013 – 2014**  
        - Created strategic revenue forecasts based on market data

        ---

        ### **Peach’s Restaurant** – *Operations Manager*  
        **North Conway, NH | 2013**  
        - Managed 10-person team, handled accounting, operations, cost-efficiency

        ---

        ### **Bank of New York Mellon** – *Derivatives Operations Specialist*  
        **Pittsburgh, PA | 2012**  
        - Settled complex derivatives, handled multi-currency operations
        """)

        # Education
        st.markdown("## EDUCATION")
        st.markdown("""
        **Duquesne University** – *BS in Business Finance*  
        _Pittsburgh, PA | 2011_  
        **Study Abroad:** ICN Business School – Nancy, France  
        **Coursework:** Derivatives, Financial Engineering, Systems Analysis, Statistical Math
        """)

        # Projects & Learning
        st.markdown("## PROJECTS & LEARNING")
        st.markdown("""
        - 🌐 [Divergent-Thinkers.com/stefan](https://divergent-thinkers.com/stefan): Conversational AI agent trained on myself  
        - 🌐 [QuantQueen.com/LiveBot](https://quantqueen.com/LiveBot): AI Portfolio Manager / Trading Engine  
        - 💻 [GitHub](https://github.com/nafets33)  
        - 🧠 Certifications & Courses: CS50x, Codecademy Python, GPT Tooling, StackOverflow MVP 🌟  
        - 🛠️ Self-taught in: NLP, LLMs, Confluence AI Agents, API Integrations, AdTech Systems
        """)


    with selected_audio_file.container():
        audio_path = st.selectbox("Select Audio File", [os.path.basename(file[0]) for file in audio_files])
    # st.write(master_text_audio[-1])
    # st.write([i for i in st.session_state])
    # st.write(st.session_state['conversation_history.json'])
    response=requests.get(f"{st.session_state['ip_address']}/api/data/{audio_path}")
    with llm_audio.container():
        # st.info(kw)
        st.audio(response.content, format="audio/mp3")  



    if client_user == 'stefanstapinski@gmail.com':
        with st.sidebar:
            st.write("Admin Only")
            st.write(st.session_state)
if __name__ == '__main__':
    all_page_auth_signin(True)
    st.session_state['ozz_guest'] = 'Stefan'
    ozz()

