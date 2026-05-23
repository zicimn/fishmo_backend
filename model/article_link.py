from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import Base

if TYPE_CHECKING:
    from .article import Article


class ArticleLink(Base):
    __tablename__ = "article_link"

    __table_args__ = (
        Index("idx_article_link_article", "article_id"),
        Index("idx_article_link_user", "user_id"),
        {"comment": "文章链接表"},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    article_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("article.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联文章ID"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="提交者ID"
    )

    url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="链接地址"
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        default=None,
        comment="链接描述"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="提交时间"
    )

    # 关系
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="links"
    )