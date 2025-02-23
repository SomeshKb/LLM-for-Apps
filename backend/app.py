import os
import time
import ollama
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

app = Flask(__name__)
CORS(app)

# Load embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize ChromaDB vector store
persist_directory = "./chroma_db"
vector_store = Chroma(
    persist_directory=persist_directory, embedding_function=embedding_model
)

# Define available actions
actions = {
    "generate_model": {
        "description": "Generate a model",
        "api_endpoint": "http://your-internal-api.com/generate-model",
        "method": "POST",
    },
    "duplicate_model": {
        "description": "Duplicate a model",
        "api_endpoint": "http://your-internal-api.com/restart-service",
        "method": "POST",
    },
    "delete_model": {
        "description": "Delete a model",
        "api_endpoint": "http://your-internal-api.com/restart-service",
        "method": "POST",
    },
    "deploy_model": {
        "description": "Deploy a model",
        "api_endpoint": "http://your-internal-api.com/deploy",
        "method": "POST",
    },
}


def detect_action_with_llm(question):
    """Uses LLM to determine the required action from the provided action list"""

    # Create a formatted string of available actions
    action_list = "\n".join(
        [f"- {key}: {value['description']}" for key, value in actions.items()]
    )

    response = ollama.chat(
        model="mistral",
        messages=[
            {
                "role": "system",
                "content": f"""
You are an AI assistant that detects user intent based on the provided actions.  
Here are the available actions:
{action_list}

When given a user question, return ONLY the corresponding action key from the list above.  
If no relevant action exists, return 'none'.
""",
            },
            {
                "role": "user",
                "content": f"User asked: {question}. What action should be performed?",
            },
        ],
        stream=False,
    )

    action_key = response.get("message", {}).get("content", "none").strip()

    # Validate action exists
    if action_key in actions:
        return action_key
    return None  # No action detected


@app.route("/upload", methods=["POST"])
def upload_document():
    """Uploads a document, extracts text, and stores it in the vector database"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save file temporarily
        file_path = f"./docs/{file.filename}"
        os.makedirs("./docs", exist_ok=True)
        file.save(file_path)

        # Load and process PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split text into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)

        # Extract text content for embedding
        text_content = [doc.page_content for doc in texts if doc.page_content.strip()]

        if not text_content:
            return jsonify({"error": "No valid text extracted from the document"}), 400

        # ✅ Add texts to ChromaDB (embeddings are handled internally)
        vector_store.add_texts(text_content)
        vector_store.persist()

        return jsonify(
            {
                "message": f"Document '{file.filename}' processed and stored successfully."
            }
        )

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def query_rag():
    """Retrieves relevant document chunks and generates an answer using DeepSeek"""
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Missing 'question' parameter"}), 400

    try:
        start_time = time.time()  # Track execution time

        # Retrieve relevant documentation
        results = vector_store.similarity_search(question, k=1)
        retrieved_text = "\n".join([doc.page_content for doc in results])

        if not retrieved_text:
            return jsonify({"error": "No relevant document found."}), 404

        # Generate response using LLM
        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that answers user queries using documentation.",
                },
                {
                    "role": "user",
                    "content": f"Here is a document:\n\n{retrieved_text}\n\nAnswer this question:\n\n{question}",
                },
            ],
            stream=False,
        )

        answer = response.get("message", {}).get("content", "No response generated.")

        # Detect required action
        action_key = detect_action_with_llm(question)

        # Format response
        response_data = {"answer": answer, "action": None}

        if action_key:
            action = actions[action_key]
            response_data["action"] = {
                "description": action["description"],
                "confirm_message": f"Do you want to {action['description']}?",
                "action_key": action_key,
            }

        return jsonify(response_data)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"message": "RAG API is running! Upload a document and query it."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)
