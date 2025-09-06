# DocuSage
A contextual PDF ChatBot enabling intelligent, natural language queries on your documents. Built with Python, Flask, MongoDB, ChromaDB, and a local Llama 3.2 model via Ollama to power a robust RAG pipeline for content-aware conversations.



# How to Run this

NexusDocs: A Contextual PDF ChatBot
This project is a sophisticated, end-to-end Contextual PDF ChatBot designed for intelligent, document-aware conversations. It allows users to upload various documents, including PDFs and images, and interact with them through natural language queries. The system goes beyond simple keyword searches, providing answers grounded in the specific content of the uploaded files.

The entire architecture forms a robust Retrieval-Augmented Generation (RAG) pipeline. This enables the chatbot to first fetch relevant information from the documents and then use that context to generate a precise, informed response. The result is a highly effective, secure, and intelligent system for navigating complex information within your own files.

Key Technologies
Python: The core programming language for the project.

Flask: Powers the backend APIs for document upload and query handling.

Ollama: Used to run the language model locally, ensuring privacy and speed.

LangChain: The framework that orchestrates the entire RAG pipeline, connecting the LLM to the data sources.

Llama 3.2 (3B): The powerful open-source language model at the heart of the chatbot.

ChromaDB: A vector store that manages embeddings for efficient semantic search.

MongoDB: Stores document metadata and conversation history to provide a persistent and contextual chat experience.

How to Run the Project on macOS
Follow these steps to get the Contextual PDF ChatBot up and running on your local machine.

1. Clone the Repository
Open your Terminal and clone the project repository:

git clone [your-repository-url]
cd [your-project-directory]




2. Set Up Your Environment
Create a Python virtual environment to manage project dependencies in an isolated space. This is a best practice to avoid conflicts with your system's Python.

python3 -m venv venv
source venv/bin/activate




You should see (venv) appear in your Terminal prompt, indicating the virtual environment is active.

3. Install Dependencies
With the virtual environment active, install all the required Python libraries using the provided requirements.txt file.

pip install -r requirements.txt




4. Install Ollama and Pull the Model
You must have Ollama installed on your Mac and the Llama 3.2 model downloaded before running the application.

Download and install Ollama from the official Ollama website.

Once installed, open your Terminal and pull the Llama 3.2 model.

ollama pull llama3.2




5. Start Ollama Server
The Ollama server must be running to handle requests from the Flask application.

ollama serve




6. Configure Your Databases
Ensure both MongoDB and ChromaDB are ready for use.

MongoDB: Follow these steps to install and start the MongoDB service on macOS using Homebrew, the recommended package manager:

Install Homebrew (if you don't have it):

/bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"



Install MongoDB Community Edition:

brew tap mongodb/brew
brew install mongodb-community



Start the MongoDB service:

brew services start mongodb-community



Verify the service is running:

brew services list



You should see mongodb-community listed with a started status. The default connection string is mongodb://localhost:27017/.

ChromaDB: This is pre-configured to run as a lightweight, in-memory database by default, so no additional setup is required beyond the pip install from the dependencies step. For a persistent database, you can run it as a server in a separate process.

7. Run ChromaDB
If you want to run ChromaDB in a persistent, client-server mode for more robust, long-term use, you can run it locally with a specified path. This will ensure your data is saved to disk and not lost when the application terminates.

**chroma run --path ./MM_CHROMA_DB --host 0.0.0.0 --port 8000**

8. Run the Application
Start the Flask application from your Terminal to launch the chatbot.

python app.py  # or the name of your main application file




Your chatbot should now be accessible in your web browser, typically at http://127.0.0.1:5001.