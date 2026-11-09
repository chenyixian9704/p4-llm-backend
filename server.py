import sqlite3

from pydantic import BaseModel, ValidationError
from fastapi import FastAPI
from first_stream import stream_answer
from first_call import ask_ai, ask_ai_structured, _call_llm
from fastapi.responses import StreamingResponse


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
@app.get("/chat/stream")
def chat_stream(question: str):
    return StreamingResponse(stream_answer(question), media_type="text/plain; charset=utf-8")

class MemoryRequest(BaseModel):
    question: str
    session_id: str = "default"

memory_store = {}   # C5：{会话id: 历史消息列表}——服务器内存里的"记事本"

@app.post("/chat/memory")
def chat_memory(data: MemoryRequest):
    history = memory_store.get(data.session_id, [])                    # ① 取这个会话的旧记忆（新会话=空列表）
    messages = history + [{"role": "user", "content": data.question}]  # ② 旧记忆 + 本次问题
    answer = _call_llm(messages[-10:])                                 # ③ 只发最近10条：窗口截断，防记忆无限胖
    memory_store[data.session_id] = messages + [                       # ④ 本轮对话（问+答）存回记事本
        {"role": "assistant", "content": answer},
    ]
    return {"answer": answer, "turns": len(memory_store[data.session_id]) // 2}