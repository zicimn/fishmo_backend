from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from config import get_db
from utils import verify_login
from model import User,Article,Comment
from typing import Optional
from cache import set_to_cache,get_search_version,get_cache_key,get_from_cache
#东西写重了,在user.py里面也有为user/info
security = HTTPBearer()
router = APIRouter(prefix = '/api/home',tags = ['home'])

@router.get('/')
async def index(
    user_id:Optional[int] = None,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    if not user_id:
        user_id = verify_login(credentials = credentials)
    result = await db.execute(
         select(User.username,User.avatar,User.bio,User.email)
         .where(User.id == user_id)
     )

    user = result.one_or_none()
    if not user:
        raise HTTPException(404,"用户不存在")
    
    article_count_result = await db.execute(
        select(func.count(Article.id))
        .where(Article.author_id == user_id)
    )

    cnt = article_count_result.scalar_one()
    if not cnt:
        cnt = 0
     
    return {
        "username":user.username,
        "avatar":user.avatar,
        "bio":user.bio,
        "email":user.email,
        "article_count":cnt
    }



@router.get('/article/{user_id}')
async def get_article(
    user_id:int,
    page:int = 1,
    size:int = 10,
    db : AsyncSession = Depends(get_db)
):

    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('home_articles', user_id=user_id, page=page, size=size, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    skip  = (page-1)*size
    result = await db.execute(
        select(Article.id, Article.title, Article.category,Article.views, Article.likes, Article.created_at)
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
            "views": article[3],
            "likes": article[4],
            "created_at": article[5]
        })
    
    data = {"author_id":user_id,"articles":articles_list}
    # 存入缓存
    await set_to_cache(cache_key, data)
    
    return data



@router.get("/comment/{user_id}")
async def get_article(
    user_id:int,
    page:int = 1,
    size:int = 10,
    db : AsyncSession = Depends(get_db)
):
    version = await get_search_version()
    cache_key = get_cache_key('home_comment', user_id=user_id, page=page, size=size, version=version)
    
    cache_data = await get_from_cache(cache_key)
    if cache_data:
        return cache_data
    
    skip = (page-1)*size
    result = await db.execute(
        select(Comment.article_id,Comment.content,Comment.created_at)
        .where(Comment.user_id == user_id)
        .offset(skip)
        .limit(size)
        .order_by(Comment.created_at.asc())
    ) 
    comments = result.all()

    if not comments:
        data = {"comments":[]}
        # 存入缓存
        await set_to_cache(cache_key, data)
        return data
    
    comments_list = []
    for c in comments:
        comments_list.append({
            "article_id":c[0],
            "content":c[1],
            "created_at":c[2]
        })

    data = {"comments":comments_list}
    await set_to_cache(cache_key,data)

    return data
