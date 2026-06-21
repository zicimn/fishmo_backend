from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from config import get_db
from utils import verify_login
from model import User,Article

#东西写重了,在user.py里面也有为user/info
security = HTTPBearer()
router = APIRouter(prefix = '/api/home',tags = ['home'])

@router.get('/')
async def index(
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
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


# @router.get('/visit')
# async def visit(

# ):
#     pass

    