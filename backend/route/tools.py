from fastapi import APIRouter,HTTPException,Depends
from utils import convert_images_to_webp,verify_login
from shemas import imageItem
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cache import get_cache_key,get_from_cache,set_to_cache
import random
from datetime import datetime,timezone,timedelta

security = HTTPBearer()#自动去掉header
router = APIRouter(prefix="/api/tools",tags=['tools'])
beijing_tz = timezone(timedelta(hours=8))

@router.post('/compression')
async def compression(data: imageItem):
    images = data.images
    quality = data.quality
    style = data.style

    if images is None or len(images) == 0:
        raise HTTPException(400,"请至少上传一张图片")
    if len(images)>10:
        raise HTTPException(400,"最多上传10张图片")

    webp_images = convert_images_to_webp(images,quality=quality,style=style)
    return {"images":webp_images,"count":len(webp_images)}


lucky = ['大凶','凶','末吉','中吉','大吉']
@router.get('/diviation')
async def diviation(
    credentials:HTTPAuthorizationCredentials = Depends(security)
):
    user_id = verify_login(credentials=credentials)
    cache_key = get_cache_key("divia_id",user_id = user_id)
    cache_data = await get_from_cache(cache_key)

    cur_time = datetime.now(beijing_tz).date().isoformat()#注意cache_data取出来为string,所以要转为string
    if cache_data:
        prev_time = cache_data.get("time")
        if prev_time == cur_time:
            return cache_data
        
    delay = 24*60*60
    fate = random.choice(lucky)
    id = random.randint(1,12)
    url = f"/upload/fate/{id}.png"
    data = {"user_id":user_id,"fate":fate,"url":url,"time":cur_time}
    await set_to_cache(cache_key,data,expire=delay)
    return data
