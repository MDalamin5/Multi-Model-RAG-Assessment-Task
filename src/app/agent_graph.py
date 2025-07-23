from langgraph.graph import StateGraph, START, END
from langgraph.store.base import BaseStore
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from trustcall import create_extractor

# Import shared components and schemas
from .config import llm, retriever, search_tool
from .schemas import GraphState, StudentProfile, Grade

# --- Define the long-term memory store at the module level ---
# This makes it a singleton that can be imported and accessed by other modules (like main.py)
long_term_store = InMemoryStore()

# --- Memory Extractor ---
memory_extractor = create_extractor(
    llm,
    tools=[StudentProfile],
    tool_choice="StudentProfile",
)

# --- Utility Functions ---
def format_docs(retriever_docs):
    return "\n\n".join(doc.page_content for doc in retriever_docs)

# --- Graph Nodes (No changes here, keeping them the same) ---

def retrieve_node(state: GraphState):
    """Retrieves documents from the vector store based on the latest user question."""
    print("---NODE: RETRIEVE DOCUMENTS---")
    question = state["messages"][-1].content
    retrieved_docs = retriever.invoke(question)
    print(f"Retrieved {len(retrieved_docs)} docs.")
    return {"docs": retrieved_docs}

def grade_document_node(state: GraphState):
    """Grades the retrieved documents for relevance to the user's question."""
    print("---NODE: GRADE DOCUMENTS---")
    question = state["messages"][-1].content
    context = state["docs"]
    
    system_msg = f"""Your task is to check if the retrieved context is relevant to the user's question. 
Can the question be answered using this context? If relevant, say 'yes', otherwise say 'no'.
Question: {question}
Context: {context}
Carefully analyze the context and question and produce the output based on the required schema."""
    
    llm_with_tool = llm.with_structured_output(Grade)
    response = llm_with_tool.invoke([SystemMessage(content=system_msg)])
    print(f"Document Grade: {response.binary_output}")
    return {"grade": response.binary_output}

def search_on_web_node(state: GraphState):
    """Performs a web search if the retrieved documents are not relevant."""
    print("---NODE: WEB SEARCH---")
    question = state["messages"][-1].content
    src_result = search_tool.run(question)
    print("---WEB SEARCH COMPLETE---")
    return {"src_docs": str(src_result)}

def generate_node(state: GraphState, config: dict, store: BaseStore):
    """Generates a response using LLM, context, and long-term memory."""
    print("---NODE: GENERATE RESPONSE---")
    question = state["messages"][-1].content
    context_source = ""

    if state.get("src_docs"):
        print("--- Using context from Web Search ---")
        context_source = state["src_docs"]
    else:
        print("--- Using context from Retriever ---")
        context_source = format_docs(state["docs"])

    user_id = config["configurable"]["user_id"]
    namespace = ("memory", user_id)
    existing_memory = store.get(namespace, "student_profile")
    
    if existing_memory and existing_memory.value:
        memory_dict = existing_memory.value
        formatted_memory = (
            f"ছাত্রের নাম: {memory_dict.get('user_name', 'অজানা')}\n"
            f"ছাত্রের শ্রেণি: {memory_dict.get('grade_or_class', 'অজানা')}\n"
            f"আগ্রহের বিষয়: {', '.join(memory_dict.get('topics_of_interest', ['কিছুই না']))}"
        )
    else:
        formatted_memory = "এই ছাত্রের জন্য কোনো স্মৃতি এখনো জমা হয়নি।"
    print(f"Loaded Memory: {formatted_memory}")

    
    rag_with_memory_prompt = PromptTemplate(
    template=(
        "You are a helpful and personalized assistant. Your task is to answer the user's question by combining information from the 'Context' and your 'User Memory'.\n\n"
        "First, identify the language of the user's 'Question'. "
        "Then, provide your answer in the SAME language as the question (either English or Bengali), personalizing it with details from the 'User Memory' if relevant.\n\n"

        "**Rules:**\n"
        "1. If the 'Question' is in Bengali, your 'Answer' MUST be in Bengali.\n"
        "2. If the 'Question' is in English, your 'Answer' MUST be in English.\n"
        "3. If the answer is not found in the 'Context', you must politely state that you don't have enough information. In Bengali say: 'দুঃখিত, উত্তর দেওয়ার মতো পর্যাপ্ত তথ্য আমার কাছে নেই।' In English say: 'Sorry, I do not have enough information to answer that.'\n"
        "4. Do not make up any information that is not in the context or memory.\n\n"

        "--- START OF USER MEMORY ---\n"
        "{memory}\n"
        "--- END OF USER MEMORY ---\n\n"

        "--- START OF CONTEXT ---\n"
        "{context}\n"
        "--- END OF CONTEXT ---\n\n"

        "Question:\n{question}\n\n"

        "Answer (personalized and in the same language as the question):"
    ),
    input_variables=["question", "context", "memory"],
)

    
    

    rag_chain = rag_with_memory_prompt | llm | StrOutputParser()
    
    response = rag_chain.invoke({
        "context": context_source,
        "question": question,
        "memory": formatted_memory
    })
    print(f"Generated Response: {response}")
    return {"messages": [AIMessage(content=response)]}

