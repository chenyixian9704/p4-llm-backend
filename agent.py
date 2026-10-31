"""P4 补全：从"最小 tool calling"升级为"完整手搓 Agent"。

对照手搓 Agent 六件套（见 agent 闭环图）：
  · System Prompt      → SYSTEM_PROMPT（人设 + 规则），之前 tool_call.py 没有这一层
  · 记忆 Memory        → self.messages + 存盘到 agent_memory.json（resume 可跨程序续聊）
  · LLM 决策/工具执行/观察结果 → chat() 里的循环（模型点单 → 本地执行 → 喂回，最多 6 轮）
  · 工具注册表         → TOOL_REGISTRY 字典：加一个工具 = 加一行，告别手写 JSON 易错、脱节

运行：
  python agent.py            # 交互式对话（输入 exit 退出）
  python agent.py --demo     # 内置多轮演示（含记忆持久化验证）
"""

import os
import sys
import json
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ["ZHIPU_API_KEY"]


# ── 1. System Prompt：Agent 的角色与规则（之前 tool_call.py 缺这块）──
SYSTEM_PROMPT = (
    "你是一个运行在本地后端里的轻量 Agent，服务于纺织/化纤行业的一线人员。"
    "你能调用少量本地工具获取实时信息（时间、日期）。"
    "规则：只在需要实时信息时调用工具，没有对应工具/数据时直接说明，禁止描述查询过程或编造结果，调完用大白话回答。"
)


# ── 2. 工具注册表：函数 + 说明书 写在一起，单一事实来源 ──
def get_time():
    """返回当前本地时间（精确到秒），格式 YYYY-MM-DD HH:MM:SS。"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date():
    """返回今天日期（不含时间），格式 YYYY-MM-DD。"""
    return datetime.datetime.now().strftime("%Y-%m-%d")
def hours_after(n):
    """计算从现在起 n 小时后的具体日期和时间，格式 YYYY-MM-DD HH:MM:SS。"""
    t = datetime.datetime.now() + datetime.timedelta(hours=n)
    return t.strftime("%Y-%m-%d %H:%M:%S")
def search_resume(question):
    """在简历知识库中检索与问题最相关的资料段落"""
    text = open("resume_kb.txt", encoding="utf-8").read()
    chunks = text.split("## ")[1:]
    STOP = "的了是在有和与就也都啊吧吗呢把对从被让向往哪些什么怎么多少这那他她它我你您会能可以很过要请帮"
    clean = "".join(ch for ch in question if ch not in STOP)
    scores = []
    for c in chunks:
        score = 0
        for ch in clean:
            if ch in c:
                score += 1
        scores.append((score, c))
    scores.sort(reverse=True)
    return "\n\n".join(c.strip() for _, c in scores[:2])
# 注册表：工具名 → (函数, 描述, 参数 schema)
TOOL_REGISTRY = {
    "get_time": (get_time, "获取当前的日期和时间（精确到秒），用于回答'现在几点'类问题。", {"type": "object", "properties": {}}),
    "get_date": (get_date, "获取今天的日期（不含时间），用于回答'今天几号'类问题。", {"type": "object", "properties": {}}),
    "hours_after": (hours_after, "计算从现在起 n 小时后的具体日期和时间。凡涉及'再过几小时/几天是何时'的问题，必须调用此工具，禁止心算。",  {"type": "object", "properties": {"n": {"type": "integer", "description": "往未来推的小时数"}}, "required": ["n"]}),
    "search_resume": (search_resume, "检索简历主人（陈奕先）的个人知识库，返回相关资料段落。凡是询问简历主人的教育背景、专业技能、项目经历、工作或实习经历、联系方式、交付文档等任何个人信息的问题，都必须先调用此工具获取资料，再依据资料回答；用户提到的任何缩写词或专业术语（如 FDE、RAG、DTY），也必须先调用此工具查证其在简历主人语境中的含义；严禁不调用此工具就凭模型记忆回答。", {"type": "object", "properties": {"question": {"type": "string", "description": "用户的问题原文"}}, "required": ["question"]}),
}


def build_tools_json():
    """从注册表自动生成交给模型的工具说明书——改函数即同步，绝不脱节。"""
    out = []
    for name, (fn, desc, schema) in TOOL_REGISTRY.items():
        out.append({"type": "function", "function": {"name": name, "description": desc, "parameters": schema}})
    return out


def ask_ai(messages, tools):
    """调智谱 GLM：messages 是完整对话历史，tools 是工具说明书。"""
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


class Agent:
    def __init__(self, resume=False):
        self.tools = build_tools_json()
        # 记忆：以 system 开局；resume=True 时从磁盘载入上次的对话历史
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if resume:
            self.messages += self._load_memory()

    def chat(self, user_text):
        """一轮用户提问 → 多轮工具循环 → 返回最终自然语言回答。"""
        self.messages.append({"role": "user", "content": user_text})
        for _ in range(6):  # 主循环护栏：最多 6 轮，防模型跑飞
            msg = ask_ai(self.messages, self.tools)
            if not msg.get("tool_calls"):  # 不再点单 → 收尾
                self.messages.append(msg)
                return msg["content"]
            self.messages.append(msg)
            for tc in msg["tool_calls"]:  # 模型点单 → 本地执行 → 喂回
                name = tc["function"]["name"]
                fn, _, _ = TOOL_REGISTRY.get(name, (None, None, None))
                args = json.loads(tc["function"]["arguments"])
                result = fn(**args) if fn else f"未知工具：{name}"
                print(f"  [模型点单] {name} → 本地执行，结果：{result}")
                self.messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
        return "（已达最大轮数，强制结束）"

    # ── 记忆持久化：把对话历史存盘，下次 resume 能接着聊 ──
    def save_memory(self, path="agent_memory.json"):
        history = [m for m in self.messages if m["role"] != "system"]  # 不存 system，避免重复堆叠
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"  [记忆] 已保存 {len(history)} 条对话到 {path}")

    def _load_memory(self, path="agent_memory.json"):
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def demo():
    print("=== 演示 1：多轮对话 + 工具调用 ===")
    a = Agent()
    print("用户：现在几点了？")
    print("Agent：", a.chat("现在几点了？"))
    print("用户：那今天几号？")
    print("Agent：", a.chat("那今天几号？"))
    a.save_memory()

    print("\n=== 演示 2：记忆持久化（新 Agent 载入刚才的对话）===")
    b = Agent(resume=True)
    print("用户：我刚才都问了什么？")
    print("Agent：", b.chat("我刚才都问了什么？"))


def repl():
    print("进入交互式 Agent（输入 exit 退出）")
    a = Agent()
    while True:
        try:
            q = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit", "退出"):
            a.save_memory()
            break
        if not q:
            continue
        print("Agent：", a.chat(q))


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        repl()
