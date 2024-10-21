# First, let's fix the AryaChatbot class (save as chatbot.py):

import os
from typing import Dict, List
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class AryaChatbot:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, huggingface_api: str):
        """Initialize the chatbot with necessary credentials and setup components."""
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.huggingface_api = huggingface_api
        # Initialize components directly
        self.vector_store = self._setup_pinecone()
        self.llm = self._setup_llm()
        self.qa_chain = self._create_qa_chain()
        
    def _setup_pinecone(self, index_name: str = "arya-index-o") -> PineconeVectorStore:
        """Initialize Pinecone and return vector store."""
        try:
            pc = Pinecone(api_key=self.pinecone_api_key, environment=self.pinecone_env)
            index = pc.Index(index_name)
            
            embeddings = HuggingFaceEmbeddings(
                model_name="intfloat/multilingual-e5-large",
                encode_kwargs={'normalize_embeddings': True}
            )
            
            return PineconeVectorStore(
                index=index,
                embedding=embeddings,
                namespace="ns1"
            )
        except PineconeException as e:
            raise Exception(f"Failed to initialize Pinecone: {str(e)}")

    def _setup_llm(self) -> HuggingFaceEndpoint:
        """Initialize the language model."""
        repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        endpoint_url = f"https://api-inference.huggingface.co/models/{repo_id}"
        
        return HuggingFaceEndpoint(
            endpoint_url=endpoint_url,
            huggingfacehub_api_token=self.huggingface_api,
            max_length=512,
            temperature=0.7,
            top_k=50,
            num_return_sequences=1,
            task="text2text-generation"
        )

    def _create_qa_chain(self) -> RetrievalQA:
        """Create the question-answering chain."""
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
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

    def get_response(self, question: str) -> str:
        """Get response for a given question."""
        try:
            response = self.qa_chain.invoke(question)
            return response['result']
        except Exception as e:
            raise Exception(f"Error getting response: {str(e)}")