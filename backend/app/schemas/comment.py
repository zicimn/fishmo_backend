# 文件: app/schemas/comment.py
# 评论相关响应模型

from datetime import datetime
from typing import List

from pydantic import BaseModel


class CommentItem(BaseModel):
    id:int
    name:str
    content:str
    created_at:datetime

class CommentList(BaseModel):
    comments:List[CommentItem]
