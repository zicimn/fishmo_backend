from fastapi import APIRouter,Depends,HTTPException
from config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from cache import get_cache_key,get_from_cache,set_to_cache,delete_cache_pattern,get_search_version,update_version
from shemas import AnnouncementItem,AnnouncementList
from model import Announcement

router = APIRouter(prefix="/api/announcement",tags=['announcement'])

#获取公告列表
@router.get('/',response_model=AnnouncementList)
async def index(
    page:int = 1,
    size:int = 10,
    db:AsyncSession = Depends(get_db)
):
    version = await get_search_version()
    cache_key = get_cache_key("announcement_list",page = page,size = size,version=version)
    
    cache_data = await get_from_cache(cache_key)
    if cache_data:
        return AnnouncementList(**cache_data)
    
    skip = (page - 1) * size

    count_stmt = select(func.count(Announcement.id)).select_from(Announcement)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Announcement.id,Announcement.title,Announcement.created_at)
        .offset(skip)
        .limit(size)
        .order_by(Announcement.created_at)
    )
    rows = result.all()

    items = []
    for id,title,created_at in rows:
        items.append(
            Announcement(
                id = id,
                title = title,
                created_at = created_at
            )
        )

    data = AnnouncementList(
        total = (total + size - 1)//size,
        items=items
    )

    await set_to_cache(cache_key,data.model_dump())

    return data



#获取公告信息
@router.get('/browse/{id}')
async def browse(
    id:int,
    db:AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Announcement)
        .where(Announcement.id == id)
    )
    announcement = result.scalar_one_or_none()
    
    if not announcement:
        raise HTTPException(404,"not_found")
    
    return{
        "title": announcement.title,
        "content":announcement.content,
        "created_at":announcement.created_at
    }
    


        