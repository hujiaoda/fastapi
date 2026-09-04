

from typing import Annotated, List
from fastapi import FastAPI, Path, Query
from model import agent


app = FastAPI()

""""
==============================
路径参数
==============================
"""
@app.get("/item/{item_id}")
async def read_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=100)]):
    return {"item_id": item_id}


""""
==============================
查询参数
==============================
"""
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(title="Query string", max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


"""
==============================
回答我
==============================
"""

@app.get("/ask_me")
async def ask(question: Annotated[str, Query(title="Your question", max_length=200)]):
    ans = agent.invoke({
        "messages":[
            {"role":"user","content":question}
        ]
    })
    return {"回复": ans["messages"][-1].content}
