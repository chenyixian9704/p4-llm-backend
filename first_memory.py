import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

resp = requests.post(
    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {key}"},
    json={
        "model": "glm-4-flash",
        "messages": [
            {"role": "user", "content": "我叫小明，是一名质检员，请记住我"},
            {"role": "assistant", "content": "我已经记住你了，小明。"},
            {"role": "user", "content": "我叫什么名字？做什么工作的？"},
        ],
    },
)
resp.raise_for_status()
print(resp.json()["choices"][0]["message"]["content"])
