from pathlib import Path
import base64
import os

def save_image_to_file(image_base64: str, article_id: int, index: int) -> str:
    """将base64图片保存到文件系统，返回相对路径"""
    if ',' in image_base64:
        data = image_base64.split(',')[1]
    else:
        data = image_base64
    
    # 获取项目根目录下的upload文件夹（与backend同级）
    current_dir = Path(__file__).resolve().parent  # utils
    backend_dir = current_dir.parent  # backend
    project_root = backend_dir.parent  # 项目根目录
    upload_dir = project_root / "upload" / "article" / str(article_id)
    
    print(f"[DEBUG] Image upload directory: {upload_dir}")
    
    # 确保目录存在
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"[DEBUG] Directory created or exists: {upload_dir.exists()}")
    except Exception as e:
        print(f"[ERROR] Failed to create directory: {e}")
        raise
    
    filename = f"{index + 1}.webp"
    file_path = upload_dir / filename
    
    print(f"[DEBUG] Saving image to: {file_path}")
    
    try:
        image_bytes = base64.b64decode(data)
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        print(f"[DEBUG] Image saved successfully")
    except Exception as e:
        print(f"[ERROR] Failed to save image: {e}")
        raise
    
    return f"/upload/article/{article_id}/{filename}"