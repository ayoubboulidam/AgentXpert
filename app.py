import os
from typing import Optional

import streamlit as st
from agent_initializer import initialize_grand_agent
from utils import handle_file_upload
from streamlit_chat import message

# App Header
st.header("AgentXpert")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "key_counter" not in st.session_state:
    st.session_state.key_counter = 0


def display_chat():
    """
    Displays the chat history in a chat-like format.
    """
    for chat in st.session_state.chat_history:
        key = f"msg_{st.session_state.key_counter}"
        st.session_state.key_counter += 1

        message(chat["text"], is_user=(chat["role"] == "User"), key=key)
        if chat.get("image"):
            st.image(chat["image"], caption="Generated Image", use_column_width=True)


def process_user_input(user_input: str, csv_file_path: Optional[str] = None):
    """
    Handles user input, processes it using the grand agent, and updates chat history.
    """
    try:
        grand_agent_executor = initialize_grand_agent(csv_file_path=csv_file_path)
        response = grand_agent_executor.invoke({"input": user_input})

        # Append user query and agent response to chat history
        st.session_state.chat_history.append({"role": "User", "text": user_input})
        st.session_state.chat_history.append(
            {"role": "Agent", "text": response.get("output", "I couldn't process that.")}
        )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# File upload for CSV
uploaded_file = st.file_uploader("Upload CSV file (if needed)", type="csv", label_visibility="collapsed")

# User input for chatbot
user_input = st.text_input("Enter your question:")

if st.button("Submit"):
    with st.spinner("Processing..."):
        file_path = handle_file_upload(uploaded_file) if uploaded_file else None
        process_user_input(user_input, csv_file_path=file_path)

    display_chat()
