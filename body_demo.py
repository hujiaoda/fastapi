from pydantic import BaseModel
from fastapi import FastAPI, HTTPException


app = FastAPI()

# 内存"数据库"：先用字典存（学概念），以后换 SQLite/MySQL
db = {123: {"name": "Foo", "price": 50.2}, 456: {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2}}


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class LoginData(BaseModel):
    username: str
    password: str


users={}

@app.post("register")
async def register(data: LoginData):
    users[data.username] = data.password
    return {"message": "注册成功"}

@app.post("/login")
async def login(data: LoginData):
    if users.get(data.username) != data.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"message": "登录成功"}

@app.get("/login/{username}")
async def get_login(username: str):
    if username not in users:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"username": username}

@app.post("/items/{item_id}")
async def create_item(item_id: int, item: Item):
    db[item_id] = item          # ← 关键：把数据存起来！
    return {"ok": True, "item": db[item_id]}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="没有这个商品")
    return db[item_id]
