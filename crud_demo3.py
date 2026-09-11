"""crud_demo3：关系查询 / N+1 对照 / 进阶查询 演示

运行：在 C:\\Users\\28401\\FastAPI 目录下执行  python crud_demo3.py
第一次运行会自动造一点演示数据（1 个用户 + 6 篇文章 + 标签）。
engine 开着 echo=True，SQL 会刷屏打印，这是正常的，请留意每段结尾统计的条数。
"""

import asyncio
import sys

from sqlalchemy import event, select
from sqlalchemy.orm import selectinload

from Routers.db import SessionFactory, engine
from Routers.user import Article, Tag, User

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 数一数“真的执行了几条 SQL”
sql_count = {"n": 0}


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _count_sql(conn, cursor, statement, parameters, context, executemany):
    sql_count["n"] += 1


async def seed_demo_data():
    """造数据：query_demo 用户 + 6 篇文章 + Python/FastAPI/SQLAlchemy 三个标签"""
    async with SessionFactory() as db:
        user = await db.scalar(select(User).where(User.username == "query_demo"))
        if user is None:
            user = User(username="query_demo", email="query_demo@aa.com", password="123456")
            db.add(user)
            await db.flush()  # 先拿到 user.id

        # 已经有文章就不再重复造
        has_articles = await db.scalar(
            select(Article.id).where(Article.author_id == user.id).limit(1)
        )
        if has_articles:
            return
        tags = []
        for name in ["Python", "FastAPI", "SQLAlchemy"]:
            tag = await db.scalar(select(Tag).where(Tag.name == name))
            if tag is None:
                tag = Tag(name=name)
                db.add(tag)
                await db.flush()
            tags.append(tag)

        for i in range(1, 7):
            db.add(
                Article(
                    title=f"demo 文章 {i}",
                    content="内容占位" * 5,
                    author_id=user.id,
                    tags=tags[: (i % 3) + 1],  # 第 1 篇挂 2 个标签、第 2 篇挂 3 个……
                )
            )
        await db.commit()
        print("已造好演示数据")


async def demo_relationship():
    print("\n===== ① 关系查询：提前说好要带出 author 和 tags =====")
    async with SessionFactory() as db:
        # 异步里不能"用到关系时再查"（会报 MissingGreenlet），
        # 所以必须在 select 时用 options(selectinload(...)) 提前说好要一起取出
        sql_count["n"] = 0
        stmt = (
            select(Article)
            .options(selectinload(Article.author), selectinload(Article.tags))
            .order_by(Article.id)
            .limit(1)
        )
        article = await db.scalar(stmt)
        if article is None:
            print("没有文章")
            return

        print(f"文章：{article.title}")
        print(f"作者：{article.author.username}")
        print(f"标签：{[t.name for t in article.tags]}")
        print(f"→ 一共发了 {sql_count['n']} 条 SQL：author 和 tags 都在这几条里取回来了")
        print("  （之后的打印没有再发 SQL，因为数据已经装进内存）")


async def demo_n_plus_1():
    print("\n===== ② N+1 对照：逐个查作者 vs selectinload 一次全查 =====")
    async with SessionFactory() as db:
        # 笨办法：先查文章，再在循环里按 author_id 一个一个查作者
        articles = (await db.scalars(select(Article).order_by(Article.id))).all()
        sql_count["n"] = 0
        for a in articles:
            # 每篇开一个"独立会话"去查作者，模拟真实项目里
            # "每个请求/每次用到关系时各自查一次"的样子。
            # 注意：如果在同一个会话里反复查同一个作者，SQLAlchemy 会用
            # 身份映射缓存住对象，第二次就不发 SQL 了——所以 N+1 在
            # 作者各不相同时最明显，演示里用独立会话排除这个干扰。
            async with SessionFactory() as db2:
                author = await db2.get(User, a.author_id)  # 每篇单独查一次
                _ = author.username
        print(
            f"笨办法：{len(articles)} 篇文章 → 循环里发了 {sql_count['n']} 条 SQL"
            f"（再加上开头查文章那 1 条，共 {sql_count['n'] + 1} 条）"
        )

        # 聪明办法：selectinload 让数据库一次性把所有作者都查回来
        sql_count["n"] = 0
        stmt = select(Article).options(selectinload(Article.author)).order_by(Article.id)
        articles2 = (await db.scalars(stmt)).all()
        for a in articles2:
            _ = a.author.username  # 数据已经在内存里，不会再发 SQL
        print(f"selectinload：{len(articles2)} 篇文章 → 一共只发了 {sql_count['n']} 条 SQL")


async def demo_advanced_query():
    print("\n===== ③ 进阶查询：where / order_by / 分页 =====")
    async with SessionFactory() as db:
        # where 的返回：满足条件的 User 对象列表
        users = (
            await db.scalars(
                select(User).where(User.username.contains("demo")).order_by(User.id)
            )
        ).all()
        print(f"where 返回的是列表，里面每个是 User 对象：{[(u.id, u.username) for u in users]}")

        # 只想要第一条：用 scalar 而不是 scalars().all()
        one = await db.scalar(select(User).where(User.username == "query_demo"))
        print(f"scalar 只拿一条：id={one.id} username={one.username}")

        # order_by：不排队时数据库返回顺序不确定，排了才有稳定顺序
        asc_ids = (await db.scalars(select(Article.id).order_by(Article.id))).all()
        desc_ids = (await db.scalars(select(Article.id).order_by(Article.id.desc()))).all()
        print(f"order_by 升序：{list(asc_ids)}")
        print(f"order_by 降序：{list(desc_ids)}")

        # 分页：每页 2 条，offset 表示跳过几条
        page1 = (
            await db.scalars(
                select(Article.id).order_by(Article.id).offset(0).limit(2)
            )
        ).all()
        page2 = (
            await db.scalars(
                select(Article.id).order_by(Article.id).offset(2).limit(2)
            )
        ).all()
        page3 = (
            await db.scalars(
                select(Article.id).order_by(Article.id).offset(4).limit(2)
            )
        ).all()
        print(f"第 1 页（跳过 0 条取 2 条）：{list(page1)}")
        print(f"第 2 页（跳过 2 条取 2 条）：{list(page2)}")
        print(f"第 3 页（跳过 4 条取 2 条）：{list(page3)}")


async def main():
    await seed_demo_data()
    await demo_relationship()
    await demo_n_plus_1()
    await demo_advanced_query()
    await engine.dispose()  # 关掉连接池，避免退出时告警


if __name__ == "__main__":
    asyncio.run(main())
