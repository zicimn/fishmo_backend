# 文件: app/schemas/announcement.py
# 公告相关响应模型

from datetime import datetime
from typing import List

from pydantic import BaseModel


class AnnouncementItem(BaseModel):
    id:int
    title:str
    created_at:datetime

    class Config:
        from_attributes = True


class AnnouncementList(BaseModel):
    total:int
    items:List[AnnouncementItem]
