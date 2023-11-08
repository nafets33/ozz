from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv
import os
import openai

load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')



# Function to fetch the answers from FAISS vector db 
def Retriever(query : str, persist_directory : str):
    embeddings = OpenAIEmbeddings()
    # memory = ConversationBufferMemory()
    # embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = FAISS.load_local(persist_directory,embeddings=embeddings)
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 3})

    # For OpenAI ChatGPT Model
    qa_chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(model='gpt-3.5-turbo-16k',max_tokens=10000), chain_type='stuff', retriever=retriever, return_source_documents=True)

    result = qa_chain({"query": query})
    return result


def MergeIndexes(db_locations : list, new_location : str = None):
    embeddings = OpenAIEmbeddings()
    """taking first database for merging all the databases
        so that we can return a single database after merging"""
    

    dbPrimary = FAISS.load_local(db_locations[0],embeddings=embeddings)
    for db_location in db_locations:
        if db_location == db_locations[0]:
            # if again we got first database then we skip it as we already have marked it as primary
            continue
        dbSecondary = FAISS.load_local(db_location,embeddings=embeddings)
        dbPrimary.merge_from(dbSecondary)

    # Return the merged database or we can store it as new db name as well 
    dbPrimary.save_local(new_location)  # Location where we have to save the merged database  
    # return dbPrimary.docstore._dict    # For priting the output
    return dbPrimary    # Will return a vector object


# Testing purpose
if __name__ == '__main__':
    ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
    PERSIST_PATH = f"{ROOT_PATH}/STORAGE"
    PERSIST_PATH_list = [PERSIST_PATH+"/db1",PERSIST_PATH+"/db2",PERSIST_PATH+"/ozz.py",PERSIST_PATH+"/README.md",PERSIST_PATH+"/llama_ozz_app.py"]
    print(MergeIndexes(PERSIST_PATH_list,PERSIST_PATH+"/newDB"))
    # print(PERSIST_PATH_list)