# like.py
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from config import Base


class Like(Base):
    __tablename__ = "like"
    __table_args__ = (
        UniqueConstraint("article_id", "user_id", name="uq_article_user_like"),
        {"comment": "点赞记录表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("article.id", ondelete="CASCADE"), 
        nullable=False, comment="文章ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="用户ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="点赞时间"
    )