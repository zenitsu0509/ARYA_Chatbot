import streamlit as st
import warnings
from config import load_config
from chatbot import AryaChatbot

@st.cache_resource
def initialize_chatbot():
    """Initialize the chatbot with configuration."""
    try:
        config = load_config()
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

def handle_enter():
    """Handle Enter key press"""
    if st.session_state.user_input and st.session_state.user_input.strip():
        handle_user_input(st.session_state.user_input)

def handle_user_input(user_question):
    """Handle user input and generate response."""
    if not user_question or not user_question.strip():
        return
        
    if st.session_state.chatbot:
        try:
            with st.spinner('Processing your question...'):
                response = st.session_state.chatbot.get_response(user_question)
                
                # Limit chat history size
                if len(st.session_state.chat_history) >= 20:
                    st.session_state.chat_history.pop(0)
                    
                st.session_state.chat_history.append({
                    'question': user_question,
                    'response': response
                })
                # Clear input after sending
                st.session_state.user_input = ""
        except Exception as e:
            st.error(f"Error processing your question: {str(e)}")

def display_chat_history():
    """Display chat history with pagination."""
    if not st.session_state.chat_history:
        return
        
    items_per_page = 5
    total_items = len(st.session_state.chat_history)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = total_pages
    
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    st.write("### Recent Conversations")
    
    for chat in reversed(st.session_state.chat_history[start_idx:end_idx]):
        with st.container():
            st.write(f"**You:** {chat['question']}")
            st.write(f"**ARYA:** {chat['response']}")
            st.markdown("---")
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Previous", disabled=st.session_state.current_page == 1):
                st.session_state.current_page -= 1
        with col2:
            st.write(f"Page {st.session_state.current_page} of {total_pages}")
        with col3:
            if st.button("Next →", disabled=st.session_state.current_page == total_pages):
                st.session_state.current_page += 1

def main():
    try:
        warnings.filterwarnings("ignore", message=".*torch.classes.*")
        
        st.set_page_config(
            page_title="ARYA",
            page_icon="🏢",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        st.title("🏢 ARYA - Your Hostel Assistant")
        st.write("Welcome! Ask me anything about Arya Bhatt Hostel.")
        
        # Initialize states
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = initialize_chatbot()
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Input container with mobile-friendly buttons
        with st.container():
            # Using columns for input and buttons
            col1, col2, col3, col4 = st.columns([6, 1.5, 1.5, 1.5])
            
            with col1:
                # Text input
                st.text_input(
                    "Your Question:",
                    key="user_input",
                    on_change=handle_enter,
                    placeholder="Type your question..."
                )
            
            # Mobile-friendly buttons
            with col2:
                if st.button("Enter ↵", use_container_width=True):
                    handle_user_input(st.session_state.user_input)
            
            with col3:
                if st.button("Send →", use_container_width=True):
                    handle_user_input(st.session_state.user_input)
            
            # Clear button for mobile users
            with col4:
                if st.button("Clear ✗", use_container_width=True):
                    st.session_state.user_input = ""
                    st.experimental_rerun()
        
        display_chat_history()
        
        # Footer with mobile-friendly spacing
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---\n💻 Developed by **Himanshu**")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()