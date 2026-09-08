import asyncio
from sqlalchemy import select
from Routers.db import SessionFactory
from Routers.user import User  # ← 缺的 import：ORM 模型在这里

async def create_user(username: str, email: str, password: str):
    async with SessionFactory() as session:
        try:
            async with session.begin():
                new_user = User(username=username, email=email, password=password)
                session.add(new_user)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    return new_user

async def read_user(user_id: int):
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
        if not user:
            print("User not found")
            return None
        return user

async def update_user(user_id: int, new_email: str, new_name: str):
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
        if not user:
            print("User not found")
            return None
        user.email = new_email
        user.username = new_name
        await session.commit()          # ← 少了括号
        print("Updated:", user.username, user.email)
        return user


async def delete_user(user_id: int):
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
        if not user:
            print("User not found")
            return None
        await session.delete(user)
        await session.commit()          # ← 少了括号
        print("Deleted user id:", user_id)


async def main():
    new_user = await create_user("demo_user", "demo@aa.com", "123456")
    if not new_user:
        return
    print(f"① Created: id={new_user.id} {new_user.username}")

    await read_user(new_user.id)                       # ② 读
    await update_user(new_user.id, "new@aa.com", "demo_new")  # ③ 改
    await read_user(new_user.id)                       # ④ 改完再读
    await delete_user(new_user.id)                     # ⑤ 删
    await read_user(new_user.id)                       # ⑥ 删完再读 → not found
    

if __name__ == "__main__":
    asyncio.run(main())
