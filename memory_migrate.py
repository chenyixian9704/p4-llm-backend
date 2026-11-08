# -*- coding: utf-8 -*-
"""一次性迁移：agent_memory.json → SQLite memory 表"""
import sqlite3, json

msgs = json.load(open("agent_memory.json", encoding="utf-8"))   # 读旧格式
print(f"旧记忆共 {len(msgs)} 条消息")

conn = sqlite3.connect("chats.db")
cur = conn.cursor()

# 建表（和 init_db.py 里的 memory 表定义保持一致）
cur.execute("""CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime'))
)""")

for m in msgs:                                                  # 逐条搬运
     cur.execute("INSERT INTO memory (role, content) VALUES (?, ?)",
                (m["role"], m["content"]))
conn.commit()

for row in cur.execute("SELECT id, role, content FROM memory"): # 验证：全读出来
    print(row)
conn.close()
