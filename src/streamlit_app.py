# streamlit_app.py

import streamlit as st
import requests
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="সহায়ক বাংলা শিক্ষক",
    page_icon="📚",
    layout="wide"
)

# --- API Endpoints ---
BASE_API_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_API_URL}/chat"
MEMORY_URL = f"{BASE_API_URL}/memory"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "student_" + str(uuid.uuid4())

# --- Sidebar to Display Long-Term Memory ---
def display_memory_sidebar():
    """Fetches and displays the user's long-term memory in the sidebar."""
    st.sidebar.title("🧠 Long-Term Memory")
    st.sidebar.markdown(f"**User ID:** `{st.session_state.user_id}`")
    
    try:
        # Fetch memory from the API
        response = requests.get(f"{MEMORY_URL}/{st.session_state.user_id}", timeout=10)
        response.raise_for_status()
        memory_data = response.json().get("memory")

        if memory_data:
            st.sidebar.write("Current student profile:")
            st.sidebar.json(memory_data)
        else:
            st.sidebar.info("No memory has been stored for this user yet. Start the conversation to build a profile!")
    
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Could not connect to the memory API.\n\nError: {e}")

# --- Main App ---
st.title("📚 সহায়ক বাংলা শিক্ষক (Personalized Chatbot)")
st.markdown("আপনার প্রশ্ন জিজ্ঞাসা করুন। চ্যাটবটটি আপনার পূর্ববর্তী কথোপকথন মনে রাখবে। সাইডবারে দেখুন কিভাবে স্মৃতি তৈরি হচ্ছে।")

# Call the function to display the sidebar on every app rerun
display_memory_sidebar()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and API Interaction ---
if prompt := st.chat_input("আপনার প্রশ্নটি এখানে লিখুন..."):
    # Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display thinking indicator and call API
    with st.chat_message("assistant"):
        with st.spinner("চিন্তা করছি..."):
            try:
                # Generate a new thread ID for each message
                thread_id = "chat_session_" + str(uuid.uuid4())
                payload = {"query": prompt, "user_id": st.session_state.user_id, "thread_id": thread_id}
                
                response = requests.post(CHAT_URL, json=payload, timeout=120)
                response.raise_for_status()
                
                bot_response = response.json().get("response", "দুঃখিত, একটি সমস্যা হয়েছে।")
                st.markdown(bot_response)
                
                # Add bot response to history
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                
                # Force a rerun to update the sidebar with the latest memory
                st.rerun()

            except requests.exceptions.RequestException as e:
                error_message = f"API এর সাথে সংযোগ করতে ব্যর্থ। অনুগ্রহ করে নিশ্চিত করুন যে FastAPI সার্ভারটি চলছে।\n\nError: {e}"
                st.error(error_message)