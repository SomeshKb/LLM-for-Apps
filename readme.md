# Project Setup Guide

## 🚀 Running the Backend

To set up and run the backend, follow these steps:

### 1️⃣ Install Ollama
Ensure you have Ollama installed on your system. You can install it using:
```sh
curl -fsSL https://ollama.com/install.sh | sh
```
Or refer to the [Ollama installation guide](https://ollama.com/docs/install).

### 2️⃣ Pull the Mistral Image
Run the following command to pull the required model:
```sh
ollama pull mistral
```

### 3️⃣ Setup Virtual Environment
Navigate to the backend directory:
```sh
cd backend
```
Create and activate a virtual environment:
```sh
python3 -m venv ollama_env
```
For macOS/Linux:
```sh
source ./ollama_env/bin/activate
```
For Windows (Command Prompt):
```sh
ollama_env\Scripts\activate
```
For Windows (PowerShell):
```sh
.\ollama_env\Scripts\Activate.ps1
```

### 4️⃣ Install Dependencies
Install the required Python packages:
```sh
pip install -r requirements.txt
```

### 5️⃣ Run the Backend Server
Finally, start the backend service:
```sh
python3 app.py
```

---

## 🎨 Running the Frontend

To start the frontend application, follow these steps:

### 1️⃣ Install Angular CLI (if not installed)
```sh
npm install -g @angular/cli
```

### 2️⃣ Navigate to the Frontend Directory
```sh
cd chat-app
```

### 3️⃣ Serve the Angular App
Run the Angular development server:
```sh
ng serve
```
If port **4200** is busy, you can change it:
```sh
ng serve --port 4300
```

The frontend should now be running at `http://localhost:4200/` by default.

---

## 📌 Notes
- Ensure you have **Node.js** and **Angular CLI** installed before running the frontend.
- The backend must be running before launching the frontend to enable full functionality.
- For production deployment, configure environment variables and optimize the build accordingly.

---

Happy Coding! 🚀🎉

