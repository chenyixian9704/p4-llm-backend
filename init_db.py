# -*- coding: utf-8 -*-
"""Step 1：初始化对话历史库——建 chats.db + chats 表"""
import sqlite3                                  # Python 自带，零安装

conn = sqlite3.connect("chats.db")              # 连库：文件不存在会自动创建
cur = conn.cursor()                             # 光标：SQL 由它代发

# 建表（三引号里的内容原样发给 SQLite；SQL 注释用 --）
cur.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,       -- 主键：每行的身份证号，自动+1
    question TEXT NOT NULL,                     -- 问题（文本，不许为空）
    answer TEXT NOT NULL,                       -- 回答
    created_at TEXT DEFAULT (datetime('now','localtime'))  -- 落库时间，自动填
)
""")

conn.commit()                                   # 提交：写操作必须 commit 才落盘
cur.close()
conn.close()
print("chats.db 建好，chats 表就位")
