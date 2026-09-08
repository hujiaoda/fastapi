from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Routers.db import SessionFactory
from Routers.user import User

app = FastAPI()


# ---------- 传输模型：接口收/发什么数据，跟数据库表无关 ----------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    """改用户：三个字段都可选，传哪个改哪个"""
    username: str | None = None
    email: str | None = None
    password: str | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)  # 允许直接从 ORM 对象取字段


# ---------- get_db：每个请求开一个会话，请求结束自动关闭 ----------
async def get_db():
    async with SessionFactory() as session:
        yield session  # 交给接口用；接口跑完，回到这里关闭会话


@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 先查：用户名或邮箱有没有已经被占用（数据库 unique 约束是最后防线）
    if await db.scalar(select(User).where(User.username == user.username)):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if await db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    new_user = User(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.username is not None:
        user.username = payload.username
    if payload.email is not None:
        user.email = payload.email
    if payload.password is not None:
        user.password = payload.password
    await db.commit()          # 改完要 commit 才算真正落库
    await db.refresh(user)     # 刷新出数据库侧的最新值
    return user


@app.delete("/users/{user_id}", response_model=UserRead)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return user  # 对象还在内存里，只是数据库那行没了，所以还能返回 JSON

@app.get("/users/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await db.scalars(select(User))  # 把“要哪些行”交给数据库，而不是自己循环
    return users.all()
