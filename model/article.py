from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import Base

if TYPE_CHECKING:
    from .article_link import ArticleLink
    from .comment import Comment

if TYPE_CHECKING:
    from .article_link import ArticleLink
    from .comment import Comment

from .article_link import ArticleLink
from .comment import Comment


class Article(Base):
    __tablename__ = "article"
    __table_args__ = (
        Index("idx_author", "author_id"),
        Index("idx_category", "category"),
        Index("idx_created", "created_at"),
        {"comment": "文章表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="标题")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="作者ID")
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    images: Mapped[Optional[List[str]]] = mapped_column(JSON, default=None, comment="图片URL数组")
    views: Mapped[int] = mapped_column(Integer, default=0, comment="浏览量")
    likes: Mapped[int] = mapped_column(Integer, default=0, comment="点赞量")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="发布时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 关联关系
    links: Mapped[List["ArticleLink"]] = relationship(
        "ArticleLink", back_populates="article", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="article", cascade="all, delete-orphan"
    )


