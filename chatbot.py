import os
from typing import Dict, List
from langchain_pinecone import PineconeVectorStore
from langchain_pinecone import PineconeEmbeddings
from pinecone import Pinecone, PineconeException
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import re
from menu import MessMenu

class AryaChatbot:
    def __init__(self, pinecone_api_key: str, pinecone_env: str, huggingface_api: str):
        """Initialize the chatbot with necessary credentials."""
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.huggingface_api = huggingface_api
        self.vector_store = None
        self.llm = None
        self.qa_chain = None
        self.menu_system = MessMenu()  # Initialize the menu system
        
    def setup(self):
        """Set up all components of the chatbot."""
        self.vector_store = self._setup_pinecone()
        self.llm = self._setup_llm()
        self.qa_chain = self._create_qa_chain()
        
    # [Previous methods remain unchanged: _setup_pinecone(), _setup_llm(), _create_qa_chain()]

    def handle_menu_query(self, question: str) -> str:
        """Handle questions related to the mess menu."""
        question_lower = question.lower()

        # Handle current menu query
        if any(phrase in question_lower for phrase in ["current menu", "today's menu", "what's for", "what is for"]):
            return self.menu_system.get_current_menu()

        # Handle weekly menu query
        if re.search(r"week(ly)? menu", question_lower):
            weekly_menu = self.menu_system.get_full_week_menu()
            if weekly_menu:
                return self.menu_system.format_full_menu(weekly_menu)
            return "Sorry, I couldn't retrieve the weekly menu at the moment."

        # Handle specific day query
        days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        for day in days_of_week:
            if day in question_lower:
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