# -*- coding: utf-8 -*-
"""切块实验：把简历知识库按 ## 小节切成块——RAG 检索的最小单位就是块"""

text = open("resume_kb.txt", encoding="utf-8").read()   # 读全文；encoding 别忘（P4.2 老课：不写=乱码）

chunks = text.split("## ")[1:]   # 按 "## " 切开；[1:] 丢掉第一个空块（文件开头在第一个标记之前）

print(f"共切成 {len(chunks)} 块")
print("-" * 30)
for i, c in enumerate(chunks):
    title = c.split("\n")[0].strip()          # 每块的第一行 = 小节标题
    print(f"[块{i}] {title}（{len(c)} 字）")
