"""C9 Step3b：给注入测试副本建向量库——kb_inject_test.txt → resume_vectors_test.json
与 embed_kb.py 同逻辑，但读写指向测试副本，真身向量库不动。"""
import json
from search_test import _embed

text = open("kb_inject_test.txt", encoding="utf-8").read()
chunks = text.split("## ")[1:]
out = []
for i, c in enumerate(chunks, 1):
    title = c.splitlines()[0]
    print(f"[{i}/{len(chunks)}] 向量化：{title}")
    out.append({"text": c, "vector": _embed(c)})

json.dump(out, open("resume_vectors_test.json", "w", encoding="utf-8"), ensure_ascii=False)
print(f"\n测试向量库已保存: resume_vectors_test.json（{len(out)} 块）")
