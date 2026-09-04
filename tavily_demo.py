"""Tavily 能力演示：search / qna_search / get_search_context / extract 的区别"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tavily import TavilyClient

from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)

query = "FastAPI 是什么"
url = "https://fastapi.tiangolo.com/"

print("=" * 56)
print("1) search —— 网页搜索：返回链接+标题+摘要的列表")
print("=" * 56)
r = client.search(query=query, max_results=2)
print("返回的顶层键:", list(r.keys()))
for item in r["results"]:
    print("-", item["title"], "|", item["url"][:50])

print("\n" + "=" * 56)
print("2) qna_search —— 搜索后直接生成一段答案（省得再调 LLM）")
print("=" * 56)
ans = client.qna_search(query=query, max_results=3)
print("答案:", str(ans)[:200])

print("\n" + "=" * 56)
print("3) get_search_context —— 返回给 LLM 用的精简上下文格式")
print("=" * 56)
ctx = client.get_search_context(query=query, max_results=2)
print("类型:", type(ctx).__name__, "| 内容:", str(ctx)[:250])

print("\n" + "=" * 56)
print("4) extract —— 直接抓取指定 URL 的页面内容（不需要搜索）")
print("=" * 56)
ex = client.extract(urls=[url])
results = ex.get("results", []) if isinstance(ex, dict) else []
if results:
    print("标题:", str(results[0].get("title"))[:80])
    print("正文前 200 字:", str(results[0].get("raw_content"))[:200])
else:
    print("extract 返回:", str(ex)[:300])
