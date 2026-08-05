# 文件: app/schemas/user.py
# 用户相关请求/响应模型

from pydantic import BaseModel, EmailStr, Field, field_validator


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

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateAvatar(BaseModel):
    avatar:str
