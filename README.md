# P4 迷你 LLM 后端（Mini LLM Backend）

> 零基础起步的第一个后端项目：亲手调大模型 API → 包装成 HTTP 服务 → 跑通 agent 循环。
> 环境约束：8GB 内存 Windows 笔记本，**零基础设施**（不用 Docker，不占服务器）。

## 需求

P3 里我是 Dify 平台用户：填提示词、点对话框，模型对我是个黑盒。
P4 的目标是打开这个黑盒，回答三个问题：

1. 平台背后到底怎么调大模型？（API 直调）
2. "别人的服务"是怎么做出来的？（HTTP 后端）
3. Agent 的工作循环底层长什么样？（tool calling）

## 做了什么

| 文件 | 能力 |
|---|---|
| `first_call.py` | ① 直调智谱 GLM API（key 鉴权 → JSON 请求 → 拆响应）；② 重构为 `ask_ai(question)` 可复用函数；③ 直接运行时带演示 |
| `server.py` | FastAPI + uvicorn：`POST /chat` 收 `{"question": ...}` → 调 `ask_ai` → 返回 `{"answer": ...}`；自带 `/docs` 交互文档 |
| `tool_call.py` | tool calling 完整循环：给模型 `get_time` 工具说明书 → 模型点单 → 本地执行 → `role: tool` 喂回 → 自然语言最终回答 |
| `agent.py` | **完整手搓 Agent**：system prompt + 多工具注册表（TOOL_REGISTRY）+ 记忆持久化（agent_memory.json，resume 续聊）+ 多轮循环护栏（最多 6 轮）。`python agent.py` 交互，`python agent.py --demo` 跑内置多轮+记忆演示 |

## 踩了什么坑（每条都是真实排障时间）

1. **WindowsApps 占位符冒充 python**——敲 `python --version` 无输出。`Get-Command python` 验源定位：假货在 PATH 里排队靠前。
2. **装完 Python 不生效**——终端是 VS Code 的子进程，父进程环境不刷新，开多少新终端都白搭。解法：重启整个 VS Code。
3. **全角括号 U+FF08**——中文输入法敲代码第一大敌。`SyntaxError: invalid character`，报错里的 (U+FF08) 就是字符的身份证号。
4. **`.env` 被 Replace 弹窗用空文件覆盖**——key 丢失。靠迁移备份 10 分钟找回。"重要数据必须有备份"在自家项目里应验。
5. **当前目录决定一切**——`.env` 建进过 C 盘用户目录；终端站在哪个文件夹，命令就在哪找文件。跑文件前先瞄提示符。
6. **代码粘进终端 = 报错**——终端下命令，编辑器写代码，分工不能乱。
7. **git 合并冲突实战**——pull 撞上本地未提交草稿：stash 收口袋 → 冲突块逐个 Accept Current → 识别 CRLF 假差异（97 行进 97 行出，`--ignore-cr-at-eol` 验证）。

## 结果

- ✅ 三层能力全部跑通：API 直调 → HTTP 服务（/docs 实测 200）→ tool calling 循环
- ✅ 关键认知：**模型出主意，代码动手**；Agent = 模型（大脑）+ 工具（手脚）+ 循环（决策→执行→反馈）
- ✅ 最有纪念意义的瞬间：在自己写的后端里问"一句话说明什么是后端"，AI 答了——用后端定义了后端

## 面试 QA 速答

**Q：大模型 API 调用的完整链路？**
key 鉴权（Authorization: Bearer）→ 组装 JSON 请求体（model + messages）→ 响应 JSON 里 `choices[0].message.content` 拆出正文。

**Q：密钥这类敏感信息怎么管理？**
.env 与代码分离 + .gitignore 双闸门（本项目真实拦截过一次差点入库）+ 密钥不进聊天记录。

**Q：什么是 Agent？和聊天机器人什么区别？**
聊天机器人一问一答；Agent 是循环——模型判断该用什么工具，代码执行，结果喂回，模型再组织答案。我在本项目的 tool_call.py 里跑通了这个最小循环；P3 的 Dify 工作流就是这个循环的可视化编排——平台版和代码版我都上过手。

**Q：前后端怎么交互？**
现挂自己的接口讲：POST /chat，请求体 {"question": ...}，FastAPI 路由到处理函数，调 GLM 后以 {"answer": ...} 返回，状态码 200。

## 运行方式

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests python-dotenv fastapi uvicorn
# 项目目录放 .env 文件，内容：ZHIPU_API_KEY=你的key
python first_call.py        # 函数演示
uvicorn server:app          # 启动后端 → 浏览器开 http://127.0.0.1:8000/docs
python tool_call.py         # tool calling 循环演示
python agent.py --demo      # 完整 Agent：多轮对话 + 工具调用 + 记忆持久化演示
python agent.py             # 进入交互式 Agent（输入 exit 退出，自动存记忆）
```
