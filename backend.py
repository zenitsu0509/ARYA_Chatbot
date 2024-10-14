import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from flask_cors import CORS
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)


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
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
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
    return_source_documents=True
)

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Preflight request handling
        return jsonify({"response": "CORS preflight passed."}), 200
    
    data = request.json
    user_question = data.get('question', '')
    
    if user_question:
        # Get the response from the QA model
        response = qa_chain.invoke(user_question)
        chatbot_response = response['result']
        
        return jsonify({"response": chatbot_response})
    
    return jsonify({"response": "Please provide a valid question."})

if __name__ == '__main__':
    app.run(debug=True)
