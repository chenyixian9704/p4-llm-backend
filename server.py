from fastapi import FastAPI
from first_call import ask_ai

app = FastAPI()
@app.get("/")
def home():
    return {"message": "这是陈奕先的 P4 后端。接口文档见 /docs，对话接口 POST /chat"}

@app.post("/chat")
def chat(data: dict):
    question = data["question"]
    answer = ask_ai(question)
    return {"answer": answer}