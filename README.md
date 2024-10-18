ARYA - Arya Bhatt Hostel Chatbot
================================

Welcome to **ARYA**, the official chatbot for Arya Bhatt Hostel. This chatbot is designed to help students and hostel residents with information related to hostel rules, facilities, and other queries. It uses Pinecone for vector search and Hugging Face for language model inference.

Features
--------

-   Provides accurate and concise answers about hostel facilities and rules.
-   Friendly, professional responses.
-   Real-time question processing.
-   Simple and easy-to-use interface.

Tech Stack
----------

-   **Streamlit**: For building the front-end of the chatbot.
-   **Pinecone**: For vector-based document retrieval.
-   **Hugging Face**: For language model and text generation.
-   **LangChain**: To manage LLM chains and document search.
-   **Python**: The core language used.

Setup Instructions
------------------

### 1\. Clone the Repository

```bash
git clone https://github.com/zenitsu0509/ARYA_Chatbot.git
cd ARYA_Chatbot
```

### 2\. Install Dependencies

Ensure that you have Python 3.8+ installed. You can install the required Python packages using:
```
pip install -r requirements.txt
```

### 3\. Set Up Environment Variables

You will need to configure environment variables to access the necessary APIs. Create a `.env` file in the project directory and add the following keys:
```
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_ENV=<your-pinecone-environment>
HUGGING_FACE_API=<your-huggingface-api-key>
```

### 4\. Configure the Index

Make sure you have a **Pinecone** index created and properly configured with the documents for Arya Bhatt Hostel information.

### 5\. Run the Application

You can start the Streamlit app using the following command:

```bash
streamlit run app.py
```

The application will launch locally, and you can access the chatbot via your browser at `http://localhost:8501`.

How It Works
------------

1.  **Pinecone Vector Store**: Retrieves relevant information from the hostel knowledge base using vector embeddings.
2.  **Hugging Face LLM**: Generates human-like responses based on the retrieved context and the user's question.
3.  **Streamlit Interface**: Provides an intuitive and responsive front-end for users to interact with the bot.

Project Structure
-----------------

```bash
arya-hostel-chatbot/
│
├── app.py                # Main application file
├── config.py             # Configuration loader for API keys and settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables file
├── README.md             # Project documentation
└── .gitignore            # Files to be ignored in version control
```

Key Functions
-------------

-   **setup_pinecone**: Initializes the Pinecone vector store for document search.
-   **setup_llm**: Configures the Hugging Face language model used for generating responses.
-   **create_qa_chain**: Combines the vector store with the LLM to create the question-answering logic.
-   **main**: Manages the Streamlit interface and user interactions.

Customization
-------------

You can modify the following parameters to customize ARYA:

-   **Language Model**: Change the Hugging Face model by updating the `repo_id` in the `setup_llm` function.
-   **Index Name**: Change the Pinecone index by modifying the `index_name` in `setup_pinecone`.

Future Enhancements
-------------------

-   **Admin Interface**: Allow hostel admins to update or add new knowledge base entries.
-   **Multilingual Support**: Support for other languages to assist international students.

Contributing
------------

If you'd like to contribute to the development of this project:

1.  Fork the repository.
2.  Create a new branch for your feature/bugfix.
3.  Submit a pull request with a detailed explanation of your changes.

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

* * * * *

💻 Developed and maintained by **Himanshu Gangwar**\
🔄 Last updated: October 2024
