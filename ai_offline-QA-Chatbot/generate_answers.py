from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv

load_dotenv('.env')


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
