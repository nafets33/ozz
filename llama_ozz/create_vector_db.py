from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.document_loaders import UnstructuredHTMLLoader, BSHTMLLoader

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os
import pandas as pd

DATA_PATH="data/"
DB_FAISS_PATH = "vectorstores/db_fiass/"

def create_vector_db(filename = "C:/Users/hp/Desktop/Viral Square/Stephan/largeDataset/pollen/ozz/fake_job_postings.csv", save=False):
    # Handle File types
    documents = []
    # sure format
    
    if filename.endswith(".csv") or filename.endswith(".txt"):
        df = pd.read_csv(filename, engine='python', on_bad_lines='skip')
        if 'description' not in df.columns.tolist():
            # process handle into dataframe
            pass
            
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