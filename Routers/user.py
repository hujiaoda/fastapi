
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# 多对多中间表：只存"文章 ↔ 标签"的配对，不存业务数据
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    user_extension: Mapped["UserExtension"] = relationship(back_populates="user")
    articles: Mapped[list["Article"]] = relationship(back_populates="author")


class UserExtension(Base):
    __tablename__ = "user_extensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship(back_populates="user_extension")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="articles")
    tags: Mapped[list["Tag"]] = relationship(secondary="article_tags", back_populates="articles")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    articles: Mapped[list["Article"]] = relationship(secondary="article_tags", back_populates="tags")
