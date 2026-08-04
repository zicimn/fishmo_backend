import random
from fastapi import HTTPException,Depends
from cache import get_cache_key,get_from_cache,delete_cache,set_to_cache
from config import RESEND_API_KEY
import resend
from pydantic import EmailStr
import asyncio

resend.api_key = RESEND_API_KEY

def get_email_cache_key(email: EmailStr) -> str:
    return get_cache_key("email_code", email)


async def clear_code(email:EmailStr):
    cache_key = get_email_cache_key(email)
    await delete_cache(cache_key)


async def send_email(email: EmailStr):

    code = str(random.randint(100000, 999999))
    cache_key = get_email_cache_key(email)
    #放置到redis里面
    await set_to_cache(cache_key, code, expire=300)

    try:
        params: resend.Emails.SendParams = {
            "from": "fishmo <noboard@fishmo.top>",
            "to": [email],
            "subject": "你的邮箱验证码",
            "html": f"""
                <h1>邮箱验证</h1>
                <p>你的验证码是：</p>
                <h2 style="color: blue;">{code}</h2>
                <p>该验证码 5 分钟内有效。</p>
            """,
        }
        # resend SDK 是同步实现（内部走 requests），不能直接 await，
        # 用 asyncio.to_thread 丢到线程池执行，避免阻塞事件循环。
        await asyncio.to_thread(resend.Emails.send, params)
        return {"message": "验证码已发送，请检查你的邮箱。"}
    except Exception as e:
        await delete_cache(cache_key) # 删除缓存中的验证码
        raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")
    

async def verify_code(email: EmailStr, code: str) -> bool:
    cache_key = get_email_cache_key(email)
    cached_code = await get_from_cache(cache_key)

    if cached_code and cached_code == code:
        await delete_cache(cache_key)  # 验证成功后删除缓存中的验证码
        return True
    else:
        return False



# def get_email_code_key(email:str)->str:
#     return get_cache_key("email_code",email)


# async def clear_code(email: str):
#     """5分钟后删除验证码"""
#     cache_key = get_email_code_key(email=email)
#     await delete_cache(cache_key)
#     print(f"验证码已清除: {email}")


# async def send_email(to_email: str) -> str:
#     """
#     发送验证码邮件
#     返回生成的6位验证码
#     """
#     # 生成6位验证码
#     code = str(random.randint(100000, 999999))
#     cache_key = get_email_code_key(email=to_email)
    
#     await set_to_cache(cache_key,code)
    
#     # 构建邮件
#     msg = MIMEMultipart()
#     msg['From'] = FROM_EMAIL
#     msg['To'] = to_email
#     msg['Subject'] = "验证码"
    
#     # 邮件正文
#     body = f"您的验证码是: {code}\n5分钟内有效。"
#     msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
#     try:
#         # 连接SMTP服务器并发送
#         server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
#         server.login(FROM_EMAIL, SMTP_PASSWORD)
#         server.send_message(msg)
#         server.quit()
        
#         print(f"验证码已发送至 {to_email}: {code}")
#         return code
#     except Exception as e:
#         await delete_cache(cache_key)
#         print(f"发送邮件失败: {e}")
#         raise HTTPException(500, "发送验证码失败")


# async def verify_code(email: str, code: str) -> bool:
#     """验证验证码是否正确"""
#     cache_key = get_email_code_key(email=email)
#     stored_code = await get_from_cache(cache_key)

#     if stored_code and stored_code == code:
#         await delete_cache(cache_key)
#         return True
#     return False