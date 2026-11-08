import sqlite3 
from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: str = "glm-4-flash"
from fastapi import FastAPI
from first_call import ask_ai
def save_chat(question, answer):
    conn = sqlite3.connect("chats.db")
    conn.execute("INSERT INTO chats (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()
app = FastAPI()
@app.get("/")
def home():
    return {"message": "这是陈奕先的 P4 后端。接口文档见 /docs，对话接口 POST /chat"}

@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):
    question = data.question
    answer = ask_ai(question)
    save_chat(question, answer)          # ← 新增：问答落库
    return {"answer": answer, "source": "glm-4-flash"}