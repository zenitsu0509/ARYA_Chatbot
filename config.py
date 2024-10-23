import os
import streamlit as st
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from environment variables or Streamlit secrets.
    Returns dict with configuration values.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Dictionary to store our configuration
    config = {}

    # List of required environment variables
    required_vars = [
        'PINECONE_API_KEY',
        'PINECONE_ENV',
        'HUGGING_FACE_API',
        'MYSQL_USER',
        'MYSQL_PASSWORD'
    ]

    # Optional variables with defaults
    optional_vars = {
        'MYSQL_HOST': 'localhost',
        'MYSQL_PORT': '3306',
        'MYSQL_DATABASE': 'Mess_Menu'
    }

    # Load required variables
    for var in required_vars:
        # First check Streamlit secrets (for deployment)
        if hasattr(st.secrets, var):
            config[var] = st.secrets[var]
        # Then check environment variables
        elif os.getenv(var):
            config[var] = os.getenv(var)
        else:
            config[var] = None

    # Load optional variables with defaults
    for var, default in optional_vars.items():
        if hasattr(st.secrets, var):
            config[var] = st.secrets[var]
        else:
            config[var] = os.getenv(var, default)

    # Validate required configuration
    missing_vars = [var for var in required_vars if config[var] is None]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set them in .env file for local development or in Streamlit secrets for deployment."
        )

    return config