import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

def stream_answer(question):
    """流式问AI：一块一块吐出去（yield），自己不打印——吃块是调用者的事"""
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": "glm-4-flash",
            "messages": [{"role": "user", "content": question}],
            "stream": True,      # 岗位一：告诉API"我要流式"
        },
        stream=True,             # 岗位二：告诉requests"边收边读"
    )
    for line in resp.iter_lines():          # 一行一行地收（这就是"流"本身）
        if not line:                         # SSE 用空行分隔消息，空行跳过
            continue
        text = line.decode("utf-8")          # 收到的是字节，翻译成文字
        if text.startswith("data:"):
            payload = text[5:].strip()       # 剥掉"data:"前缀，留下JSON
            if payload == "[DONE]":
                break                        # 服务器说"上完菜了"，散场
            chunk = json.loads(payload)      # 这一小片是JSON，拆包
            piece = chunk["choices"][0]["delta"].get("content", "")
            yield piece                      # ② 不print，改成"吐出去"——吐完暂停，被要再继续

if __name__ == "__main__":            # ③ 主程序变"吃块的"：要一块吃一块
    for piece in stream_answer("用三句话介绍什么是流式输出"):
        print(piece, end="", flush=True)   # end=""不换行拼接；flush=立刻显示别攒着
    print()   # 收尾补一个换行
