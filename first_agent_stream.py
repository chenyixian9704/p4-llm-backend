import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

tools = [{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "获取当前的日期和时间",
        "parameters": {"type": "object", "properties": {}}
    }
}]

resp = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": "现在几点了？"}],
        "tools": tools,
        "stream": True,      # 带着工具清单 + 要求流式：两种机制第一次同框
    },
    stream=True,
)

for line in resp.iter_lines():
    if not line:
        continue
    text = line.decode("utf-8")
    if text.startswith("data:"):
        payload = text[5:].strip()
        if payload == "[DONE]":
            print("\n=== 上完菜了 ===")
            break
        chunk = json.loads(payload)
        delta = chunk["choices"][0].get("delta", {})
        if delta.get("content"):
            print("【文本块】", delta["content"])
        if delta.get("tool_calls"):
            print("【工具块】", json.dumps(delta["tool_calls"], ensure_ascii=False))
