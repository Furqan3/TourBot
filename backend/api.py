from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import certifi

ca = certifi.where()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
mongo_token = os.getenv("MONGODB_URL")
groq_api_key = os.getenv("GROQ_API_KEY")

# Setup embeddings
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=MODEL_ID, model_kwargs={"device": "cpu"})

# Connect to MongoDB
client = MongoClient(mongo_token, tlsCAFile=ca)
db = client['Tour']
collection = db['spots']

class ChatInput(BaseModel):
    query: str

def perform_vector_search(doc_embedding):
    try:
        result = collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": doc_embedding[0],
                    "path": "embedding",  
                    "numCandidates": 1000,
                    "limit": 3,
                    "index": "vectorsearch"
                }
            }
        ])
        return list(result)
    except Exception as e:
        print(f"An error occurred during vector search: {e}")
        return []

def generate_groq_response(prompt, system_message):
    client = Groq(api_key=groq_api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def is_tourist_spot_query(query):
    tourist_keywords = ["tourist", "spot", "place", "visit", "attraction", "sightseeing", "tour", "destination", "landmark", "site"]
    return any(keyword in query.lower() for keyword in tourist_keywords)

@app.post("/chat")
async def chat(chat_input: ChatInput):
    query = chat_input.query

    if is_tourist_spot_query(query):
        # Improve the query
        improve_query_prompt = f"Refine this tourist spot query: {query}"
        improve_query_system = "Extract the main spot"
        improved_query = generate_groq_response(improve_query_prompt, improve_query_system)

        # Perform vector search
        document = Document(page_content=improved_query)
        doc_embedding = embeddings.embed_documents([document.page_content])
        search_results = perform_vector_search(doc_embedding)

        # Generate response based on search results
        context = "\n".join([f"Name: {result['name']}\nDescription: {result['description']}" for result in search_results])
        
        final_prompt = f"""User Query: {query}
        Improved Query: {improved_query}
        Context (Top 3 Tourist Spots):
        {context}

        Provide a brief, relevant response recommending 1-2 spots in Pakistan based on the query. For each, give a short description and one key reason to visit. If no good match, suggest how to refine the search."""

        system_message = "You are a concise tour guide assistant. Give short and simple, relevant recommendations based on the provided information. and the give the response in a good way. don't give extra irrevilent details"
    else:
        # For non-tourist queries, use a general conversation prompt
        final_prompt = f"User Query: {query}\n\nProvide a brief, friendly response to this general query:"
        system_message = "You are a Tour Spot AI assistant. Give concise, helpful answers to Answer about tour spots in Pakistan"

    response = generate_groq_response(final_prompt, system_message)
    return {"response": response}

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
