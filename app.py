# app.py

import os
from google.genai import types
import io
from dotenv import load_dotenv
from google.genai.types import HttpOptions, Part
import PyPDF2

load_dotenv()

import streamlit as st
from google import genai  
from google.genai import types


def get_pdf_text(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(pdf_bytes)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()


# Configure Streamlit page
st.set_page_config(page_title="Generic ChatBot", layout="centered")
st.title("Generic Chatbot")
st.subheader("Generic Chatbot for your generic questions")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm your ChatBot helper. How can I help you today?"
        }
    ]

def display_messages():
    """Display all messages in the chat history"""
    for msg in st.session_state.messages:
        author = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(author):
            st.write(msg["content"])

def friendly_wrap(raw_text):
    """Add a friendly tone to AI responses"""
    return (
        "Great question! 🌱\n\n"
        f"{raw_text.strip()}\n\n"
        "Would you like me to elaborate on any part of this, or do you have other healthcare domain questions?"
    )

# Display existing messages
display_messages()

# Handle new user input
prompt = st.chat_input(
    "Enter your questions here...",
    accept_file=True,
    file_type=["txt", "pdf"]
    )

if prompt is not None and prompt.text != "" and (prompt.files is None or len(prompt.files) == 0):    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt.text})

    # Show user message
    with st.chat_message("user"):
        st.write(prompt.text)

    # Show thinking indicator while processing
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("🤔 Thinking...")

        # Call Gemini API
        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents={prompt.text},
                config=types.GenerateContentConfig(
                        system_instruction="You are a helpful assistant that provides clear and concise answers to user questions about Healthcare topics with no more than 10 points",),
            )
        
            # Extract response text
            answer = response.text
            friendly_answer = friendly_wrap(answer)

        except Exception as e:
            friendly_answer = f"I'm sorry, I encountered an error: {e}. Please try asking your question again."

        # Replace thinking indicator with actual response
        placeholder.write(friendly_answer)

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": friendly_answer})

    # Refresh the page to show updated chat
    st.rerun()

#write code to read pdf file and upload to gemini API for question answering
if prompt is not None and prompt.files is not None:
    st.write("Processing uploaded files...")
    # Loop through uploaded files and send it to Gemini API
    for uploaded_file in prompt.files:
        if uploaded_file.type == "application/pdf":
            file_content = uploaded_file.read()
            # Here you would typically send the file_content to the Gemini API for processing
            st.write(f"Uploaded file: {uploaded_file} (PDF content length: {len(file_content)} bytes)")
            
            with st.chat_message("assistant"):
             placeholder = st.empty()
             placeholder.write("🤔 Thinking...")

             pdf_text = get_pdf_text(uploaded_file)

            # st.write(pdf_text)
            
            #llmprompt = "Summarize the healthcare industry contents in different categories in points wise"
            MODEL="gemini-2.5-flash"
            
            response = client.models.generate_content(
                model=MODEL,
                contents=pdf_text,
                config=types.GenerateContentConfig(
                        system_instruction=prompt.text)
            )
            st.write(response.text)
        else:
            st.write(f"Unsupported file type: {uploaded_file.type}. Please upload a PDF file.")

# End of app.py
  