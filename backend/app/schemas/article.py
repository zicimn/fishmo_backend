# 文件: app/schemas/article.py
# 文章相关请求/响应模型与排序字段

from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.model import Article


class Post(BaseModel):
    status:bool | None = None
    title:str
    category:str
    content:str
    images:List[str] | None = None

class ArticleItem(BaseModel):
    id:int
    title:str
    author_name:str
    category:str | None = None
    views:int
    likes:int
    create_at:datetime
    avatar:str | None = None

    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    total : int
    items : List[ArticleItem]

class ArticleEdit(BaseModel):
    status:bool
    title:str | None = None
    category:str | None = None
    content:str | None = None
    images:List[str] | None = None


SORTABLE_FIELDS = {
    "created_at": Article.created_at,
    "views": Article.views,
    "likes": Article.likes
}
