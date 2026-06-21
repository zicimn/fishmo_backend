from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from config import Base


class Announcement(Base):
    __tablename__ = "announcement"

    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    title:Mapped[str] = mapped_column(String(255),nullable=True,comment="标题")
    content:Mapped[str] = mapped_column(Text,nullable=True,comment="内容")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment="发布时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
