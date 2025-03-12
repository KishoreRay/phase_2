import streamlit as st
from rephraser_llm import rephraser
import os
from PIL import Image
import pymupdf  # PyMuPDF for PDF handling
import pandas as pd
import subprocess
from sync import syncer

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_paths' not in st.session_state:
        st.session_state.file_paths = []

def open_file(file_path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS/Linux
            subprocess.run(['xdg-open', file_path], check=True)
    except Exception as e:
        st.error(f"Could not open file: {str(e)}")

def display_file_preview(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    with st.sidebar.container():
        st.markdown(f"### {os.path.basename(file_path)}")
        
        if file_ext in ['.jpg', '.jpeg', '.png']:
            image = Image.open(file_path)
            st.image(image, caption=os.path.basename(file_path), use_column_width=True)
        elif file_ext == '.pdf':
            try:
                pdf_document = pymupdf.open(file_path)
                first_page = pdf_document[0]
                image = first_page.get_pixmap()
                image_path = "temp_preview.png"
                image.save(image_path)
                st.image(image_path, caption=f"Preview of {os.path.basename(file_path)}", use_column_width=True)
                os.remove(image_path)
                pdf_document.close()
            except Exception as e:
                st.error(f"Error previewing PDF: {str(e)}")
        elif file_ext in ['.mp4', '.avi', '.mov']:
            st.video(file_path)
        elif file_ext in ['.mp3', '.wav', '.ogg']:
            st.audio(file_path)
        elif file_ext in ['.txt', '.md']:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                st.text_area("Text Preview", content, height=200)
        elif file_ext in ['.py', '.cpp', '.java', '.js', '.html', '.css', '.json', '.xml']:
            with open(file_path, "r", encoding="utf-8") as file:
                code = file.read()
                st.code(code, language=file_ext[1:])
        else:
            st.write("Preview not available for this file type.")
        
        if st.button(f"Open {os.path.basename(file_path)}", key=file_path):
            open_file(file_path)

def main():
    st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
    
    st.markdown(
        """
        <style>
        body {background-color: #0d0d0d;}
        .stApp {background-color: #100f0f; color: white;}
        .chat-container {max-width: 800px; margin: auto;}
        .chat-message {padding: 15px; border-radius: 10px; margin-bottom: 10px;}
        .user-message {background-color: #444; text-align: left;}
        .bot-message {background-color: #007bff; color: white; text-align: right;}
        .input-container {position: fixed; bottom: 0; left: 0; right: 0; background: #1a1a1a; padding: 10px;}
        .input-box {width: 100%; padding: 10px; border-radius: 5px;}
        .send-button {background: none; border: none; color: #007bff; font-size: 20px; cursor: pointer;}
        .sidebar .sidebar-content {background-color: #141414; padding: 20px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()
    st.sidebar.header("Sources")

        # Add Sync button to the top right corner
    if st.sidebar.button("🔄 Sync"):
        SCAN_DRIVES = ["E:\\new_file_test"]  # Update with actual paths to scan
        syncer(SCAN_DRIVES)
        st.experimental_rerun()
    
    chat_col, sidebar_col = st.columns([6, 2])
    
    with chat_col:
        st.title("💬Chat")
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            role_class = "user-message" if message["role"] == "user" else "bot-message"
            st.markdown(f"<div class='chat-message {role_class}'>{message['content']}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with sidebar_col:
        st.subheader("Suggested Queries")
        suggestions = [
            "find my resume?",
            "where the documents related IEEE papers?",
            "How many IEEE papers do i have related to LLM",
            "Search for the images i took with my friends in theme park"
        ]
        for suggestion in suggestions:
            if st.button(suggestion):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                result2, response = rephraser(suggestion)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Extract file paths and update session state
                st.session_state.file_paths = [row['file_path'] for row in result2 if 'file_path' in row]
                st.experimental_rerun()
        
        
        for file_path in st.session_state.file_paths:
            display_file_preview(file_path)
    
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    user_input = st.text_input("Type your message here...", key="user_input")
    send_clicked = st.button("📤 Send")
    
    if send_clicked and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        result2, response = rephraser(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Extract file paths and update session state
        st.session_state.file_paths = [row['file_path'] for row in result2 if 'file_path' in row]
        st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()