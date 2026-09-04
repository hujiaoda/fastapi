# FastAPI 学习仓库

从零学 FastAPI 的动手代码仓库：路径/查询参数、请求体、pydantic 校验、CRUD、依赖注入、APIRouter 模块化，
外加一个"FastAPI 接口 + DeepSeek agent"的 AI 问答小功能。

## 快速开始

1. 创建 `.env`（密钥不入库，参考 `config.py` 需要的变量）：

   ```
   DEEPSEEK_API_KEY=sk-xxx
   QWEN_API_KEY=sk-xxx
   TAVILY_API_KEY=tvly-xxx
   ```

2. 安装依赖：

   ```bash
   pip install fastapi uvicorn pydantic python-dotenv langchain langchain-openai langchain-deepseek tavily-python
   ```

   （国内连不上 PyPI 时加清华镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple`）

3. 启动某个 demo（一次一个，都占 8000 端口）：

   ```bash
   python -m uvicorn Fastapi_path:app --reload   # 路径/查询参数 + AI 问答
   python -m uvicorn body_demo:app --reload      # 请求体 CRUD（内存存储）
   python -m uvicorn main:app --reload           # APIRouter 模块化（users / art）
   ```

4. 浏览器打开 `http://127.0.0.1:8000/docs`（FastAPI 自动文档），或用仓库里的 `.http` 文件测试

## 文件清单

| 文件 | 内容 |
|---|---|
| `Fastapi_path.py` | 路径参数（ge/le 约束）、查询参数、AI 问答接口 `/ask_me` |
| `model.py` | DeepSeek agent：`web_search`（Tavily 搜索）+ `fetch_url`（Tavily extract 抓链接） |
| `pydantic_demo.py` | pydantic 基础：BaseModel / 类型校验 / model_dump |
| `body_demo.py` | 请求体 CRUD：POST 存数据 → GET 读数据（内存字典），含登录雏形 |
| `depends_demo.py` | 依赖注入：公共分页参数 + token 校验 |
| `Routers/users.py` | APIRouter 示例：用户列表 / 详情 / 按年龄性别筛选 |
| `Routers/article.py` | APIRouter 示例：文章列表 / 详情 / 购买 |
| `main.py` | 装配入口：include_router 挂载 users 和 art |
| `tavily_demo.py` | Tavily 能力演示：search / qna_search / get_search_context / extract |
| `config.py` | 从 `.env` 读取 API 密钥（不含密钥本身） |
| `test_*.http` | VS Code REST Client 测试文件（对应不同 app） |

## 已学知识点

| 主题 | 内容 |
|---|---|
| 传参 | 路径参数（标识资源）/ 查询参数（筛选选项）/ body（提交内容） |
| pydantic | 请求体自动解析 + 校验 + 422；类型自动转换；必填/可选/默认值 |
| CRUD | POST=创建、GET=读取，内存字典存储（重启丢失） |
| 依赖注入 | `Depends` 抽公共参数/登录校验，接口复用 |
| APIRouter | 按业务域拆文件 + `prefix` 自动加前缀 + `tags` 文档分组 + `include_router` 装配 |
| AI 接入 | DeepSeek agent 作为 FastAPI 接口后端，工具决定能力边界 |
| 测试 | `/docs` 可视化测试 + `.http` 文件模拟真实请求 |

## 踩坑速查（都真实踩过）

1. 文件名别叫 `pydantic.py` / `fastapi.py`（会遮蔽同名库）
2. `from datetime import datetime`（不是 `from time import`）
3. 路径参数用 `Path()`，查询参数用 `Query()`——用错参数会被静默忽略
4. `@tool` 对象不能直接调用，用 `.invoke()` 或交给 agent
5. FastAPI 进程里 `create_agent(debug=True)` 会在 GBK 终端崩溃（UnicodeEncodeError）
6. LangChain 消息是对象：用 `.content`，不是 `["content"]`
7. URL 路径参数转成 int 后，别拿字符串键去比对（`"123"` ≠ `123`）
8. `dict.values()` 是视图对象：能遍历不能下标，取字段要 `[u["name"] for u in info.values()]`
9. APIRouter 的 `prefix` 会拼在真实 URL 前，测试/访问别漏前缀
10. `.http` 文件每个请求块用 `###` 分隔，否则解析错乱

## 下一步（个人计划）

- `response_model`：约束返回格式（防止密码等内部字段泄漏）
- SQLite：把内存字典换成持久化数据库
- 前端 fetch：HTML 页面调用接口，形成完整前后端闭环
