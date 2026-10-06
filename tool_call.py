import os, datetime
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

def get_time():
    """获取当前的日期和时间——这是一个本地工具，模型自己没有时钟"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ask_ai(messages, tools=None):
    body = {"model": "glm-4-flash", "messages": messages}
    if tools:
        body["tools"] = tools
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json=body,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]

tools = [{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "获取当前的日期和时间",
        "parameters": {"type": "object", "properties": {}}
    }
}]

messages = [{"role": "user", "content": "现在几点了？"}]

msg = ask_ai(messages, tools)
print("【第一轮】模型的原始回复：", msg)

if msg.get("tool_calls"):
    messages.append(msg)
    for tc in msg["tool_calls"]:
        name = tc["function"]["name"]
        result = get_time() if name == "get_time" else "不认识这个工具"
        print("【模型点单】要调工具:", name, "→ 我执行，结果:", result)
        messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    final = ask_ai(messages, tools)
    print("【最终回答】", final["content"])
else:
    print("【最终回答】", msg["content"])
    