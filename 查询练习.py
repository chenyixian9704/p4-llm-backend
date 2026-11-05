# -*- coding: utf-8 -*-
"""Step 3 查询练习：三板斧四连跑"""
import sqlite3

conn = sqlite3.connect("chats.db")

print("=== Q1 · WHERE 精筛：11-02 当天 ===")
for row in conn.execute("SELECT question, answer FROM chats WHERE created_at LIKE '2026-11-02%'"):
    print(row)

print("\n=== Q2 · ORDER BY + LIMIT：最新 3 条 ===")
for row in conn.execute("SELECT question, created_at FROM chats ORDER BY created_at ASC LIMIT 3"):
    print(row)

print("\n=== Q3 · LIKE 模糊搜：问题里含'什么' ===")
for row in conn.execute("SELECT question FROM chats WHERE question LIKE '%什么%'"):
    print(row)

print("\n=== Q4 · GROUP BY + COUNT：每天对话数 ===")
for row in conn.execute("SELECT substr(created_at, 1, 10) AS 日期, COUNT(*) AS 条数 FROM chats GROUP BY substr(created_at, 1, 10)"):
    print(row)

conn.close()
