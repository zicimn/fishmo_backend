from utils.verify_email import verify_code, send_email
from utils import verify_login, save_avatar_from_base64, get_avatar_url, delete_old_avatar
from fastapi import APIRouter,Depends,HTTPException,Query
from config import get_db,SECRET_KEY,ALGORITHM
from model import User,Article,ArticleLink,Favorite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,or_,update
from passlib.context import CryptContext
from jose import jwt,JWTError
from shemas import Account,Update_request,LoginRequest
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from cache import get_cache_key,get_from_cache,delete_cache,delete_cache_pattern,set_to_cache,get_search_version,update_version
# from func import send_email,codes,verify_code,verify_login,convert_to_webp
# from backend.utils.avatar_utils import save_avatar_from_base64, get_avatar_url, delete_old_avatar


security = HTTPBearer()#自动去掉header
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")#hash加密方式
router = APIRouter(prefix="/api/user",tags=['user'])


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):

    print("LOGIN SECRET:", SECRET_KEY)

    query = await db.execute(select(User).where(User.username == data.username))
    result = query.scalar_one_or_none()

    if not result or not pwd_context.verify(data.password, result.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = jwt.encode(
        {"sub": str(result.id), "username": result.username},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "id": result.id,
        "username": result.username,
        "access_token": token,
        "avatar": get_avatar_url(result.avatar)
    }
    


@router.post('/register')
async def register(
    account: Account,
    code:str,
    db: AsyncSession = Depends(get_db)
):
    
    print("UPDATE SECRET:", SECRET_KEY)
    # 查询是否存在
    result = await db.execute(
        select(User).where(
            or_(User.username == account.name, User.email == account.email)
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(400, detail="用户名或邮箱已存在")
    
    ok = await verify_code(email=account.email,code=code)
    if not ok:
        raise HTTPException(400,"验证码错误或者过期")


    
    hashed_password = pwd_context.hash(account.password)
    
    new_user = User(
        username=account.name,
        email=account.email,  
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }



@router.get('/info')
async def get_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "未找到")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": get_avatar_url(user.avatar),
        "bio": user.bio
    }

@router.put('/update')
async def update_user(data:Update_request,
    credentials: HTTPAuthorizationCredentials = Depends(security),#验证Authorization
    db:AsyncSession = Depends(get_db)):

    user_id = verify_login(credentials=credentials)
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404,"未找到")
    
    if data.new_username:
        existing = await db.execute(select(User).where(User.username == data.new_username))
        if existing.scalar_one_or_none():
            raise HTTPException(400, "用户名已被使用")
        user.username = data.new_username

    if data.new_email:
        existing = await db.execute(select(User).where(User.email == data.new_email))
        if existing.scalar_one_or_none():
            raise HTTPException(400, "邮箱已被使用")
        user.email = data.new_email

    if data.new_avator:
        # 删除旧头像
        delete_old_avatar(user.avatar)
        # 保存新头像并获取URL路径
        avatar_url = save_avatar_from_base64(data.new_avator, user_id)
        user.avatar = avatar_url

    if data.new_password:
        user.password_hash = pwd_context.hash(data.new_password)
    if data.new_bio:
        user.bio = data.new_bio

    await db.commit()
    await db.refresh(user)
    await update_version()
    return {
        "msg": '更新成功',
        "user_id": user_id,
        "user": {
            "id": user.id,
            "username": user.username,
            "avatar": get_avatar_url(user.avatar)
        }
    }
    


@router.delete("/delete")
async def delete(credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db),
    ok:bool = False):#ok是留确认的
    #登录成功使用
    if not ok:
        return {'msg':"not deleted"}
    print("CREDENTIALS:", credentials)
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("TOKEN:", token)
        user_id = int(payload['sub'])#从token取出id
    except JWTError:
        raise HTTPException(401,"token无效")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404,"未找到")
    
    await db.delete(user)
    await db.commit()

    return {"user":user}



@router.post('/send_code')
async def send_code(email:EmailStr,db:AsyncSession = Depends(get_db)):
    
    code = await send_email(email)
    print(f"code:{code}")
    return {"msg":"验证码已发送"}



