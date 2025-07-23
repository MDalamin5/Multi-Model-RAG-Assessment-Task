# 🧠 Personalized Bengali RAG Tutor with Agentic Memory

This project implements a sophisticated, personalized AI tutor for Bengali literature. It leverages an **Agentic RAG (Retrieval-Augmented Generation)** architecture to provide accurate, context-aware, and personalized answers. The system features both short-term (conversational) and long-term (user profile) memory, allowing it to remember user details and past topics across different sessions.

The core of the system is an agent built with LangChain and LangGraph. This agent can reason about its steps, dynamically deciding whether to answer from a vectorized knowledge base or perform a web search if the initial context is insufficient. The entire system is served via a FastAPI backend and includes a user-friendly Streamlit interface for interaction.

## ✨ Key Features

*   **Agentic RAG Architecture:** The system uses a state machine (graph) to intelligently decide its course of action, including retrieving documents, grading their relevance, and falling back to web search.
*   **Long-Term Memory:** Remembers user-specific details like name, grade, and topics of interest across multiple sessions, creating a truly personalized learning experience.
*   **Short-Term Memory:** Maintains conversational context within a single session, allowing for natural follow-up questions.
*   **Dynamic Tool Use:** Automatically switches between a private knowledge base (Pinecone) and a public web search (Google Serper) to ensure the most relevant answers.
*   **Open-Source & Efficient:** Built with powerful open-source models like `llama3-8b-8192` (via Groq) and `sentence-transformers/all-mpnet-base-v2`.
*   **Production-Ready Stack:** Deployed with a FastAPI backend and a Streamlit frontend, demonstrating a full-stack application.
*   **Integrated Tracing:** Leverages LangSmith for full observability and debugging of the agent's reasoning process.
*   **Quantified Performance:** Includes a full evaluation suite to measure and prove the system's accuracy and relevance.

## 🏛️ System Architecture

The agent's logic is structured as a graph, where each node represents a step in the reasoning process. The agent dynamically traverses this graph based on the relevance of the retrieved information.

![System Architecture Graph](bangla-rag-agent/docs/images/system_architecture.png)

```mermaid
graph TD
    A[Start] --> B(retrieve);
    B --> C(grade_docs);
    C --"relevant_docs"--> E(generate);
    C --"not_relevant_docs"--> D(web_call);
    D --> E;
    E --> F(update_memory);
    F --> G[End];

    subgraph "Knowledge Base"
        B
    end
    subgraph "External Knowledge"
        D
    end
    subgraph "Reasoning & Generation"
        C
        E
    end
    subgraph "Memory"
        F
    end

<hr>

## 🛠️ Technology Stack & Tools
- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **LLM & Orchestration**: LangChain, LangGraph, LangSmith
- **LLM Provider:** Groq (for Llama 4)
- **Vector Database:** Pinecone
- **Embedding Model:** Hugging Face sentence-transformers/all-mpnet-base-v2
- **Web Search:** Google Serper API
- **Core Libraries:** python-dotenv, pydantic, trustcall


## 🚀 Setup and Installation Guide
Follow these steps to get the project running on your local machine.
1. Clone the Repository
```
Generated bash
git clone <your-repository-url>
cd <repository-name>
```