def update_memory_node(state: GraphState, config: dict, store: BaseStore):
    """Updates the student's profile in the long-term memory store."""
    print("---NODE: UPDATE MEMORY---")
    user_id = config["configurable"]["user_id"]
    namespace = ("memory", user_id)
    
    # --- CRITICAL CHANGE HERE ---
    # We only need the user's latest message to extract information.
    # The AI's previous long answer confuses the extractor.
    last_user_message = state["messages"][-2] # The message before the last AI response
    
    # We also get the existing memory to update it, not overwrite it.
    existing_memory_record = store.get(namespace, "student_profile")
    existing_profile = {"StudentProfile": existing_memory_record.value} if existing_memory_record else None

    extraction_instruction = (
        "Based on the user's message, extract or update the student's profile. "
        "If an existing profile is provided, merge the new information into it. "
        "Crucially, all extracted text for 'topics_of_interest' and 'last_topic_discussed' MUST be in the Bengali (Bangla) language."
    )
    
    # Invoke the extractor with a cleaner, more focused context.
    # We pass the instruction, the user's message, and the existing profile to update.
    result = memory_extractor.invoke({
        "messages": [
            SystemMessage(content=extraction_instruction),
            last_user_message
        ],
        "existing": existing_profile
    })
    
    if result.get("responses"):
        # The extractor now correctly uses the 'patch' operation
        updated_profile = result["responses"][0]
        
        # Check if the response is a dictionary (from model_dump) or already a patch object
        if hasattr(updated_profile, 'model_dump'):
             profile_to_save = updated_profile.model_dump()
        else: # It might be a patch object from trustcall
             profile_to_save = updated_profile

        print(f"Updated Profile to save: {profile_to_save}")
        store.put(namespace, "student_profile", profile_to_save)
    else:
        print("No new profile information found to update.")
    return

def route_node(state: GraphState):
    """Decides whether to use retrieved docs or perform a web search."""
    print("---NODE: ROUTING---")
    if state['grade'] == 'yes':
        print("Decision: Documents are relevant. Generating response.")
        return "relevant_docs"
    else:
        print("Decision: Documents not relevant. Performing web search.")
        return "not_relevant_docs"

# --- Graph Builder ---
def get_graph():
    """Builds and compiles the LangGraph agent."""
    checkpointer = MemorySaver()
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("grade_docs", grade_document_node)
    builder.add_node("web_call", search_on_web_node)
    builder.add_node("generate", generate_node)
    builder.add_node("update_memory", update_memory_node)

    # Add edges
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade_docs")
    builder.add_conditional_edges(
        "grade_docs",
        route_node,
        {"relevant_docs": "generate", "not_relevant_docs": "web_call"},
    )
    builder.add_edge("web_call", "generate")
    builder.add_edge("generate", "update_memory")
    builder.add_edge("update_memory", END)

    # Use the module-level long_term_store when compiling
    graph = builder.compile(checkpointer=checkpointer, store=long_term_store)
    print("✅ Agent graph compiled successfully.")
    return graph