import os
from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
 
load_dotenv('.env')




def generate_image_embeddings(images: List[str]) -> List[List[float]]:
    embeddings = []
    persist_directory = '/STORAGE/db3/'
    openai_embeddings = OpenAIEmbeddings()
    for image in images:
        # Load image data
        image_data = open(image, 'rb').read()

        # Generate embedding using OpenAI
        embedding = openai_embeddings.encode_image(image_data)

        # Store embedding in vector store (optional)
        vector_store = FAISS.from_embeddings(documents=embedding, embedding=openai_embeddings)
        vector_store.save_local(persist_directory)
        embeddings.append(embedding)

    return embeddings


def chat_with_images(messages: List[str], images: List[str]) -> List[str]:
    # Generate image embeddings
    image_embeddings = generate_image_embeddings(images)
    openai_embeddings = OpenAIEmbeddings()
    persist_directory = '/STORAGE/db3/'
    
    # Initialize conversational retrieval chain
    conversational_chain = ConversationalRetrievalChain(
        embedding_extractor=openai_embeddings,
        vector_store=FAISS.load_local(persist_directory,embeddings=openai_embeddings),
        chat_model=ChatOpenAI(model='text-davinci-003')
    )

    # Process messages and generate responses
    responses = []
    for message, embedding in zip(messages, image_embeddings):
        response = conversational_chain.process(message, embedding)
        responses.append(response)

    return responses


# Driver code
def main():
    # Example images locations
    images = ['master_ozz/test_images/macbook_test_image.jpg', 'master_ozz/test_image/orange_test_image.jpg', 'master_ozz/test_image/test_image.jpg']

    # Example messages
    messages = ['What do you think of this image?', 'What is this object?', 'Can you describe this scene?']

    # Generate responses
    responses = chat_with_images(messages, images)
    print(responses)


main()