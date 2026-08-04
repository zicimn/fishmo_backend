from sqlalchemy import Index, ForeignKey,DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from config import Base


class Favorite(Base):
    __tablename__ = "favorite"
    __table_args__ = (
        Index("idx_user_article", "user_id", "article_id", unique=True),
        {"comment": "收藏表"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )
    
    article_id: Mapped[int] = mapped_column(
        ForeignKey("article.id", ondelete="CASCADE"),
        nullable=False,
        comment="文章ID"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="收藏时间"
    )