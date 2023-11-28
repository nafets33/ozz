import os

# Directory where files will be stored, vector db will be stored
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = f"{ROOT_PATH}/DATA"
PERSIST_PATH = f"{ROOT_PATH}/STORAGE"

# EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"