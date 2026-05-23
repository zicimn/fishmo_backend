import smtplib
import random
import threading
import base64
import io
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException,Depends
from jose import jwt,JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import ALGORITHM,SECRET_KEY
from PIL import Image
from typing import List
from shemas import SORTABLE_FIELDS
from sqlalchemy import desc, asc


SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465                       
FROM_EMAIL = "3878160878@qq.com"  
SMTP_PASSWORD = "njegsymidvbpcfhb"

security = HTTPBearer()#自动去掉header

# 存储验证码 {邮箱: 验证码}
codes = {}

def clear_code(email: str):
    """5分钟后删除验证码"""
    codes.pop(email, None)
    print(f"验证码已清除: {email}")

def send_email(to_email: str) -> str:
    """
    发送验证码邮件
    返回生成的6位验证码
    """
    # 生成6位验证码
    code = str(random.randint(100000, 999999))
    
    # 保存验证码
    codes[to_email] = code
    
    # 5分钟后自动删除
    threading.Timer(300.0, clear_code, args=[to_email]).start()
    
    # 构建邮件
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "验证码"
    
    # 邮件正文
    body = f"您的验证码是: {code}\n5分钟内有效。"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # 连接SMTP服务器并发送
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(FROM_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"验证码已发送至 {to_email}: {code}")
        return code
    except Exception as e:
        print(f"发送邮件失败: {e}")
        raise HTTPException(500, "发送验证码失败")

def verify_code(email: str, code: str) -> bool:
    """验证验证码是否正确"""
    stored_code = codes.get(email)
    if stored_code and stored_code == code:
        return True
    return False

def verify_login(credentials: HTTPAuthorizationCredentials) -> int:
    """验证token并返回用户id"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("TOKEN:", token)
        user_id = int(payload['sub'])#从token取出id
        return user_id
    except JWTError:
        raise HTTPException(401,"token无效")
    

def convert_to_webp(image:str,quality:int = 85)->str:
    """将单个图片转换为webp格式"""
    if not image:
        return image
    
    # 如果已经是webp格式，直接返回
    if 'image/webp' in image:
        return image
    
    if ',' in image:
        data = image.split(',')[1]
    else:
        data = image
    
    image_bytes = base64.b64decode(data)
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode in ('RGBA','LA','P'):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')

    output = io.BytesIO()
    img.save(output,format='WEBP',quality=quality, method=6, optimize = True )
    webp_byte = output.getvalue()

    webp_base64 = base64.b64encode(webp_byte).decode('utf-8')
    return f"data:image/webp;base64,{webp_base64}"


def convert_images_to_webp(images: List[str], quality: int = 85) -> List[str]:
    """将图片列表转换为webp格式"""
    if not images:
        return []
    
    webp_images = []
    for image in images:
        try:
            webp_image = convert_to_webp(image, quality)
            webp_images.append(webp_image)
        except Exception as e:
            print(f"转换图片失败: {e}")
            # 如果转换失败，保留原图
            webp_images.append(image)
    
    return webp_images


def get_sort_column(field: str):
    """获取排序字段，带验证"""
    if field not in SORTABLE_FIELDS:
        raise ValueError(f"无效的排序字段: {field}，可选: {list(SORTABLE_FIELDS.keys())}")
    return SORTABLE_FIELDS[field]

def build_order_by(field: str, order: str = "desc"):
    """构建排序表达式"""
    column = get_sort_column(field)
    return desc(column) if order == "desc" else asc(column)