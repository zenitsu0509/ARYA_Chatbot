import os
import streamlit as st
from typing import Dict, List
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import load_config

def setup_pinecone(api_key: str, environment: str, index_name: str = "arya-index") -> PineconeVectorStore:
    """Initialize Pinecone and return vector store."""
    try:
        pc = Pinecone(api_key=api_key, environment=environment)
        index = pc.Index(index_name)
        
        # Initialize embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large",
            encode_kwargs={'normalize_embeddings': True}
        )
        
        return PineconeVectorStore(
            index=index,
            embedding=embeddings,
            namespace="arya-namespace"
        )
    except PineconeException as e:
        st.error(f"Failed to initialize Pinecone: {str(e)}")
        raise

def setup_llm(api_token: str) -> HuggingFaceEndpoint:
    """Initialize the language model."""
    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    endpoint_url = f"https://api-inference.huggingface.co/models/{repo_id}"
    
    # Pass parameters explicitly
    return HuggingFaceEndpoint(
        endpoint_url=endpoint_url,
        huggingfacehub_api_token=api_token,
        max_length=512,
        temperature=0.7,
        top_k=50,
        num_return_sequences=1,
        task="text2text-generation"  # Changed from text-generation
    )
    
    return HuggingFaceEndpoint(
        endpoint_url=endpoint_url,
        huggingfacehub_api_token=api_token,
        model_kwargs=model_kwargs,
        task="text2text-generation"  # Changed from text-generation
    )

def create_qa_chain(llm: HuggingFaceEndpoint, docsearch: PineconeVectorStore) -> RetrievalQA:
    """Create the question-answering chain with custom prompt."""
    template = """
    You are Arya, the official bot of Arya Bhatt Hostel. Your role is to provide accurate and helpful information about the hostel.

    Context information from the knowledge base:
    {context}

    Guidelines:
    - Provide concise, accurate answers based on the given context
    - If information is not available in the context, politely say you don't know
    - Be friendly and professional in your responses
    - Keep responses brief but informative

    Question: {question}
    Answer:
    """
    
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

def main():
    try:
        # Suppress torch warning
        import warnings
        warnings.filterwarnings("ignore", message=".*torch.classes.*")
        
        # Load configuration
        config = load_config()
        
        # Initialize Pinecone and vector store
        docsearch = setup_pinecone(
            api_key=config['PINECONE_API_KEY'],
            environment=config['PINECONE_ENV']
        )
        
        # Initialize HuggingFace LLM
        llm = setup_llm(config['HUGGING_FACE_API'])
        
        # Initialize QA chain
        qa_chain = create_qa_chain(llm, docsearch)
        
        # Setup interface
        st.set_page_config(
            page_title="ARYA - Arya Bhatt Hostel Chatbot",
            page_icon="🏢",
            layout="centered"
        )
        
        st.title("🏢 ARYA - Your Hostel Assistant")
        st.markdown("""
        Welcome to the Arya Bhatt Hostel chatbot! I'm here to help you with any questions about the hostel.
        Feel free to ask about facilities, rules, or any other hostel-related matters.
        """)
        
        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat input
        user_question = st.text_input("Your Question:", key="user_input")
        
        if user_question:
            try:
                with st.spinner('Processing your question...'):
                    response = qa_chain.invoke(user_question)
                    
                    # Extract sources if available
                    sources = []
                    if 'source_documents' in response:
                        sources = [doc.metadata.get('source', 'Unknown') for doc in response['source_documents']]
                    
                    result = {
                        'question': user_question,
                        'response': response['result'],
                        'sources': sources
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
                    if chat.get('sources'):
                        with st.expander("View Sources"):
                            for source in chat['sources']:
                                st.write(f"- {source}")
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
