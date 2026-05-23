from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import Base

if TYPE_CHECKING:
    from .article import Article


class Comment(Base):
    __tablename__ = "comment"

    __table_args__ = (
        Index("idx_comment_article", "article_id"),
        Index("idx_comment_user", "user_id"),
        {"comment": "评论表"},
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
        comment="评论用户ID"
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="评论内容"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="评论时间"
    )

    # 关系
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="comments"
    )