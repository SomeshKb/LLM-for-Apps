import os
import ollama
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import time

app = Flask(__name__)
CORS(app)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

persist_directory = "./chroma_db"
vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

@app.route('/upload', methods=['POST'])
def upload_document():
    """ Uploads a document, extracts text, and stores it in the vector database """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
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

        return jsonify({"message": f"Document '{file.filename}' processed and stored successfully."})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_rag():
    """ Retrieves relevant document chunks and generates an answer using DeepSeek """
    data = request.json
    if "question" not in data:
        return jsonify({"error": "Missing 'question' parameter"}), 400

    try:
        question = data["question"]
        
        start_time = time.time()  # Track execution time

        # Retrieve top matching document chunks (optimize search)
        results = vector_store.similarity_search(question, k=1)  # Reduce to `k=1` for faster response
        retrieved_text = "\n".join([doc.page_content for doc in results])

        if not retrieved_text:
            return jsonify({"error": "No relevant document found."}), 404

        # Time check for debugging
        search_time = time.time() - start_time
        print(f"🔍 Vector search took {search_time:.2f} seconds")

        # Generate response using Ollama DeepSeek (with timeout handling)
        response = ollama.chat(
            model="deepseek-r1",
            messages=[
                {"role": "system", "content": "Use the retrieved document data to answer the question."},
                {"role": "user", "content": f"Question: {question}\n\nRelevant Document:\n{retrieved_text}"}
            ],
            stream=False
        )

        answer = response.get("message", {}).get("content", "No response generated.")

        print(f"🧠 DeepSeek response: {answer}")
        
        # Time check for debugging
        total_time = time.time() - start_time
        print(f"🧠 DeepSeek took {total_time - search_time:.2f} seconds")

        return jsonify({"answer": answer})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "RAG API is running! Upload a document and query it."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
