# 文件: app/schemas/article_link.py
# 文章链接相关请求模型

from pydantic import BaseModel


class LinkRequest(BaseModel):
    url : str
    title : str | None = None
