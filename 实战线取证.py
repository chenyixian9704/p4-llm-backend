# -*- coding: utf-8 -*-
"""实战线取证：让 Agent 真跑 K2/K6，窃听它传给检索工具的 query。

背景矛盾：预演探针（考卷检索预演v3.py，用用户原话）显示 K2 的《专业技能》
排第 1、K6 的 80/80 老家 [4] 根本没进前 2——但 11-06 卷面上的 K2 答案
偏偏含教育背景/术语表的料。两个嫌疑：
  ① 实战里检索的输入不是用户原话，是模型点单时自己写的 question 参数
  ② 生成层自由发挥（小模型把"听着像"的料从自己联想里抓来拌进答案）
本脚本把暗线录下来：模型传参原文 → 该参数实际拉回的块 → 最终回答。
对照预演 X 光片，锅在哪一层当场对号。
用法：D:/conda/python.exe 实战线取证.py
"""
import agent
from agent import Agent

TAP_LOG = []                                    # 每次检索留痕
_orig = agent.TOOL_REGISTRY["search_resume"][0]

def tapped_search_resume(question):
    """原函数照常干活，顺手把传参和返回块记到 TAP_LOG——模型无感。"""
    result = _orig(question)
    titles = [c.strip().splitlines()[0] for c in result.split("\n\n")]
    TAP_LOG.append({"query": question, "titles": titles})
    return result

# 换芯：注册表原位换窃听版（签名/返回值不变，模型无感）
agent.TOOL_REGISTRY["search_resume"] = (
    tapped_search_resume, ) + agent.TOOL_REGISTRY["search_resume"][1:]

CASES = [
    ("K2", "他掌握哪些与 AI 相关的技能？"),
    ("K6", "他给 Agent 设计的评测考卷覆盖哪几类题？分数是怎么变化的？"),
]
RUNS = 5
for r in range(1, RUNS + 1):
    print("#" * 62)
    print(f"########## 第 {r}/{RUNS} 轮 ##########")
    for k, q in CASES:
        TAP_LOG.clear()
        a = Agent()                                 # 每题独立新会话，与验收考卷同款
        ans = a.chat(q)
        print("=" * 62)
        print(f"=== {k}：{q}")
        if not TAP_LOG:
            print("  （零调用！模型没查知识库就作答——本身就是大发现）")
        for tap in TAP_LOG:
            print(f"\n  [模型传参] {tap['query']}")
            for t in tap["titles"]:
                print(f"    ▸ 《{t}》")
        print(f"\n  [最终回答] {ans}\n")
