import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from .agent_graph import get_graph

# Initialize FastAPI app
app = FastAPI(
    title="Bangla RAG Agent API",
    description="An API for interacting with a personalized RAG chatbot."
)

# Initialize the agent graph when the application starts
agent_graph = get_graph()

# Define the request body model
class ChatRequest(BaseModel):
    query: str
    user_id: str
    thread_id: str # A unique ID for each conversation turn

# Define the API endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Receives a user query and returns the agent's response.
    """
    # Configuration for the graph invocation
    config = {
        "configurable": {
            "user_id": request.user_id,
            "thread_id": request.thread_id
        }
    }
    
    # Prepare the input for the graph
    input_message = {"messages": [HumanMessage(content=request.query)]}

    # Asynchronously invoke the graph
    response = await agent_graph.ainvoke(input_message, config=config)
    
    # Extract the final AI message
    final_message = response['messages'][-1].content
    
    return {"response": final_message}

# Optional: Add a root endpoint for health checks
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bangla RAG Agent API is running."}