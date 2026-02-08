import streamlit as st
import pandas as pd
from src.agent import DataAnalystAgent
import os
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Data Analysis Agent", page_icon="bar_chart", layout="wide")

# Load environment variables
load_dotenv()

st.title("🤖 Data Analysis AI Agent")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    api_key_input = st.text_input("OpenAI API Key", type="password", key="api_key_input")
    
    # Try to get from env if not input
    if not api_key_input:
        api_key_input = os.getenv("OPENAI_API_KEY")
        if api_key_input:
            st.success("API Key found in environment")
    
    st.header("Data Upload")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.agent = None

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! meaningful data analysis starts here. Please upload a dataset to get started."}]

if "agent" not in st.session_state:
    st.session_state.agent = None

# Main Chat Interface
if uploaded_file and api_key_input:
    # Load Data
    if st.session_state.agent is None:
        try:
            df = pd.read_csv(uploaded_file)
            base_url = os.getenv("OPENAI_BASE_URL")
            st.session_state.agent = DataAnalystAgent(df, api_key_input, base_url=base_url)
            st.toast("Agent initialized successfully!", icon="✅")
            # Optional: Add initial analysis to chat
            st.session_state.messages.append({"role": "assistant", "content": f"I've loaded your dataset with {len(df)} rows and {len(df.columns)} columns. Ask me anything about it!"})
        except Exception as e:
            st.error(f"Error loading file: {e}")

    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text, analysis_result = st.session_state.agent.process_message(prompt)
                
                st.markdown(response_text)
                if analysis_result is not None:
                     # with st.expander("Analysis Result", expanded=False): # Collapsed by default
                     #    st.code(analysis_result) # Display as code, but user can ignore it. 
                     
                     # The user said "idont want any code". So let's actually comment it out or make it very hidden.
                     pass
        
        # Save Agent Response (Text only for history, or structure it)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

elif not uploaded_file:
    st.info("👈 Please upload a CSV file to begin.")
elif not api_key_input:
    st.warning("👈 Please enter your OpenAI API Key to proceed.")
