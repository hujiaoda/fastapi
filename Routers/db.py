"""数据库基础设施：engine（连接池）+ SessionFactory（会话工厂）+ Base（模型登记处）

三个东西各管一件事：
- engine：和 MySQL 的连接池，程序启动建一次
- SessionFactory：每次调用生成一个新 Session（一次"通话"，干完活就关）
- Base：模型的"户口本"——所有模型类继承它，SQLAlchemy 才认识、才会建表
"""
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DB_URI


# ① engine：数据库连接池（总机），只建一次，全程复用
engine = create_async_engine(
    DB_URI,
    echo=True,           # 打印 SQL 日志：能亲眼看到 ORM 翻译出的 SQL
    pool_size=10,        # 连接池大小（最多保持 10 条线路）
    max_overflow=20,     # 不够用时最多再开 20 条
    pool_recycle=3600,   # 连接最多空闲 1 小时就回收
    pool_pre_ping=True,  # 每次用前检查连接是否还活着
)


# ② SessionFactory：会话生产机器，每次调用给你一个全新 Session
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


# ③ Base：模型登记处。所有模型继承它（class User(Base)），
# 之后 Base.metadata.create_all(engine) 就能按登记的表建到数据库里

# 命名约定：给所有约束（索引/唯一/外键/主键）起"统一格式的名字"。
# 建表时用不用都行；但 Alembic 迁移需要——否则约束名是 MySQL 随机生成的，
# 迁移脚本没法精确地删除/重建某个约束。
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",      # 索引 index
    "uq": "uq_%(table_name)s_%(column_0_name)s",        # 唯一约束 unique
    "ck": "ck_%(table_name)s_%(constraint_name)s",      # 检查约束 check
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # 外键
    "pk": "pk_%(table_name)s",          # 主键
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
