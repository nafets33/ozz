from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.document_loaders import UnstructuredHTMLLoader, BSHTMLLoader, DataFrameLoader

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os
import pandas as pd

DATA_PATH="data/"
DB_FAISS_PATH = "vectorstores/db_fiass/"

def create_vector_db(filename = "ozz/ozz/Learning walks data.txt'", save=True):
    # Handle File types
    # documents = []
    df = pd.read_csv(filename)
    loader = DataFrameLoader(df, page_content_column="contents")
    documents = loader.load()
            
    # sent.Analyzer
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts=text_splitter.split_documents(documents)

    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device':'cpu'})
    db=FAISS.from_documents(texts,embeddings)
    
    if save:
        db.save_local(DB_FAISS_PATH)
    
    return db

if __name__=="__main__":
    create_vector_db()