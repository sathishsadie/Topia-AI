

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from collections import deque
from typing import Any
from dotenv import load_dotenv

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent


# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class QueryRequest(BaseModel):
    message: str

class FarmData(BaseModel):
    name: str

class AnimalData(BaseModel):
    number: int


# Load environment variables
load_dotenv()
RETRIEVE_K = int(os.getenv("RETRIEVE_K", 5))

# Load vector store for Retrieval-Augmented Generation (RAG)
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

    vector_store = FAISS.load_local(
        r"Topia_Vector_DB_cosine\\topia.faiss",
        embeddings,
        allow_dangerous_deserialization=True
    )
except Exception as e:
    print(f"Warning: could not load vector store: {e}")
    vector_store = None


def get_retrieved_context(query: str, k: int = RETRIEVE_K) -> str:
    """Retrieve top-k docs from FAISS and format into context string without character limit."""
    if vector_store is None:
        return ""

    try:
        docs = vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Warning: could not perform similarity search: {e}")
        try:
            docs_with_scores = vector_store.similarity_search_with_score(query, k=k)
            docs = [d for d, _ in docs_with_scores]
        except Exception:
            return ""

    parts = [getattr(doc, "page_content", "").strip() for doc in docs]
    return "\n\n".join(parts)
@tool
async def createfarm(name: str) -> str:
    """Creates a new farm with the given name for the user."""
    name_clean = (name or "").strip()
    if not name_clean:
        return "Please provide a non-empty farm name."
    resp = await create_farm(FarmData(name=name_clean))
    return resp.get("message", f"Farm '{name_clean}' created successfully!")

async def _quantity_op(endpoint: str, quantity: int, plural_name: str) -> str:
    """Helper for buy/sell operations."""
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        return f"Invalid quantity: {quantity}. Please pass a whole number."
    if qty <= 0:
        return "Quantity must be greater than 0."
    
    data = AnimalData(number=qty)
    if endpoint == "buychicken":
        resp = await buy_chicken(data)
    elif endpoint == "sellchicken":
        resp = await sell_chicken(data)
    elif endpoint == "buygoat":
        resp = await buy_goat(data)
    elif endpoint == "sellgoat":
        resp = await sell_goat(data)
    elif endpoint == "buyquail":
        resp = await buy_quail(data)
    elif endpoint == "sellquail":
        resp = await sell_quail(data)
    else:
        return "Invalid operation."
        
    return resp.get("message", f"{qty} {plural_name} processed successfully.")

@tool
async def buychicken(quantity: int) -> str: 
    """Buys the specified number of chickens for the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("buychicken", quantity, "chickens")

@tool
async def sellchicken(quantity: int) -> str: 
    """Sells the specified number of chickens from the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("sellchicken", quantity, "chickens")

@tool
async def buygoat(quantity: int) -> str: 
    """Buys the specified number of goats for the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("buygoat", quantity, "goats")

@tool
async def sellgoat(quantity: int) -> str:
    """Sells the specified number of goats from the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("sellgoat", quantity, "goats")

@tool
async def buyquail(quantity: int) -> str: 
    """Buys the specified number of quails for the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("buyquail", quantity, "quails")

@tool
async def sellquail(quantity: int) -> str: 
    """Sells the specified number of quails from the user's farm. **Always ask the user for confirmation before executing this tool.**"""
    return await _quantity_op("sellquail", quantity, "quails")


# LangChain Agent Configuration
TOOLS = [createfarm, buygoat, sellgoat, buychicken, sellchicken, buyquail, sellquail]
SYSTEM_PROMPT = (
    "You are Topia Farm AI — a helpful assistant with the following core functions\n"
    "1) If a user requests to buy or sell an animal, first ask them to confirm the action before executing the tool.\n"
    "2) If the user requests an action that matches a tool (create farm, buy/sell animals), execute that tool ONLY after confirmation.\n"
    "3) If the user asks a company-specific question, answer STRICTLY using the RETRIEVED CONTEXT.\n"
    "4) For casual conversation, respond helpfully.\n"
    "Avoid inventing facts. If uncertain, say you don't know."
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT + "\n\nRETRIEVED CONTEXT:\n{context}\n"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, TOOLS, prompt)
agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

memory: deque = deque(maxlen=20)

def extract_response_text(resp: Any) -> str:
    """Extract agent response text safely."""
    if isinstance(resp, dict):
        for key in ("output", "output_text", "text", "result"):
            if key in resp and resp[key]:
                return str(resp[key])
        return str(resp)
    return str(resp)


# Main FastAPI Endpoints
@app.post("/chat")
async def chat_with_bot(request: QueryRequest):
    input_message = request.message
    retrieved_context = get_retrieved_context(input_message, k=6)
    chat_history_list = list(memory)
    
    try:
        # ainvoke must be used with async tools
        result = await agent_executor.ainvoke({
            'input': input_message,
            'chat_history': chat_history_list,
            'context': retrieved_context
        })
    except Exception as e:
        return {"response": f"Sorry, an error was raised: {e}"}
    
    assistant_text = extract_response_text(result)
    memory.append(HumanMessage(content=input_message))
    memory.append(AIMessage(content=assistant_text))
    return {"response": assistant_text}


# Backend API Endpoints (these are now part of the same application)
@app.post("/createfarm")
async def create_farm(data: FarmData):
    print(f"Received request to create farm: {data.name}")
    return {"message": f"Farm '{data.name}' created successfully!"}

@app.put("/buygoat")
async def buy_goat(data: AnimalData):
    print(f"Received request to buy {data.number} goats")
    return {"message": f"Successfully purchased {data.number} goats."}

@app.put("/sellgoat")
async def sell_goat(data: AnimalData):
    print(f"Received request to sell {data.number} goats")
    return {"message": f"Successfully sold {data.number} goats."}

@app.put("/buychicken")
async def buy_chicken(data: AnimalData):
    print(f"Received request to buy {data.number} chickens")
    return {"message": f"Successfully purchased {data.number} chickens."}

@app.put("/sellchicken")
async def sell_chicken(data: AnimalData):
    print(f"Received request to sell {data.number} chickens")
    return {"message": f"Successfully sold {data.number} chickens."}

@app.put("/buyquail")
async def buy_quail(data: AnimalData):
    print(f"Received request to buy {data.number} quails")
    return {"message": f"Successfully purchased {data.number} quails."}

@app.put("/sellquail")
async def sell_quail(data: AnimalData):
    print(f"Received request to sell {data.number} quails")
    return {"message": f"Successfully sold {data.number} quails."}