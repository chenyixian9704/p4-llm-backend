import os
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]

# ── 工具区：真函数 + 注册表捆在一起（C6 考古成果：单一事实来源）──
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hours_after(n):
    return (datetime.now() + timedelta(hours=int(n))).strftime("%Y-%m-%d %H:%M:%S")

TOOL_REGISTRY = {
    "get_time": (get_time, "获取当前的日期和时间。", {"type": "object", "properties": {}}),
    "hours_after": (hours_after, "计算从现在起 n 小时后的具体日期和时间。凡涉及'再过几小时'的问题必须调用此工具，禁止心算。",
                    {"type": "object", "properties": {"n": {"type": "integer", "description": "往未来推的小时数"}}, "required": ["n"]}),
}

def build_tools_json():
    """从注册表自动生成 API 要的说明书（翻译官，agent.py 同款）"""
    return [{"type": "function", "function": {"name": n, "description": d, "parameters": s}}
            for n, (fn, d, s) in TOOL_REGISTRY.items()]

def ask_ai_stream(messages, tools):
    """供货商 2.0：文本碎片当场 yield（text 包裹）；点单碎片悄悄攒，流结束打包 yield（tool_round 包裹）"""
    body = {"model": "glm-4-flash", "messages": messages, "tools": tools, "stream": True}
    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json=body,
        stream=True,
    )
    acc = {}   # 点单碎片账本：index → {id, name, arguments}（按格分筐，支持一轮流多个点单）
    for line in resp.iter_lines():
        if not line:
            continue
        text = line.decode("utf-8")
        if text.startswith("data:"):
            payload = text[5:].strip()
            if payload == "[DONE]":
                break
            delta = json.loads(payload)["choices"][0].get("delta", {})
            if delta.get("content"):                     # 文本碎片 → 直播
                yield {"type": "text", "piece": delta["content"]}
            for tc in delta.get("tool_calls") or []:     # 点单碎片 → 悄悄攒
                i = tc.get("index", 0)
                slot = acc.setdefault(i, {"id": "", "name": "", "arguments": ""})
                if tc.get("id"):
                    slot["id"] = tc["id"]
                fn = tc.get("function") or {}
                if fn.get("name"):
                    slot["name"] = fn["name"]
                if fn.get("arguments"):
                    slot["arguments"] += fn["arguments"]  # 参数长单子：一块一块拼
    if acc:   # 流结束发现攒到了点单 → 这轮是工具轮，打包交还
        calls = [{"id": s["id"], "type": "function",
                  "function": {"name": s["name"], "arguments": s["arguments"]}}
                 for _, s in sorted(acc.items())]
        yield {"type": "tool_round", "tool_calls": calls}

def run_agent_stream(user_text):
    """一轮提问：最终回答打字机直播；工具轮只显示状态。返回完整最终回答。"""
    messages = [{"role": "user", "content": user_text}]
    tools = build_tools_json()
    for round_no in range(1, 7):                     # 6 轮护栏（agent.py 同款）
        was_tool_round = False
        final_text = ""
        for parcel in ask_ai_stream(messages, tools):
            if parcel["type"] == "text":             # text 包裹：立刻播出
                print(parcel["piece"], end="", flush=True)
                final_text += parcel["piece"]
            else:                                    # tool_round 包裹：执行但不外播
                was_tool_round = True
                messages.append({"role": "assistant", "tool_calls": parcel["tool_calls"]})  # 先补点单消息
                for tc in parcel["tool_calls"]:      # 再逐单执行、喂回
                    name = tc["function"]["name"]
                    args = json.loads(tc["function"]["arguments"] or "{}")
                    fn, _, _ = TOOL_REGISTRY.get(name, (None, None, None))
                    result = fn(**args) if fn else f"未知工具：{name}"
                    print(f"\n[正在调用工具 {name} …]")
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
        if not was_tool_round:                       # 本轮全是文本 = 直播的就是最终回答
            print()
            return final_text
    print("\n（已达最大轮数）")
    return "（已达最大轮数，强制结束）"

if __name__ == "__main__":
    q = input("你（直接回车=默认问题）：").strip() or "现在几点了？再过5小时又是几点？"
    run_agent_stream(q)
