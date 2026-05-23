# from datetime import datetime
# from typing import List, Optional, TYPE_CHECKING

# from sqlalchemy import String, Text, Integer, DateTime, JSON, Index
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from config import Base

# class Draft(Base):
#     __tablename__ = "draft"
#     __table_args__ = (
#         Index("idx_draft_user", "user_id"),
#         Index("idx_draft_updated", "updated_at"),
#         {"comment": "草稿表"},
#     )

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
#     title: Mapped[str] = mapped_column(String(255), nullable=False, comment="标题")
#     category: Mapped[str] = mapped_column(String(50), nullable=False, comment="分类")
#     content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
#     images: Mapped[Optional[List[str]]] = mapped_column(JSON, default=None, comment="图片URL数组")
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.now, comment="创建时间"
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
#     )

#     # 可选：关联用户（如果需要，需先定义User模型）
#     # user: Mapped["User"] = relationship("User", back_populates="drafts")