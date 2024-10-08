import os
import streamlit as st
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize Pinecone
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENV')
pc = Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)

# Connect to Pinecone index
index_name = "arya-index"
index = pc.Index(index_name)

# Define Hugging Face embeddings model
model_name = "intfloat/multilingual-e5-large"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# Initialize PineconeVectorStore for retrieval
docsearch = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace="arya-namespace"
)

# Define the LLM for generating responses (Hugging Face model)
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Example model
endpoint_url = f"https://api-inference.huggingface.co/models/{repo_id}"
huggingface_api_token = os.getenv('HUGGING_FACE_API')

llm = HuggingFaceEndpoint(
    endpoint_url=endpoint_url,
    huggingfacehub_api_token=huggingface_api_token,
    temperature=0.7,
    top_k=50
)

# Create a prompt template for the chatbot
template = """
You are Arya, the official bot of Arya Bhatt Hostel. Humans will ask you questions about the Arya Bhatt Hostel. 
Use the following context from the vector database to answer the question.
If you don't know the answer, just say you don't know.
Answer in a short and concise way.

Question: {question}
Answer:
"""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Create a retrieval-based QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(),
    return_source_documents=True  # Optional, if you want to return sources
)

# Streamlit App Interface
st.title("ARYA(Arya Bhatt offical Chat Bot)")
st.write("Ask me anything about Arya Bhatt Hostel!")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input for user question
user_question = st.text_input("Your Question:")

# If user has entered a question, process it
if user_question:
    with st.spinner('Thinking...'):
        # Get the response using invoke instead of run
        response = qa_chain.invoke(user_question)
        
        # Extract the chatbot's response
        chatbot_response = response['result']
        
        # Add the question and response to the chat history
        st.session_state.chat_history.append({"question": user_question, "response": chatbot_response})

if st.session_state.chat_history:
    st.write("### Chat History")
    for i, chat in enumerate(st.session_state.chat_history):
        st.write(f"**You:** {chat['question']}")
        st.write(f"**ARYA:** {chat['response']}")

# Footer
st.markdown("""
---
Developed and maintained by **Himanshu**
""")