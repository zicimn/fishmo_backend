import base64
import io
import os
from PIL import Image
from typing import List

# 格式映射表
FORMAT_MAP = {
    "webp": {"format": "WEBP", "mime": "image/webp", "ext": "webp"},
    "png": {"format": "PNG", "mime": "image/png", "ext": "png"},
    "jpg": {"format": "JPEG", "mime": "image/jpeg", "ext": "jpg"},
    "jpeg": {"format": "JPEG", "mime": "image/jpeg", "ext": "jpg"},
    "gif": {"format": "GIF", "mime": "image/gif", "ext": "gif"},
}

def convert_to_webp(image: str, quality: int = 85, style: str = "webp") -> str:
    """将单个图片转换为指定格式"""
    if not image:
        return image
    
    style = style.lower().strip()
    fmt_info = FORMAT_MAP.get(style, FORMAT_MAP["webp"])
    
    
    # 解析 base64
    if ',' in image:
        data = image.split(',')[1]
    else:
        data = image
    
    image_bytes = base64.b64decode(data)
    img = Image.open(io.BytesIO(image_bytes))
    
    # 处理颜色模式
    if style in ("png", "gif") and img.mode in ('RGBA', 'LA', 'P'):
        # PNG/GIF 保留透明通道
        pass
    else:
        # 其他格式转 RGB（JPEG 不支持透明）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 透明背景转白色背景（或黑色）
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        else:
            img = img.convert('RGB')
    
    # 保存为指定格式
    output = io.BytesIO()
    
    save_kwargs = {"format": fmt_info["format"]}
    
    # 不同格式的特殊参数
    if fmt_info["format"] == "WEBP":
        save_kwargs.update({"quality": quality, "method": 6, "optimize": True})
    elif fmt_info["format"] == "JPEG":
        save_kwargs.update({"quality": quality, "optimize": True})
    elif fmt_info["format"] == "PNG":
        save_kwargs.update({"optimize": True})
    
    img.save(output, **save_kwargs)
    
    encoded = base64.b64encode(output.getvalue()).decode('utf-8')
    return f"data:{fmt_info['mime']};base64,{encoded}"


def convert_images_to_webp(images: List[str], quality: int = 85, style: str = "webp") -> List[str]:
    """批量转换图片"""
    if not images:
        return []
    
    results = []
    for image in images:
        try:
            results.append(convert_to_webp(image, quality, style))
        except Exception as e:
            print(f"转换失败: {e}")
            results.append(image)  # 失败保留原图
    
    return results






# def convert_to_webp(image:str,quality:int = 85,style:str = "webp")->str:
#     """将单个图片转换为webp格式"""
#     if not image:
#         return image
    
#     if ',' in image:
#         data = image.split(',')[1]
#     else:
#         data = image
    
#     image_bytes = base64.b64decode(data)
#     img = Image.open(io.BytesIO(image_bytes))

#     if img.mode in ('RGBA','LA','P'):
#         img = img.convert('RGBA')
#     else:
#         img = img.convert('RGB')

#     output = io.BytesIO()
#     img.save(output,format='WEBP',quality=quality, method=6, optimize = True )
#     webp_byte = output.getvalue()

#     webp_base64 = base64.b64encode(webp_byte).decode('utf-8')
#     return f"data:image/webp;base64,{webp_base64}"


# def convert_images_to_webp(images: List[str], quality: int = 85) -> List[str]:
#     """将图片列表转换为webp格式"""
#     if not images:
#         return []
    
#     webp_images = []
#     for image in images:
#         try:
#             webp_image = convert_to_webp(image, quality)
#             webp_images.append(webp_image)
#         except Exception as e:
#             print(f"转换图片失败: {e}")
#             # 如果转换失败，保留原图
#             webp_images.append(image)
    
#     return webp_images