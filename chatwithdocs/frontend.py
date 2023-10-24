import streamlit as st
import os
from constants import DATA_PATH, PERSIST_PATH
from ingest import Directory, CreateChunks, CreateEmbeddings
from generate_answers import Retriever



st.set_page_config(page_title="QA-ChatBot")
st.title('QA-ChatBot')


with st.sidebar:
    files = st.sidebar.file_uploader('Upload your files',type=['PDF','CSV','MD','DOCX','DOC','XLSX','PY','HTML'],accept_multiple_files=True)
    
    # Store all the files
    if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)

    # Iterating over files and saving it 
    for file in files:
        if file is not None:
            with open(os.path.join(DATA_PATH, file.name), 'wb') as f:
                f.write(file.read())
            # st.write(f"Saved {file.name}")

    # Training the files or creating embeddings and storing in vector db
    if files is not None:
        if st.sidebar.button('Train'):
            with st.sidebar.status("Training Model..."):
                load_files = Directory(DATA_PATH)
                chunks = CreateChunks(load_files)
                embeddings = CreateEmbeddings(chunks,PERSIST_PATH)


# Show all the uploaded files
file_names = [name for name in os.listdir(DATA_PATH) if os.path.isfile(os.path.join(DATA_PATH, name))]
if not file_names:
    st.write('You have no files uploaded.')
else:
    selected_file = st.sidebar.selectbox(label="Uploaded Files", options=file_names)

# Chat Interface
query = st.chat_input(placeholder="Enter your query")
if query is not None:
    with st.chat_message('user'):
        st.write(query)

    # Exception or error handling of response
    try:
        if query:
            with st.spinner("Searching..."):
                response = Retriever(query, PERSIST_PATH)

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
    except Exception:
        with st.chat_message('ai'):
            st.write('There are some problems with your docs or something went wrong :(')