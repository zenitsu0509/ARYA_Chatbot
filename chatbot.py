import os
from typing import Dict, List
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import re
from menu import get_menu_for_day, get_full_week_menu

class AryaChatbot:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, huggingface_api: str):
        """Initialize the chatbot with necessary credentials."""
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.huggingface_api = huggingface_api
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        
    def setup(self):
        """Set up all components of the chatbot."""
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
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )

    def get_response(self, question: str) -> str:
        """Get response for a given question."""
        try:
            if not self.qa_chain:
                raise Exception("Chatbot not properly initialized. Call setup() first.")
            
            # Check if the question is related to the menu
            menu_response = self.handle_menu_query(question)
            if menu_response:
                return menu_response
            
            # Otherwise, use the QA chain for normal responses
            response = self.qa_chain.invoke(question)
            return response['result']
        except Exception as e:
            raise Exception(f"Error getting response: {str(e)}")
    
    def handle_menu_query(self, question: str) -> str:
        """Handle questions related to the mess menu."""
        # Normalize the question to lowercase
        question_lower = question.lower()
        
        # Check if the question asks about the weekly menu
        if re.search(r"week(ly)? menu", question_lower):
            weekly_menu = get_full_week_menu()
            if weekly_menu:
                menu_string = "Weekly Mess Menu:\n"
                for day_menu in weekly_menu:
                    menu_string += f"\n{day_menu['day_of_week']}:\n  Morning: {day_menu['morning_menu']}\n  Evening: {day_menu['evening_menu']}\n  Night: {day_menu['night_menu']}\n  Dessert: {day_menu['dessert']}\n"
                return menu_string
            return "Sorry, I couldn't retrieve the weekly menu at the moment."
        
        # Check if the question asks about a specific day's menu
        days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        for day in days_of_week:
            if day in question_lower:
                day_menu = get_menu_for_day(day.capitalize())
                if day_menu:
                    return (f"Menu for {day_menu['day_of_week']}:\n"
                            f"  Morning: {day_menu['morning_menu']}\n"
                            f"  Evening: {day_menu['evening_menu']}\n"
                            f"  Night: {day_menu['night_menu']}\n"
                            f"  Dessert: {day_menu['dessert']}")
                return f"Sorry, I couldn't retrieve the menu for {day.capitalize()}."
        
        # If no menu-related question detected, return None
        return None