from fastapi import FastAPI
from first_call import ask_ai

app = FastAPI()

@app.post("/chat")
def chat(data: dict):
    question = data["question"]
    answer = ask_ai(question)
    return {"answer": answer}