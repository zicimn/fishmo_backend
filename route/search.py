from fastapi import Depends,HTTPException,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,case,or_,desc,func
from model import Article
from cache import get_cache_key,get_from_cache,set_to_cache,get_search_version,update_version
from config import get_db

router = APIRouter(prefix="/api/search",tags= ['search'])

@router.get('/{word}')
async def search(word:str,
    page:int = 1,
    size:int = 10,
    db:AsyncSession = Depends(get_db)
):
    skip = (page - 1)*size
    pattern = f"%{word}%"

    version = await get_search_version()
    cache_key = get_cache_key("search_result",word = word,page = page,size = size,version=version)
    cache_data = await get_from_cache(cache_key)
    if cache_data:
        return cache_data

    score = (
        case((Article.title.ilike(pattern),3),else_=0)+
        case((Article.content.ilike(pattern),1),else_=0)
    ).label("score")

    # 计算总数
    count_result = await db.execute(
        select(func.count(Article.id))
        .where(
            or_(
                Article.title.ilike(pattern),
                Article.content.ilike(pattern)
            )
        )
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Article.id, Article.title, Article.author_id, Article.category, Article.views, Article.likes, Article.created_at,score)
        .where(
            or_(
                Article.title.ilike(pattern),
                Article.content.ilike(pattern)
            )
        )
        .offset(skip)
        .limit(size)
        .order_by(
            desc(score),
            desc(Article.created_at)
        )
    )
    search = result.all()
    if not search:
        data = {"word":word,"result":[], "total": total}
        await set_to_cache(cache_key,data)
        return data
    
    res = []
    for article in search:
        res.append({
            "id":article[0],
            "title":article[1],
            "author_id":article[2],
            "category":article[3],
            "views":article[4],
            "likes":article[5],
            "created_at":article[6]
        })

    data = {"word":word,"result":res, "total": total}
    await set_to_cache(cache_key,data)
    return data