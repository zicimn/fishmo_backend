from pydantic import BaseModel,EmailStr,Field,field_validator
from typing import List, Optional
from datetime import datetime
from model import Article

class Account(BaseModel):
    name:str = Field(min_length=2,max_length=20)
    password:str = Field(min_length=8,max_length=20)
    email:EmailStr = Field(description="邮箱需要以@qq.com结尾")

    @field_validator('email')
    @classmethod
    def verify_email_end(cls,v:str)->str:
        if not v.endswith('@qq.com'):
            raise ValueError("邮箱需要以@qq.com结尾")
        return v

class Update_request(BaseModel):
    new_username:str | None = None
    new_email:EmailStr | None =Field(None,description="邮箱需要以@qq.com结尾") 
    new_password:str | None = None
    new_bio:str | None = None
    new_avator:str|None = None

    @field_validator('new_email')
    @classmethod
    def verify_email_end(cls,v:str|None)->str|None:
        if not v.endswith('@qq.com') and v is not None:
            raise ValueError("邮箱需要以@qq.com结尾")
        return v

class Post(BaseModel):
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

    class Config:
        from_attributes = True

class ArticleList(BaseModel):
    total : int
    items : List[ArticleItem]

class LoginRequest(BaseModel):
    username: str
    password: str

class ArticleEdit(BaseModel):
    title:str | None = None
    category:str | None = None
    content:str | None = None
    images:List[str] | None = None
    
class LinkRequest(BaseModel):
    url : str
    title : str | None = None

class CommentItem(BaseModel):
    name:str
    content:str
    created_at:datetime

class CommentList(BaseModel):
    comments:List[CommentItem]


class UpdateAvatar(BaseModel):
    avatar:str

class imageItem(BaseModel):
    images:List[str]
    quality:int | None = 85
    style:str | None = "webp"


SORTABLE_FIELDS = {
    "created_at": Article.created_at,
    "views": Article.views,
    "likes": Article.likes
}

