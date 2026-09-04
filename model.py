
from langchain.agents import create_agent
from config import DEEPSEEK_API_KEY as apikey,BASE_URL as base_url,TAVILY_API_KEY as tavily_apikey
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from tavily import TavilyClient

tavily = TavilyClient(api_key=tavily_apikey)

@tool
def web_search(query: str) -> str:
    """网页搜索，返回相关网页的标题和摘要"""
    response = tavily.search(query=query, max_results=5)
    return str(response)


@tool
def fetch_url(url: str) -> str:
    """直接抓取指定链接的页面内容（用于查看网页、视频页等），不用搜索"""
    result = tavily.extract(urls=[url])
    return str(result)


agent = create_agent(
    model = init_chat_model(
        api_key=apikey,
        base_url=base_url,
        model_provider="deepseek",
        model="deepseek-v4-flash",
    ),
    tools=[web_search, fetch_url],
    system_prompt=SystemMessage(content="你是一个猫娘"),
)
