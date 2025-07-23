# app/main.py

import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from .agent_graph import get_graph, long_term_store  # <-- IMPORT THE MEMORY STORE

# Initialize FastAPI app
app = FastAPI(
    title="Bangla RAG Agent API",
    description="An API for interacting with a personalized RAG chatbot."
)

# Initialize the agent graph when the application starts
agent_graph = get_graph()

# --- API Request Models ---
class ChatRequest(BaseModel):
    query: str
    user_id: str
    thread_id: str

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint for health checks."""
    return {"status": "ok", "message": "Bangla RAG Agent API is running."}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Receives a user query and returns the agent's response."""
    config = {
        "configurable": {
            "user_id": request.user_id,
            "thread_id": request.thread_id
        }
    }
    input_message = {"messages": [HumanMessage(content=request.query)]}

    response = await agent_graph.ainvoke(input_message, config=config)
    final_message = response['messages'][-1].content
    
    return {"response": final_message}

@app.get("/memory/{user_id}")
def get_memory(user_id: str):
    """Retrieves the long-term memory profile for a given user."""
    namespace = ("memory", user_id)
    key = "student_profile"
    
    # Get the memory from the store
    memory_record = long_term_store.get(namespace, key)
    
    if memory_record:
        return {"user_id": user_id, "memory": memory_record.value}
    
    return {"user_id": user_id, "memory": None}