import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

def ask_ai(question):
    """问AI任何问题，返回回答文字"""
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": "glm-4-flash",
            "messages": [
                {"role": "user", "content": question}
            ],
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    answer1 = ask_ai("用一句话解释什么是API")
    print(answer1)

    answer2 = ask_ai("给零基础学生一句学Python的建议")
    print(answer2)
    answer3 = ask_ai("找ai产品经理的工作需要哪些技能")
    print(answer3)