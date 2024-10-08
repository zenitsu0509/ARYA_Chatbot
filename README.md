Arya Bhatt Hostel Chatbot
=========================

This repository contains the code for an AI-powered chatbot that answers questions related to Arya Bhatt Hostel. The chatbot utilizes state-of-the-art natural language processing (NLP) models to provide accurate and concise answers from a knowledge base. It integrates **Pinecone** for efficient vector-based search and **Hugging Face** models for generating human-like responses. The chatbot is deployed using **Streamlit** for an interactive web-based interface.

Features
--------

-   **Real-time question answering**: The chatbot can answer questions about Arya Bhatt Hostel, such as hostel rules, facilities, and more.
-   **Efficient vector search**: Pinecone is used to store and retrieve information from the vector database, ensuring fast and relevant responses.
-   **Hugging Face NLP models**: The chatbot utilizes Hugging Face's `mistralai/Mixtral-8x7B-Instruct-v0.1` model for generating responses.
-   **Streamlit interface**: A simple and intuitive interface that allows users to ask questions and view chat history.
-   **Chat history**: The app displays the full chat history during the session, showing past interactions and responses.
-   **Dynamic and customizable**: Easily adaptable to other use cases with different knowledge bases or NLP models.

Getting Started
---------------

### Prerequisites

To run this project locally, you'll need the following tools installed:

-   Python 3.8 or higher
-   Streamlit
-   Pinecone
-   Hugging Face's Transformers

### Installation

1.  Clone the repository:

    `git clone https://github.com/zenitsu0509/Arya_Chatbot.git
    cd Arya_Chatbot`

2.  Install the required dependencies:

    `pip install -r requirements.txt`

3.  Set up your environment variables:

    -   Create a `.env` file in the root directory of your project.
    -   Add your **Pinecone** and **Hugging Face** API keys as environment variables in the `.env` file:

        `PINECONE_API_KEY=your-pinecone-api-key
        PINECONE_ENV=your-pinecone-environment
        HUGGING_FACE_API=your-hugging-face-api-key`

### Running the App

After installing the dependencies and setting up the environment variables, you can run the chatbot using Streamlit:

`streamlit run app.py`

This will start the Streamlit server and launch the chatbot in your web browser. You can now interact with the chatbot and ask questions about Arya Bhatt Hostel.

Usage
-----

Once the app is running, simply enter your questions in the input field. The chatbot will respond with the most accurate and concise answer based on the available knowledge base. You can also view the chat history within the session to see past conversations.

Project Structure
-----------------

-   **app.py**: The main application file containing the Streamlit UI and logic for the chatbot.
-   **chatbot.py**: Core functionality for embedding questions, retrieving context, and generating responses.
-   **requirements.txt**: List of dependencies needed to run the application.
-   **.env.example**: Example environment file with placeholders for API keys.

Technologies Used
-----------------

-   **Pinecone**: For vector-based search and context retrieval.
-   **Hugging Face Transformers**: For NLP-based response generation.
-   **Streamlit**: For deploying the chatbot with a web interface.
-   **Python**: Core programming language for implementing the chatbot logic.

Future Enhancements
-------------------

-   Add more knowledge and rules to the vector database to cover a wider range of hostel-related queries.
-   Implement support for multiple languages using multilingual models.
-   Improve the user interface with additional features, such as voice input and real-time notifications.

Contributing
------------

Contributions are welcome! Feel free to fork this repository, make improvements, and submit a pull request.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Maintainer
----------

Developed and maintained by **Himanshu**. Feel free to reach out for any questions or collaboration opportunities.
