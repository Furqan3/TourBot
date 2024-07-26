from groq import Groq
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

def load_environment():
    load_dotenv()
    mongo_token = os.getenv("MONGODB_URL")
    groq_api_key = os.getenv("GROQ_API_KEY")
    return mongo_token, groq_api_key

def setup_embeddings():
    MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    return HuggingFaceEmbeddings(model_name=MODEL_ID, model_kwargs={"device": "cpu"})

def connect_to_mongodb(mongo_token):
    client = MongoClient(mongo_token)
    db = client['Tour']
    return db['spots']

def perform_vector_search(collection, doc_embedding):
    try:
        result = collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": doc_embedding[0],
                    "path": "embedding",  
                    "numCandidates": 1000,
                    "limit": 5,
                    "index": "vectorsearch"
                }
            }
        ])
        return list(result)
    except Exception as e:
        print(f"An error occurred during vector search: {e}")
        return []

def generate_groq_response(query, groq_api_key):
    client = Groq(api_key=groq_api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def main():
    mongo_token, groq_api_key = load_environment()
    embeddings = setup_embeddings()
    collection = connect_to_mongodb(mongo_token)

    query = input("Enter your query: ")
    document = Document(page_content=query)
    doc_embedding = embeddings.embed_documents([document.page_content])

    search_results = perform_vector_search(collection, doc_embedding)

    context = query
    for i in search_results:
        context += f'\nName: {i["name"]}, Description: {i["description"]}'

    response = generate_groq_response(context, groq_api_key)
    print("Groq Response:")
    print(response)

if __name__ == "__main__":
    main()