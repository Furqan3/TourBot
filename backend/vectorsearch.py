from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import certifi
ca = certifi.where()

load_dotenv()
mongo_token = os.getenv("MONGODB_URL")

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(model_name=MODEL_ID, model_kwargs={"device": "cpu"})


client = MongoClient(mongo_token, tlsCAFile=ca)
db = client['Tour']
collection = db['spots']

query = "tell me best spots in karachi"
document = Document(page_content=query)
doc_embedding = embeddings.embed_documents([document.page_content])


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

  
except Exception as e:
    print(f"An error occurred during vector search: {e}")

for i in list(result):
        print(f'Name: {i["name"]},  Description: {i["description"]}')


