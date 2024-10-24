import streamlit as st
import warnings
from config import load_config
from chatbot import AryaChatbot
import gc
import functools

# Cache the config loading to avoid repeated disk reads
@st.cache_data
def cached_load_config():
    """Cache configuration loading to reduce disk reads."""
    return load_config()

# Cache the chatbot initialization
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

# Cache the response generation
@st.cache_data(max_entries=100, ttl=3600)
def get_cached_response(question: str, _chatbot) -> str:
    """Cache chatbot responses to reduce API calls and computation."""
    return chatbot.get_response(question)

def clear_chat_history():
    """Clear chat history and session state."""
    st.session_state.chat_history = []
    gc.collect()  # Force garbage collection

def manage_chat_history(history, max_length=50):
    """Manage chat history length to prevent memory bloat."""
    if len(history) > max_length:
        history = history[-max_length:]  # Keep only the latest conversations
    return history

def main():
    try:
        # Suppress torch warning
        warnings.filterwarnings("ignore", message=".*torch.classes.*")
        
        # Setup page configuration
        st.set_page_config(
            page_title="ARYA - Arya Bhatt Dev",
            page_icon="🏢",
            layout="centered"
        )
        
        # Load cached config
        config = cached_load_config()
        
        st.title("🏢 ARYA - Development")
        st.markdown("""
        Welcome to the Arya Bhatt Hostel chatbot! I'm here to help you with any questions about the hostel.
        Feel free to ask about facilities, rules, or any other hostel-related matters.
        """)
        
        # Initialize session state efficiently
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = initialize_chatbot(config)
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Add clear chat button
        if st.button("Clear Chat History"):
            clear_chat_history()
        
        # Chat input with memory management
        user_question = st.text_input("Your Question:", key="user_input")
        
        if user_question and st.session_state.chatbot:
            try:
                with st.spinner('Processing your question...'):
                    # Use cached response
                    response = get_cached_response(user_question, st.session_state.chatbot)
                    
                    result = {
                        'question': user_question,
                        'response': response
                    }
                    
                    # Manage chat history length
                    st.session_state.chat_history.append(result)
                    st.session_state.chat_history = manage_chat_history(st.session_state.chat_history)
                    
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")
        
        # Display chat history efficiently
        if st.session_state.chat_history:
            st.write("### Recent Conversations")
            # Only show last 5 conversations to reduce memory usage
            for chat in reversed(st.session_state.chat_history[-5:]):
                with st.container():
                    st.write(f"**You:** {chat['question']}")
                    st.write(f"**ARYA:** {chat['response']}")
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
        # Clean up resources
        gc.collect()

if __name__ == "__main__":
    main()