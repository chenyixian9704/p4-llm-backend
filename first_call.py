import os
import re
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]


class LLMAnswer(BaseModel):
    """C3 Step2 核心：模型结构化回答的统一格式。
    confidence 是模型对回答可靠性的自评（high/medium/low）。"""
    answer: str
    confidence: str


def _call_llm(messages):
    """裸调 GLM（唯一出口）：返回正文文本。"""
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": "glm-4-flash", "messages": messages},
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def ask_ai(question):
    """旧接口：问AI任何问题，返回回答文字（--demo 演示在用）。"""
    return _call_llm([{"role": "user", "content": question}])


def strip_code_fence(raw):
    """C3 Step3：把模型裹的 ```json ... ``` 围栏剥掉，只留 {...} 部分。
    没裹围栏的回答原样返回——正则找不到就不动手。"""
    m = re.search(r"\{.*\}", raw, re.S)
    return m.group() if m else raw


def ask_ai_structured(question):
    """C3 Step2：要求模型按 JSON 回答，model_validate_json 当闸门。

    ⚠️ 故意不做容错：模型偶尔不守规矩（答案裹 ```json 代码块、漏字段）会抛
    ValidationError —— 这不是 bug，是给 Step3 留的活教材（/docs 四测抓现行）。
    """
    instruction = (
        "请严格按如下JSON格式回答，除JSON外不要输出任何其他内容：\n"
        '{"answer": "你的回答", "confidence": "high|medium|low"}\n'
        "confidence 是你对本回答可靠性的自评：确定选high，有推测成分选medium，"
        "不知道或超纲选low。"
    )
    raw = _call_llm([{"role": "user", "content": f"{question}\n\n{instruction}"}])
    raw = strip_code_fence(raw)
    return LLMAnswer.model_validate_json(raw)


if __name__ == "__main__":
    answer1 = ask_ai("用一句话解释什么是API")
    print(answer1)

    answer2 = ask_ai("给零基础学生一句学Python的建议")
    print(answer2)
    answer3 = ask_ai("找ai产品经理的工作需要哪些技能")
    print(answer3)
