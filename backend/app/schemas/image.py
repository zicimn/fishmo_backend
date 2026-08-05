# 文件: app/schemas/image.py
# 图片压缩请求模型（/api/tools/compression）

from typing import List

from pydantic import BaseModel


class imageItem(BaseModel):
    images:List[str]
    quality:int | None = 85
    style:str | None = "webp"
