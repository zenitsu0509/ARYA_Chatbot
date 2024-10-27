import streamlit as st
import warnings
from config import load_config
from chatbot import AryaChatbot
import gc
import functools
from PIL import Image
import os

# Cache decorators remain the same
@st.cache_data
def cached_load_config():
    """Cache configuration loading to reduce disk reads."""
    return load_config()

@st.cache_resource
def initialize_chatbot(config):
    """Initialize and cache the chatbot instance."""
    try:
        chatbot = AryaChatbot(
            pinecone_api_key=config['PINECONE_API_KEY'],
            pinecone_env=config['PINECONE_ENV'],
            huggingface_api=config['HUGGING_FACE_API']
        )
        chatbot.setup()
        return chatbot
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {str(e)}")
        return None

@st.cache_data(max_entries=100, ttl=3600)
def get_cached_response(question: str) -> str:
    """Cache chatbot responses to reduce API calls and computation."""
    chatbot = st.session_state.chatbot
    if chatbot is None:
        raise ValueError("Chatbot not initialized")
    return chatbot.get_response(question)

def init_session_state():
    """Initialize all session state variables."""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

def clear_chat_history():
    """Clear chat history and session state."""
    st.session_state.chat_history = []
    get_cached_response.clear()
    gc.collect()

def manage_chat_history(history, max_length=50):
    """Manage chat history length to prevent memory bloat."""
    if len(history) > max_length:
        history = history[-max_length:]
    return history

def display_images(photo_paths):
    """Display images in a grid layout."""
    try:
        cols = st.columns(min(3, len(photo_paths)))
        for idx, path in enumerate(photo_paths):
            if os.path.exists(path):
                try:
                    with Image.open(path) as img:
                        cols[idx % 3].image(img, caption=f"Image {idx + 1}", use_column_width=True)
                except Exception as e:
                    cols[idx % 3].error(f"Error loading image: {str(e)}")
            else:
                cols[idx % 3].error(f"Image not found: {path}")
    except Exception as e:
        st.error(f"Error displaying images: {str(e)}")

def handle_input():
    """Handle the submission of user input."""
    if st.session_state.user_input.strip():
        user_question = st.session_state.user_input
        try:
            with st.spinner('Processing your question...'):
                response = get_cached_response(user_question)
                result = {'question': user_question}
                
                if isinstance(response, dict) and "photos" in response:
                    result['response'] = "Here are the photos you requested:"
                    result['photos'] = response["photos"]
                else:
                    result['response'] = response if isinstance(response, str) else response.get("text", "I'm not sure how to respond to that.")
                
                st.session_state.chat_history.append(result)
                st.session_state.chat_history = manage_chat_history(st.session_state.chat_history)
                
        except Exception as e:
            st.error(f"Error processing your question: {str(e)}")
    
    st.session_state.user_input = ""

def main():
    try:
        # Initialize session state first
        init_session_state()
        
        # Suppress warnings
        warnings.filterwarnings("ignore", message=".*torch.classes.*")
        
        # Setup page configuration
        st.set_page_config(
            page_title="ARYA - Arya Bhatt Dev",
            page_icon="🏢",
            layout="centered"
        )
        
        # Load cached config
        config = cached_load_config()
        
        # Initialize chatbot if not already done
        if st.session_state.chatbot is None:
            st.session_state.chatbot = initialize_chatbot(config)
        
        st.title("🏢 ARYA - Development")
        st.markdown("""
        Welcome to the Arya Bhatt Hostel chatbot! I'm here to help you with any questions about the hostel.
        Feel free to ask about facilities, rules, or any other hostel-related matters.
        """)
        
        # Add clear chat button
        if st.button("Clear Chat History"):
            clear_chat_history()
        
        # Create input form
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input(
                "Your Question:",
                key="user_input"
            )
            submit_button = st.form_submit_button("Send", on_click=handle_input)
        
        # Display chat history
        if st.session_state.chat_history:
            st.write("### Recent Conversations")
            for chat in reversed(st.session_state.chat_history[-5:]):
                with st.container():
                    st.write(f"**You:** {chat['question']}")
                    st.write(f"**ARYA:** {chat['response']}")
                    
                    if 'photos' in chat:
                        display_images(chat['photos'])
                    
                    st.markdown("---")
        
        # Footer
        st.markdown("""
        ---
        💻 Developed and maintained by **Himanshu**  
        🔄 Last updated: October 2024
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please contact the administrator for assistance.")
        
    finally:
        gc.collect()

if __name__ == "__main__":
    main()