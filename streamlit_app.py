import streamlit as st
import warnings
from config import load_config
from chatbot import AryaChatbot

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

def main():
    try:
        # Suppress torch warning
        warnings.filterwarnings("ignore", message=".*torch.classes.*")
        
        # Setup page configuration
        st.set_page_config(
            page_title="ARYA - Arya Bhatt dev bot",
            page_icon="🏢",
            layout="centered"
        )
        
        st.title("🏢 ARYA - Dev Bot")
        st.markdown("""
        Welcome to the Arya Bhatt Hostel chatbot! I'm here to help you with any questions about the hostel.
        Feel free to ask about facilities, rules, or any other hostel-related matters.
        """)
        
        # Initialize session state
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = initialize_chatbot()
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat input
        user_question = st.text_input("Your Question:", key="user_input")
        
        if user_question and st.session_state.chatbot:
            try:
                with st.spinner('Processing your question...'):
                    response = st.session_state.chatbot.get_response(user_question)
                    
                    result = {
                        'question': user_question,
                        'response': response
                    }
                    st.session_state.chat_history.append(result)
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.write("### Recent Conversations")
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
        """)
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please contact the administrator for assistance.")

if __name__ == "__main__":
    main()