@router.post("/retrieve")#y因为send_code已经验证了所以就懒得二次验证了
async def retrieve(email:EmailStr,password:str,code:str,
    db:AsyncSession = Depends(get_db)):

    ok = await verify_code(email,code)
    if not ok:
        raise HTTPException(400,"验证码错误或者过期")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404,'未找到邮箱')
    
    
    hashed_password = pwd_context.hash(password)
    user.password_hash = hashed_password
    await db.commit()
    return {'msg': "修改成功"}


    
@router.get('/article/get_list')#本质上是公开的没必要进行验证这一步
async def get_list(
    page:int = 1,
    size:int = 10,
    credentials : HTTPAuthorizationCredentials = Depends(security),
    db : AsyncSession = Depends(get_db)
):

    user_id = verify_login(credentials=credentials)
    print(user_id)

    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('user_articles', user_id=user_id, page=page, size=size, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    skip  = (page-1)*size
    result = await db.execute(
        select(Article.id, Article.title, Article.category, Article.content, Article.views, Article.likes, Article.created_at)
        .where(Article.author_id == user_id)
        .offset(skip)
        .limit(size)
        .order_by(Article.created_at.asc()))
    articles = result.all()

    if not articles:
        data = {"author_id":user_id,"articles":[]}
        # 存入缓存
        await set_to_cache(cache_key, data)
        return data
    
    # 转换为字典格式
    articles_list = []
    for article in articles:
        articles_list.append({
            "id": article[0],
            "title": article[1],
            "category": article[2],
            "content": article[3],
            "views": article[4],
            "likes": article[5],
            "created_at": article[6]
        })
    
    data = {"author_id":user_id,"articles":articles_list}
    # 存入缓存
    await set_to_cache(cache_key, data)
    
    return data



@router.get("/article/getlinklist")
async def get_link_list(
    page : int = 1,
    size: int = 10,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    
    user_id = verify_login(credentials=credentials)

    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('user_links', user_id=user_id, page=page, size=size, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    skip = (page - 1)*size
    # 再查询链接，并确保属于该文章
    result = await db.execute(
        select(ArticleLink)
        .where(ArticleLink.user_id == user_id)
        .offset(skip)
        .limit(size)
        .order_by(ArticleLink.created_at.desc())
    )
    links = result.scalars().all()
    
    if not links:
        data = {"links":[]}
        # 存入缓存
        await set_to_cache(cache_key, data)
        return data
    
    # 转换为可序列化的字典格式
    links_list = []
    for link in links:
        links_list.append({
            "id": link.id,
            "article_id": link.article_id,
            "user_id": link.user_id,
            "url": link.url,
            "title": link.title,
            "created_at": link.created_at
        })
    
    data = {"links": links_list}
    # 存入缓存
    await set_to_cache(cache_key, data)
    
    return data


@router.get('/favorite/get_list')
async def get_favorite_list(
    page : int = 1,
    size: int = 10,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)

    version = await get_search_version()
    cache_key = get_cache_key('user_favorites', user_id=user_id, page=page, size=size, version=version)
    cached_data = await get_from_cache(cache_key)

    if cached_data:
        return cached_data
    
    skip = (page - 1)*size
    result = await db.execute(
        select(Article.id, Article.title, Article.category, Article.created_at, Article.views, Article.likes)
        .join(Favorite, Article.id == Favorite.article_id)
        .where(Favorite.user_id == user_id)
        .offset(skip)
        .limit(size)
    )
    favorites = result.all()

    if not favorites:
        data = {"favorites":[]}
        await set_to_cache(cache_key, data)
        return data

    favorites_list = []
    for fav in favorites:
        favorites_list.append({
            "id": fav[0],
            "title": fav[1],
            "category": fav[2],
            "created_at": fav[3],
            "views": fav[4],
            "likes": fav[5]
        })
    data = {"favorites": favorites_list}
    await set_to_cache(cache_key, data)
    return data
