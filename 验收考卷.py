# -*- coding: utf-8 -*-
"""A计划验收考试·基线卷（检索v1）：10题×四维8分制，跑完生成人工判分底稿
纪律：每题独立新会话（控制变量，P3 同款）；判分靠人，脚本只是记录员"""
from agent import Agent
from datetime import datetime

QUESTIONS = [
    ("K1", "知识题", "简历主人叫什么名字？毕业于哪所学校、什么专业？"),
    ("K2", "知识题", "他掌握哪些与 AI 相关的技能？"),
    ("K3", "知识题", "他在云服务器上部署过什么平台？独立解决过哪类故障？"),
    ("K4", "知识题", "他的 RAG 项目叫什么名字？评测结果如何？"),
    ("K5", "知识题", "他手搓的 Agent 有哪些核心组件？"),
    ("K6", "知识题", "他给 Agent 设计的评测考卷覆盖哪几类题？分数是怎么变化的？"),
    ("K7", "知识题", "他实习过的公司是哪家？担任什么岗位？"),
    ("T8", "陷阱题", "他的高考分数是多少？"),
    ("T9", "陷阱题", "他通过大学英语四六级了吗？"),
    ("T10", "陷阱题", "他期望的薪资是多少？"),
]

lines = [
    "# A 计划验收考试·基线卷（检索v1）", "",
    f"运行时间：{datetime.now():%Y-%m-%d %H:%M:%S}",
    "判分口径：P3 同款四维 × 10 题（事实准确2 / 拒答边界2 / 引用依据2 / 表达格式2 = 每题 8 分，满分 80）",
    "预期：K1-K7 应依据知识库作答；T8-T10 知识库无此信息，应明确拒答（说不知道/资料没有）",
    "对照基线：P3 Dify 版 RAG 实测 80/80（同口径）", "",
]

for qid, qtype, q in QUESTIONS:
    a = Agent()                       # 每题独立新会话——控制变量
    start = len(a.messages)
    answer = a.chat(q)
    calls = [tc["function"]["name"] for m in a.messages[start:] for tc in m.get("tool_calls", [])]
    lines.append(f"## {qid}（{qtype}）")
    lines.append(f"**问题**：{q}")
    lines.append(f"**工具轨迹**：{calls if calls else '（零调用）'}")
    lines.append(f"**Agent 回答**：{answer}")
    lines.append(f"**人工判分（0-8）**：____")
    lines.append("")

open("验收报告-基线卷-检索v1.md", "w", encoding="utf-8").write("\n".join(lines))
print("考卷跑完：验收报告-基线卷-检索v1.md 已生成（10 题底稿，待人工判分）")
