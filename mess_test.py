from mess_menu import get_mess_menu

# In your chatbot's message handler
def handle_message(message):
    if "menu" in message.lower():
        response = get_mess_menu()
        # Send response back to user
        print(response)  # or however you send messages in your chatbot