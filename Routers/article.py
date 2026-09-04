from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/art", tags=["art"])


articles = {
    1: {"title": "FastAPI入门", "content": "FastAPI是一个现代、快速（高性能）的Web框架，用于构建API，基于Python 3.6+类型提示。"},
    2: {"title": "Python基础", "content": "Python是一种广泛使用的高级编程语言，具有简洁的语法和强大的库支持。"},
    3: {"title": "数据科学", "content": "数据科学是一个跨学科领域，涉及统计学、计算机科学和领域知识，用于从数据中提取有价值的信息。"},
}

@router.get("/art_list")
async def art_list():
    return {"articles": [a["title"] for a in articles.values()]}

@router.get("/art_info/{art_id}")
async def art_info(art_id: int):
    if art_id not in articles:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article_info": articles[art_id]}

@router.get("/art_buy/{art_id}")
async def art_buy(art_id: int):
    if art_id not in articles:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": f"Successfully purchased article '{articles[art_id]['title']}'."}
