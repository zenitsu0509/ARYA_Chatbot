import os
from typing import Dict, List
from langchain.vectorstores import VectorStore
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import re
from menu import MessMenu
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AryaChatbot:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, huggingface_api: str):
        """Initialize the chatbot with necessary credentials."""
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.huggingface_api = huggingface_api
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        self.menu_system = MessMenu()
        
    def setup(self):
        """Set up all components of the chatbot."""
        try:
            self.vector_store = self.setup_pinecone()
            self.llm = self.setup_llm()
            self.qa_chain = self.create_qa_chain()
        except Exception as e:
            raise Exception(f"Failed to initialize chatbot: {str(e)}")
        
    def setup_pinecone(self, index_name: str = "arya-index-o") -> VectorStore:
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

    def setup_llm(self) -> HuggingFaceEndpoint:
        """Initialize the language model."""
        try:
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
        except Exception as e:
            raise Exception(f"Failed to initialize language model: {str(e)}")

    def create_qa_chain(self) -> RetrievalQA:
        """Create the question-answering chain with custom prompt."""
        try:
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
        except Exception as e:
            raise Exception(f"Failed to create QA chain: {str(e)}")

    def handle_menu_query(self, question: str) -> str:
        """Handle questions related to the mess menu."""
        try:
            question_lower = question.lower()
            logger.debug(f"Handling menu query: {question_lower}")

            # Handle current menu query
            if re.search(r"(current menu|today's menu|what's for|what is for|what are we eating|mess menu|food)", question_lower):
                logger.debug("Fetching current menu")
                return self.menu_system.get_current_menu()

            # Handle weekly menu query
            if re.search(r"week(ly)? menu", question_lower):
                logger.debug("Fetching weekly menu")
                weekly_menu = self.menu_system.get_full_week_menu()
                if weekly_menu:
                    return self.menu_system.format_full_menu(weekly_menu)
                return "Sorry, I couldn't retrieve the weekly menu at the moment."

            # Handle specific day query
            days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
            for day in days_of_week:
                if day in question_lower:
                    logger.debug(f"Fetching menu for {day.capitalize()}")
                    day_menu = self.menu_system.get_menu_for_day(day.capitalize())
                    if day_menu:
                        response = [
                            f"📅 Menu for {day_menu['day_of_week']}:",
                            f"🌅 Breakfast: {day_menu['morning_menu']}",
                            f"🌞 Lunch: {day_menu['evening_menu']}",
                            f"🌙 Dinner: {day_menu['night_menu']}"
                        ]
                        
                        if day_menu['dessert'] != 'OFF':
                            response.append(f"🍨 Dessert: {day_menu['dessert']}")
                            
                        return "\n".join(response)
                    return f"Sorry, I couldn't retrieve the menu for {day.capitalize()}."

        except Exception as e:
            logger.error(f"Error handling menu query: {str(e)}")
            return "Sorry, I couldn't retrieve the menu at the moment."

        return None

    def get_response(self, question: str) -> str:
        """Get response for a given question."""
        try:
            # First, check if the question is related to the mess menu
            menu_response = self.handle_menu_query(question)
            if menu_response:
                return menu_response

            # If it's not a menu query, proceed with normal QA handling
            if not self.qa_chain:
                raise Exception("Chatbot not properly initialized. Call setup() first.")
            
            response = self.qa_chain.invoke(question)
            return response['result']
        except Exception as e:
            raise Exception(f"Error getting response: {str(e)}") 


# Test function to verify menu queries
def test_handle_menu_query():
    bot = AryaChatbot("pinecone_key", "pinecone_env", "huggingface_key")
    bot.setup()  # Ensure everything is set up

    test_questions = [
        "What's today's menu?",
        "What are we eating?",
        "What's for lunch?",
        "Tell me about the current menu.",
        "Show me the mess menu",
        "I want to know the food today."
    ]

    for question in test_questions:
        print(f"Query: {question}")
        response = bot.handle_menu_query(question)
        print(f"Response: {response}\n")


if __name__ == "__main__":
    test_handle_menu_query()