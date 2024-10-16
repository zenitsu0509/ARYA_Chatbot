import streamlit as st
from mycors import give_my_response


# Set the title of the app
st.title("Simple Text Input and Output App")

# Text input field
user_input = st.text_input("Enter your text:")

# If input is provided, display the output
if user_input:
    answer = give_my_response(user_input)
    st.write("bot:", answer)
