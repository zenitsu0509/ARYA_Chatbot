# Use the official Python image as a base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from the requirements file
COPY lxrequirement.txt .
RUN pip install --no-cache-dir -r lxrequirement.txt

# Expose the port that Streamlit uses (default: 8501)
EXPOSE 8000

# Run the Streamlit app
CMD ["streamlit", "run", "chatbot2.py", "--server.port=8000", "--server.address=0.0.0.0"]