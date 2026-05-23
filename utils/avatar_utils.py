import os
import base64
import uuid
from pathlib import Path
from PIL import Image
import io

# 头像存储配置
UPLOAD_DIR = Path(__file__).parent.parent.parent / "upload" / "avatars"
DEFAULT_AVATAR = "/upload/avatars/default_avatar.webp"
BASE_URL = "/upload/avatars"

def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_avatar_from_base64(base64_image: str, user_id: int) -> str:
    
    print(f"[DEBUG] save_avatar_from_base64 called for user_id: {user_id}")
    ensure_upload_dir()
    print(f"[DEBUG] UPLOAD_DIR: {UPLOAD_DIR}")
    print(f"[DEBUG] UPLOAD_DIR exists: {UPLOAD_DIR.exists()}")
    
    if not base64_image:
        print(f"[DEBUG] No base64 image provided, returning default: {DEFAULT_AVATAR}")
        return DEFAULT_AVATAR
    
    # 处理base64数据
    if ',' in base64_image:
        data = base64_image.split(',')[1]
    else:
        data = base64_image
    
    try:
        # 解码base64
        image_bytes = base64.b64decode(data)
        img = Image.open(io.BytesIO(image_bytes))
        
        # 转换为RGBA或RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        
        # 压缩图片尺寸
        max_size = (800, 800)
        img.thumbnail(max_size, Image.LANCZOS)
        
        # 生成文件名
        filename = f"{user_id}.webp"
        filepath = UPLOAD_DIR / filename
        
        print(f"[DEBUG] Saving avatar to: {filepath}")
        
        # 保存为webp格式
        img.save(filepath, format='WEBP', quality=85, method=6, optimize=True)
        
        print(f"[DEBUG] Avatar saved successfully")
        
        # 返回相对URL路径
        result_url = f"{BASE_URL}/{filename}"
        print(f"[DEBUG] Returning URL: {result_url}")
        return result_url
    except Exception as e:
        print(f"[DEBUG] 保存头像失败: {e}")
        return DEFAULT_AVATAR

def get_avatar_url(avatar_path: str | None) -> str:
    print(f"[DEBUG] get_avatar_url called with: {avatar_path}")
    
    if not avatar_path:
        print(f"[DEBUG] No avatar path, returning default: {DEFAULT_AVATAR}")
        return DEFAULT_AVATAR
    
    # 如果已经是完整URL，直接返回
    if avatar_path.startswith('http'):
        print(f"[DEBUG] Already a full URL, returning: {avatar_path}")
        return avatar_path
    
    # 如果是相对路径，直接返回
    if avatar_path.startswith('/upload/'):
        print(f"[DEBUG] Relative path, returning: {avatar_path}")
        return avatar_path
    
    # 如果是旧格式的base64数据，返回默认头像
    if avatar_path.startswith('data:image'):
        print(f"[DEBUG] Base64 data, returning default: {DEFAULT_AVATAR}")
        return DEFAULT_AVATAR
    
    print(f"[DEBUG] Unknown format, returning as-is: {avatar_path}")
    return avatar_path

def delete_old_avatar(avatar_path: str | None):
    if not avatar_path:
        return
    
    # 只删除本地文件，不删除默认头像
    if avatar_path.startswith('/upload/avatars/') and 'default_avatar' not in avatar_path:
        try:
            # 将URL路径转换为文件系统路径
            relative_path = avatar_path.replace('/upload/', 'upload/')
            filepath = Path(__file__).parent.parent.parent / relative_path
            if filepath.exists():
                filepath.unlink()
                print(f"已删除旧头像: {filepath}")
        except Exception as e:
            print(f"删除旧头像失败: {e}")
