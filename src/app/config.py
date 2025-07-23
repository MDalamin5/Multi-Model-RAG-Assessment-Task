import os
import warnings
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.utilities import GoogleSerperAPIWrapper
from pinecone import Pinecone

# Ignore warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# --- API Keys and Environment Setup ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Set environment variables for LangChain and other libraries
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_PROJECT"] = "Bangla RAG Agent"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["HF_TOKEN"] = HF_TOKEN
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY

# --- Model and Index Names ---
LLAMA_MODEL = os.getenv("LLAMA_MODEL")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

# --- Initialize Core Components (Singletons) ---

# Initialize LLM
llm = ChatGroq(model=LLAMA_MODEL)

# Initialize Embeddings
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# Initialize Retriever
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Initialize Web Search Tool
search_tool = GoogleSerperAPIWrapper()

print("✅ Core components initialized successfully.")