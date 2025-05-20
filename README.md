# 🧠 RAG Chatbot

A Retrieval-Augmented Generation (RAG) Chatbot built with FastAPI, Sentence Transformers, and Streamlit. This application allows users to upload documents, ask questions, and receive intelligent responses powered by LLMs enhanced with relevant information from your documents.

## 🚀 Features

- Upload documents (`pdf`, `txt`, `xlsx`, etc.) as either QA pairs or contextual information
- Automatically generate and store document embeddings
- Ask questions through a friendly chat interface
- RAG-based LLM responses using your uploaded data
- Simple and intuitive web interface

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- git

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/AbdulWasayUl/llm-project.git
   cd rag-chatbot
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install requirements**

   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

The application consists of three main components that need to be set up:

### 1. Set up the RAG index

```bash
cd app
python rag/rag.py
```

This initializes the RAG system, creating necessary directories and preparing the embedding model.

### 2. Download the LLM model

```bash
python backend/models.py
```

This downloads the specified LLM to models directory for later use.

### 3. Start the backend server

```bash
uvicorn backend.main:app --reload --port 8000
```

This starts the FastAPI backend server on port 8000 with auto-reload enabled.

### 4. Launch the frontend

```bash
streamlit run "frontend/app.py"
```

This starts the Streamlit frontend application. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501).

## 📝 Usage

1. **Upload Data**
   - Use the "Upload" tab to add your documents
   - Choose whether to process as QA pairs or context
   - For QA the questions and answers should be in seperate lines
   - Click "Upload" and wait for processing confirmation

2. **Chat Interface**
   - Type your questions in the input field
   - The chatbot will respond using the relevant information from your documents

## 🔧 Troubleshooting

- If you encounter issues with dependencies, try upgrading pip: `pip install --upgrade pip`
- Make sure all services (backend and frontend) are running simultaneously
- Check the console for error messages if the application isn't working properly

## 📋 Project Structure

```
rag-chatbot/
├── app/
│   ├── backend/
│   │   ├── main.py          # FastAPI server
│   │   └── models.py        # LLM models
│   ├── frontend/
│   │   └── app.py           # Streamlit interface
│   ├── rag/
│   │   └── rag.py           # RAG implementation
│   └── ...
├── requirements.txt
└── README.md
```