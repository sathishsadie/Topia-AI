<<<<<<< HEAD
# Topia-AI
Chat application .
=======
# 🌾 Topia Farm AI  

Topia Farm AI is an **AI-powered farm management assistant** that helps farmers and businesses manage their farms digitally.  
It combines **LangChain Agents**, **Gemini LLM**, and **FAISS-based RAG** (Retrieval-Augmented Generation) to answer farm-related queries and execute operations like buying/selling animals.  

---

## 🚀 Features  

- **Farm Creation**  
  Create a new farm with a custom name.  

- **Animal Management**  
  - Buy/Sell **Goats**  
  - Buy/Sell **Chickens**  
  - Buy/Sell **Quails**  
  - Always asks for confirmation before performing buy/sell actions.  

- **RAG-powered Question Answering**  
  - Uses FAISS vector database for **retrieval-augmented answers**.  
  - Ensures farm/company-specific answers are based on retrieved documents.  

- **Conversational AI**  
  - Supports casual farm-related conversations.  
  - Responds in a natural, conversational style.  

---

## 🏗 Project Structure  

```

frontend/   # React + TypeScript + Tailwind frontend
backend/    # FastAPI backend with LangChain + Gemini AI

```

---

## ⚙️ Prerequisites  

- **Backend**  
  - Python 3.10+  
  - FastAPI, Uvicorn  
  - LangChain, FAISS, Google Generative AI  
  - `.env` file with:  
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    RETRIEVE_K=5
    ```

- **Frontend**  
  - Node.js (v18+)  
  - npm  

---

## ▶️ Setup Instructions  

### Backend  

1. Go to the backend folder:  
   ```bash
   cd backend
   ```

2. Install dependencies:

   ```bash
   pip install fastapi uvicorn python-dotenv langchain langchain-google-genai langchain-community
   pip install faiss-cpu
   ```

3. Add `.env` file:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   RETRIEVE_K=5
   ```

4. Start FastAPI server:

   ```bash
   uvicorn app:app --reload
   ```

Backend runs on: `http://127.0.0.1:8000`

---

### Frontend

1. Go to frontend folder:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start development server:

   ```bash
   npm run dev
   ```

Frontend runs on: `http://localhost:5173`

---

## 💡 Example Usage

* `"Create a farm named GreenField"` → Creates new farm.
* `"Buy 10 goats"` → Bot asks: *“Do you want to confirm buying 10 goats?”*
* `"Yes"` → Executes `buygoat` tool.
* `"Sell 5 chickens"` → Executes after confirmation.
* `"Tell me about Topia company policies"` → Uses FAISS RAG context for answers.
* `"How are you today?"` → Friendly conversational reply.

---

## 🛠 Technologies Used

* **Frontend:** React + TypeScript + TailwindCSS
* **Backend:** FastAPI + Python
* **AI/LLM:** Gemini (via LangChain)
* **RAG:** FAISS Vector DB with Google Embeddings
* **Agent:** LangChain Tool-Calling Agent with confirmation logic

---

## 🌍 Use Case

**Topia Farm AI** can be used by:

* **Farmers** → Manage livestock digitally without manual tracking.
* **Agri-Tech Startups** → Build smart farm dashboards with AI integration.
* **Companies** → Provide AI-driven support for farm management queries.
* **Education & Research** → Simulate farm economics and management with AI.

This system ensures **safe, reliable AI assistance** by using:

* **Tool confirmation** (avoids accidental buy/sell).
* **RAG retrieval** (answers grounded in actual knowledge base).
* **Contextual conversations** (personalized user experience).

---

## 📜 License

This project is licensed under the MIT License.
