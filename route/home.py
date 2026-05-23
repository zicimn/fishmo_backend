from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import get_db
from utils import verify_login
from model import User

security = HTTPBearer()
router = APIRouter(prefix = '/api/home',tags = ['home'])

@router.get('/')
async def index(
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials = credentials)
    result = await db.execute(
         select(User.username,User.avatar,User.bio)
         .where(User.id == user_id)
     )

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404,"用户不存在")
     
    return {
        "username":user.username,
        "avatar":user.avatar,
        "bio":user.bio
    }