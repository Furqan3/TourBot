import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

load_dotenv()

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MONGO_URL = os.getenv('MONGODB_URL')
HF_TOKEN = os.getenv('hf')

embeddings = HuggingFaceEmbeddings(model_name=MODEL_ID, model_kwargs={"device": "cpu"})

def load_data(filename):
    with open(filename) as f:
        return json.load(f)

def remove_duplicates(data):
    return [dict(tupleized) for tupleized in set(tuple(item.items()) for item in data)]

def embed_documents(data):
    for item in tqdm(data):
        document = Document(page_content=item['description'])
        doc_embedding = embeddings.embed_documents([document.page_content])
        item['embedding'] = doc_embedding[0]
    return data

def insert_to_mongodb(data):
    try:
        client = MongoClient(MONGO_URL)
        db = client['Tour']
        collection = db['spots']
        collection.insert_many(data)
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
    finally:
        client.close()

def main():
    data = load_data('data.json')
    data = remove_duplicates(data)
    
    try:
        data = embed_documents(data)
    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return
    
    insert_to_mongodb(data)

if __name__ == "__main__":
    main()