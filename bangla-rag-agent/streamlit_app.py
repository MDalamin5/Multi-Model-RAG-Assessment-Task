import streamlit as st
import requests
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="সহায়ক বাংলা শিক্ষক",
    page_icon="📚",
    layout="wide"
)

# --- API Endpoint ---
API_URL = "http://127.0.0.1:8000/chat"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    # Generate a unique user ID that persists across the browser session
    st.session_state.user_id = "student_" + str(uuid.uuid4())

# --- UI Components ---
st.title("📚 সহায়ক বাংলা শিক্ষক (Personalized Chatbot)")
st.markdown("আপনার প্রশ্ন জিজ্ঞাসা করুন। চ্যাটবটটি আপনার পূর্ববর্তী কথোপকথন মনে রাখবে।")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and API Interaction ---
if prompt := st.chat_input("আপনার প্রশ্নটি এখানে লিখুন..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display thinking indicator and call API
    with st.chat_message("assistant"):
        with st.spinner("চিন্তা করছি..."):
            try:
                # Generate a new thread ID for each message to mimic the notebook's behavior
                thread_id = "chat_session_" + str(uuid.uuid4())

                payload = {
                    "query": prompt,
                    "user_id": st.session_state.user_id,
                    "thread_id": thread_id
                }
                
                response = requests.post(API_URL, json=payload, timeout=120)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                bot_response = response.json().get("response", "দুঃখিত, একটি সমস্যা হয়েছে।")
                st.markdown(bot_response)
                
                # Add bot response to chat history
                st.session_state.messages.append({"role": "assistant", "content": bot_response})

            except requests.exceptions.RequestException as e:
                error_message = f"API এর সাথে সংযোগ করতে ব্যর্থ। অনুগ্রহ করে নিশ্চিত করুন যে FastAPI সার্ভারটি চলছে।\n\nError: {e}"
                st.error(error_message)