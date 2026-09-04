from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])

# 静态数据：直接读，不需要 Depends
info = {
    1: {"age": 25, "gender": "男", "name": "黎明"},
    2: {"age": 30, "gender": "男", "name": "张三"},
    3: {"age": 28, "gender": "女", "name": "李四"},
}


# Depends 的正确用途：公共筛选参数（以后多个接口共享同一套参数定义）
async def common_filter(age_max: int = 100, gender: str | None = None):
    return {"age_max": age_max, "gender": gender}

@router.get("/list")
async def user_list():
    return {"users": [u["name"] for u in info.values()]}


@router.get("/info/{user_id}")
async def user_info(user_id: int):
    # 读数据：直接用 info，不需要依赖
    if user_id not in info:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_info": info[user_id]}


@router.get("/filter")
async def filter_users(filters: dict = Depends(common_filter)):
    # 筛选才是 Depends 的用武之地：公共筛选参数 + 过滤逻辑
    result = [
        u for u in info.values()
        if u["age"] <= filters["age_max"]
        and (filters["gender"] is None or u["gender"] == filters["gender"])
    ]
    return {"users": result}
