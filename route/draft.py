# from fastapi import Depends,HTTPException,APIRouter
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy import select,case,or_,desc,func
# from model import Draft
# from config import get_db
# from utils import verify_login
# from shemas import Post

# security = HTTPBearer()#自动去掉header
# router = APIRouter(prefix="/api/draft",tags= ['draft'])

# @router.get('/')
# async def get_draft(
#     credentials:HTTPAuthorizationCredentials = Depends(security),
#     db:AsyncSession = Depends(get_db)
# ):
#     user_id = verify_login(credentials=credentials)
#     result = await db.execute(
#         select(Draft)
#         .where(Draft.user_id == user_id)    
#     )

#     draft = result.scalar_one_or_none()
#     if not draft:
#         raise HTTPException(status_code=404,detail="没有草稿")
    
#     return {
#         "title":draft.title,
#         "category":draft.category,
#         "content":draft.content,
#         "images":draft.images if draft.images else [],
#     }



# @router.post('/')
# async def save_draft(
#     pt:Post,
#     credentials:HTTPAuthorizationCredentials = Depends(security),
#     db:AsyncSession =Depends(get_db)
# ):
#     user_id = verify_login(credentials=credentials)
#     result = await db.execute(
#         select(Draft)
#         .where(Draft.user_id == user_id)    
#     )

#     draft = result.scalar_one_or_none()
#     if draft:
#         return HTTPException(status_code=400,detail="草稿已存在，请先删除或更新")
    
#     new_draft = Draft(
#         user_id = user_id,
#         title = pt.title,
#         category = pt.category,
#         content = pt.content
#         images = pt.images if pt.images else []
#     )

#     db.add(new_draft)
#     await db.commit()
#     await db.refresh(new_draft)

#     return {"message":"草稿保存成功"}
