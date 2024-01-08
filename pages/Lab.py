import streamlit as st
import os
from bs4 import BeautifulSoup
import re
from master_ozz.utils import return_app_ip, ozz_master_root, set_streamlit_page_config_once, sign_in_client_user, print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv


def lab():
    main_root = ozz_master_root()  # os.getcwd()
    load_dotenv(os.path.join(main_root, ".env"))
    set_streamlit_page_config_once()
    
    ip_address, streamlit_ip = return_app_ip()
    print(ip_address)

    if not sign_in_client_user():
        st.stop()

    client_user = st.session_state['client_user']

    constants = init_constants()
    DATA_PATH = constants.get('DATA_PATH')
    PERSIST_PATH = constants.get('PERSIST_PATH')


    with st.sidebar:
    # with ozz_lab_lab:
        files = st.sidebar.file_uploader('Upload your files',type=['PDF','CSV','MD','DOCX','DOC','XLSX','PY','HTML', 'TXT'],accept_multiple_files=True)
        
        # Store all the files
        if not os.path.exists(DATA_PATH):
                os.mkdir(DATA_PATH)

        # Iterating over files and saving it 
        for file in files:
            if file is not None:
                with open(os.path.join(DATA_PATH, file.name), 'wb') as f:
                    f.write(file.read())
                # st.write(f"Saved {file.name}")

        # Training the files or creating embeddings and storing in vector dbs

        # Predefined options for the select box
        predefined_options = os.listdir(PERSIST_PATH)

        # Text input for custom value
        custom_value = st.text_input("Enter custom value:")
        if custom_value not in predefined_options:
            predefined_options.append(custom_value)

        # Select box with predefined options
        db_name = st.selectbox("Select DB", predefined_options)

        if files is not None:
            if st.sidebar.button('Train'):
                with st.sidebar.status("Training Model..."):
                    load_files = Directory(DATA_PATH)
                    # clean data WORKERBEE
                    # load_files = clean_data(data)
                    chunks = CreateChunks(load_files)
                    embeddings = CreateEmbeddings(chunks, os.path.join(PERSIST_PATH, db_name))
                    st.info("EMBEDDING Created", db_name)


    # Show all the uploaded files
    file_names = [name for name in os.listdir(DATA_PATH) if os.path.isfile(os.path.join(DATA_PATH, name))]
    if not file_names:
        st.write('You have no files uploaded.')
    else:
        selected_file = st.sidebar.selectbox(label="Uploaded Files", options=file_names)

    # Chat Interface
    db_names = os.listdir(PERSIST_PATH)
    db_name = st.selectbox("Chat with DB: ", db_names)
    query = st.chat_input(placeholder="Enter your query")
    if query is not None:
        with st.chat_message('user'):
            st.write(query)

        # Exception or error handling of response
        try:
            if query:
                with st.spinner("Searching..."):
                    Retriever_db = os.path.join(PERSIST_PATH, db_name)
                    response = Retriever(query, Retriever_db)

            with st.chat_message('ai'):
                query = response["query"]
                result = response["result"]
                source_documents = response.get("source_documents")

                st.write(result)
                st.markdown("###### Here are top 3 search results",unsafe_allow_html=True)
                for index, document in enumerate(source_documents):
                    with st.status(f"Document {index+1}"):
                        page_content = document.page_content
                        formatted_content = ' '.join(line.strip() for line in page_content.split('\n'))
                        metadata = document.metadata
                        if 'page' in metadata:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n
                                        Page Number: {metadata['page']+1}""",unsafe_allow_html=True)
                        elif 'row' in metadata:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n
                                        Row Number: {metadata['row']+1}""",unsafe_allow_html=True)
                        else:
                            st.markdown(f""" > Content: <br><hr>
                                        {formatted_content} <br><hr>
                                        Source Document: {metadata['source']} \n""",unsafe_allow_html=True)
        except Exception as e:
            with st.chat_message('ai'):
                st.write('There are some problems with your docs or something went wrong :(')
                print_line_of_error(e)
if __name__ == '__main__':
    lab()