import streamlit as st
import os
from bs4 import BeautifulSoup

from master_ozz.utils import print_line_of_error, Directory, CreateChunks, CreateEmbeddings, Retriever, init_constants

st.set_page_config(page_title="QA-ChatBot")
st.title('QA-ChatBot')

constants = init_constants()
DATA_PATH = constants.get('DATA_PATH')
PERSIST_PATH = constants.get('PERSIST_PATH')

import re

def is_html(data):
    # Use BeautifulSoup to check if the data is HTML
    try:
        soup = BeautifulSoup(data, 'html.parser')
        return soup.html is not None
    except:
        return False

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text()
    return text_content

def clean_text(text):
    # Remove non-alphanumeric characters and extra whitespaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    cleaned_text = re.sub(' +', ' ', cleaned_text)  # Remove extra whitespaces
    return cleaned_text

def clean_data(data):
    if is_html(data):
        # If it's HTML, clean the HTML content first
        cleaned_text = clean_html(data)
        # Then, clean the text
        cleaned_text = clean_text(cleaned_text)
        return cleaned_text
    else:
        # If it's not HTML, just clean the text
        return clean_text(data)

# # Example usage
# html_data = "<p>Your HTML content goes here</p>"
# text_data = "This is a sample text without HTML tags."

# cleaned_data_html = clean_data(html_data)
# cleaned_data_text = clean_data(text_data)

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

    # Training the files or creating embeddings and storing in vector dbs

    # Predefined options for the select box
    predefined_options = os.listdir(PERSIST_PATH)

    # Text input for custom value
    custom_value = st.text_input("Enter custom value:")
    predefined_options.append(custom_value)

    # Select box with predefined options
    db_name = st.selectbox("Select from predefined options:", predefined_options)

    if files is not None:
        if st.sidebar.button('Train'):
            with st.sidebar.status("Training Model..."):
                load_files = Directory(DATA_PATH)
                # clean data WORKERBEE
                # load_files = clean_data(data)
                chunks = CreateChunks(load_files)
                embeddings = CreateEmbeddings(chunks, os.path.join(PERSIST_PATH, db_name))


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
                Retriever_db = os.path.join(PERSIST_PATH, "db1")
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