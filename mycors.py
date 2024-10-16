import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from flask_cors import CORS

load_dotenv()

pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone_environment = os.getenv('PINECONE_ENV')
pc = Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)

index_name = "arya-index"
index = pc.Index(index_name)

model_name = "intfloat/multilingual-e5-large"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

docsearch = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace="arya-namespace"
)

repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
endpoint_url = f"https://api-inference.huggingface.co/models/{repo_id}"
huggingface_api_token = os.getenv('HUGGING_FACE_API')

llm = HuggingFaceEndpoint(
    endpoint_url=endpoint_url,
    huggingfacehub_api_token=huggingface_api_token,
    temperature=0.7,
    top_k=50
)


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever(),
    return_source_documents=True
)


def give_my_response(user_question):
    response = qa_chain.invoke(user_question)
    chatbot_response = response['result']
    return chatbot_response
    
