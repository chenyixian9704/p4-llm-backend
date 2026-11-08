import sqlite3
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI
from first_call import ask_ai, ask_ai_structured


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    source: str = "glm-4-flash"
    confidence: str = "n/a"   # C3 Step2 新增：模型自评置信度（high/medium/low/n/a）


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
    try:
        llm = ask_ai_structured(question)
        answer, confidence = llm.answer, llm.confidence
    except ValidationError:
        # C3 Step3 兜底：模型不守 JSON 格式（如裹 ```json 围栏）时降级为普通回答，
        # confidence 标 n/a 诚实记录"这次没拿到自评"——/chat 从此永不 500
        answer, confidence = ask_ai(question), "n/a"
    save_chat(question, answer)
    return {"answer": answer, "source": "glm-4-flash", "confidence": confidence}
