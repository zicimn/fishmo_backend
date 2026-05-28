from fastapi import APIRouter,Depends,HTTPException,Query
from config import get_db,SECRET_KEY,ALGORITHM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from shemas import Post,ArticleItem,ArticleList,ArticleEdit,LinkRequest,CommentItem,CommentList,SORTABLE_FIELDS
from model import Article,ArticleLink,User,Like,Comment,Favorite
from utils import verify_login,convert_images_to_webp,build_order_by,save_image_to_file
from cache import get_cache_key, get_from_cache, set_to_cache, delete_cache_pattern, get_search_version, update_version

security = HTTPBearer()#自动去掉header
router = APIRouter(prefix="/api/article",tags=['article'])

@router.post('/publish/')
async def publish(pt:Post,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)):

    user_id = verify_login(credentials=credentials)
    
    result = await db.execute(select(User.id).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(404,'not found')
    
    # 转换图片为webp格式
    webp_images = convert_images_to_webp(pt.images) if pt.images else []
    
    # 先创建文章获取ID
    new_article = Article(
        title = pt.title,
        author_id = user_id,
        category = pt.category,
        content = pt.content,
        images = []
    )

    db.add(new_article)
    await db.commit()
    await db.refresh(new_article)
    
    article_id = new_article.id
    
    # 保存图片到文件系统并获取路径
    image_paths = []
    for index, img in enumerate(webp_images):
        try:
            path = save_image_to_file(img, article_id, index)
            image_paths.append(path)
        except Exception as e:
            print(f"保存图片失败: {e}")
    
    # 更新文章的图片路径
    new_article.images = image_paths
    await db.commit()

    # 清理缓存
    await delete_cache_pattern('article_list:*')
    await delete_cache_pattern(f'user_articles:*user_id={user_id}*')
    await update_version()

    return{
        "id":article_id,
        "title":pt.title,
        "category":pt.category,
        "content":pt.content,
        "images":image_paths
    }


@router.get('/visit/{id}')
async def visit(id:int,db:AsyncSession = Depends(get_db)):
    # 先获取文章和作者信息
    result = await db.execute(
        select(Article, User.username).join(User, Article.author_id == User.id).where(Article.id == id)
    )
    row = result.first()

    if not row:
        raise HTTPException(404,"not found")
    
    article, author_name = row
    
    # 更新浏览量
    article.views +=1
    await db.commit()
    await db.refresh(article)

    return {
        "title":article.title,
        "content":article.content,
        "images":article.images if article.images else [],
        "author_id":article.author_id,
        "author_name":author_name,
        "views":article.views
    }


@router.get('/', response_model=ArticleList)
async def index(
    page: int = 1,
    size: int = 10,
    category: str = None,
    sort: str = Query("created_at", description=f"可选: {list(SORTABLE_FIELDS.keys())}"),
    order: str = Query("desc", pattern="^(desc|asc)$"),
    db: AsyncSession = Depends(get_db)
):

    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('article_list', page=page, size=size, category=category, sort=sort, order=order, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return ArticleList(**cached_data)

    try:
        order_by_clause = build_order_by(sort, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    skip = (page - 1) * size

    # 构建基础查询
    base_stmt = (
        select(Article.id, Article.title, Article.author_id, Article.category, Article.views, Article.likes, Article.created_at, User.username)
        .join(User, Article.author_id == User.id)
    )
    #不基于base_stmt构建是因为同时查询了article和user表,造成了笛卡尔积问题导致显示错误
    count_stmt = select(func.count(Article.id)).select_from(Article.__table__.alias('Article'))
    if category:
        base_stmt = base_stmt.where(Article.category == category)
        count_stmt = count_stmt.where(Article.category == category)

    # 计算总数
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # 构建分页查询
    paginated_stmt = base_stmt.offset(skip).limit(size).order_by(order_by_clause)

    result = await db.execute(paginated_stmt)
    rows = result.all()

    items = []

    for article_id, title, author_id, category, views, likes, created_at, name in rows:
        items.append(
            ArticleItem(
                id=article_id,
                title=title,
                author_name=name,
                category=category,
                views=views,
                likes=likes,
                create_at=created_at
            )
        )

    data = ArticleList(
        total=(total + size -1)//size,
        items=items
    )
    
    # 存入缓存
    await set_to_cache(cache_key, data.model_dump())
    
    return data


@router.put('/edit/{id}')
async def edit(id :int,
    data : ArticleEdit,
    credentials : HTTPAuthorizationCredentials = Depends(security),
    db : AsyncSession = Depends(get_db)
    ):

    user_id = verify_login(credentials=credentials)
    print(user_id)
    
    result = await db.execute(select(Article).where(Article.author_id == user_id).where(Article.id == id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404,"not found")
    
    if data.title:
        article.title = data.title
    if data.category:
        article.category = data.category
    if data.content:
        article.content = data.content
    if data.images:
        # 转换图片为webp格式
        webp_images = convert_images_to_webp(data.images)
        
        # 保存图片到文件系统并获取路径
        image_paths = []
        for index, img in enumerate(webp_images):
            try:
                path = save_image_to_file(img, id, index)
                image_paths.append(path)
            except Exception as e:
                print(f"保存图片失败: {e}")
        
        article.images = image_paths

    await db.commit()
    await db.refresh(article)

    # 清理缓存
    await delete_cache_pattern('article_list:*')
    await delete_cache_pattern(f'user_articles:*user_id={user_id}*')
    await delete_cache_pattern(f'article_comments:*article_id={id}*')
    await delete_cache_pattern(f'article_links:*article_id={id}*')
    await update_version()

    return {"msg":"修改成功","article":article}


@router.delete("/delete/{id}")
async def delete(
    id:int,
    ok:bool = False,
    credentials : HTTPAuthorizationCredentials = Depends(security),
    db : AsyncSession = Depends(get_db)
):
    if not ok:
        return {"msg":"not deleted"}

    user_id = verify_login(credentials=credentials)
    result = await db.execute(
        select(Article)
        .where(Article.author_id == user_id)
        .where(Article.id == id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404,"not found")
    
    await db.delete(article)
    await db.commit()

    # 清理缓存
    await delete_cache_pattern('article_list:*')
    await delete_cache_pattern(f'user_articles:*user_id={user_id}*')
    await delete_cache_pattern(f'article_comments:*article_id={id}*')
    await delete_cache_pattern(f'article_links:*article_id={id}*')
    await delete_cache_pattern(f'user_favorites:*')
    await update_version()

    return {
        "author_id":user_id,
        "id":id,
        "article":article
    }


@router.post('/{id}/submit_link')#添加帖子id
async def sumbit_link(
    id:int,
    link:LinkRequest,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)

    result = await db.execute(select(Article).where(Article.id == id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(404,"not found")

    new_link = ArticleLink(
        article_id = id,
        user_id = user_id,
        url = link.url,
        title = link.title
    )

    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)

    # 清理缓存
    await delete_cache_pattern(f'article_links:*article_id={id}*')
    await delete_cache_pattern(f'user_links:*user_id={user_id}*')
    await update_version()

    # 转换为可序列化的字典格式
    link_dict = {
        "id": new_link.id,
        "article_id": new_link.article_id,
        "user_id": new_link.user_id,
        "url": new_link.url,
        "title": new_link.title,
        "created_at": new_link.created_at
    }

    return {
        "msg":"添加成功",
        "link": link_dict
    }


@router.get("/{article_id}/links")
async def get_link(
    article_id: int,      # 文章ID
    page : int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('article_links', article_id=article_id, page=page, size=size, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return cached_data

    skip = (page - 1) * size
    # 再查询链接，并确保属于该文章
    result = await db.execute(
        select(ArticleLink)
        .where(ArticleLink.article_id == article_id)
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


@router.delete("/{article_id}/deleted/{link_id}")#文章id,链接id
async def delete_link(
    article_id:int,
    link_id:int,
    ok:bool = False,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    if not ok:
        return {"msg":"not deleted"}

    user_id = verify_login(credentials=credentials)
    print(f"u:{user_id},l:{link_id},a:{article_id}")
    
    # 查询所有链接，查看数据库中的实际数据
    all_links_result = await db.execute(
        select(ArticleLink)
    )
    all_links = all_links_result.scalars().all()
    print(f"All links in DB: {[(link.id, link.article_id, link.user_id) for link in all_links]}")
    
    # 先查询链接是否存在
    result = await db.execute(
        select(ArticleLink)
        .where(ArticleLink.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(404,f"链接不存在，ID: {link_id}")
    
    # 验证链接是否属于该文章
    if link.article_id != article_id:
        raise HTTPException(403,f"无权操作此链接，链接属于文章ID: {link.article_id}")
    
    # 验证链接是否属于该用户
    if link.user_id != user_id:
        raise HTTPException(403,f"无权操作此链接，链接属于用户ID: {link.user_id}")
    
    await db.delete(link)
    await db.commit()

    # 清理缓存
    await delete_cache_pattern(f'article_links:*article_id={article_id}*')
    await delete_cache_pattern(f'user_links:*user_id={user_id}*')
    await update_version()

    # 转换为可序列化的字典格式
    link_dict = {
        "id": link.id,
        "article_id": link.article_id,
        "user_id": link.user_id,
        "url": link.url,
        "title": link.title,
        "created_at": link.created_at
    }

    return {
        "msg":"删除成功",
        "link": link_dict
    }


@router.get("/{id}/comment",response_model=CommentList)
async def get_comment(
    id:int,
    page:int = 1,
    size:int = 10,
    db:AsyncSession = Depends(get_db)
):
    # 生成缓存键
    version = await get_search_version()
    cache_key = get_cache_key('article_comments', article_id=id, page=page, size=size, version=version)
    
    # 尝试从缓存获取数据
    cached_data = await get_from_cache(cache_key)
    if cached_data:
        return CommentList(**cached_data)

    result = await db.execute(
        select(Article.id)
        .where(Article.id == id)
    )

    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(404,"not found")

    skip  = (page-1)*size

    result = await db.execute(
        select(Comment, User.username)
        .join(User, Comment.user_id == User.id)
        .where(Comment.article_id == id)
        .order_by(Comment.created_at.desc())  
        .offset(skip)
        .limit(size)
    )

    comments = [
        CommentItem(
            name = name,
            content = comment.content,
            created_at= comment.created_at
        )
        for comment,name in result.all()
    ]

    data = CommentList(comments=comments)
    
    # 存入缓存
    await set_to_cache(cache_key, data.model_dump())
    
    return data


@router.post("/{id}/comments")
async def add_comment(
    id:int,
    content:str,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)

    result = await db.execute(select(Article).where(Article.id == id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(404,"not found")
    
    new_comment = Comment(
        article_id = id,
        user_id = user_id,
        content = content
    )

    db.add(new_comment)
    await db.commit()

    # 清理缓存
    await delete_cache_pattern(f'article_comments:*article_id={id}*')
    await update_version()

    return {
        "msg":"评论成功",
        "comment":new_comment
    }



@router.post("/favorite/add/{id}")
async def add_favorite(
    id:int,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)

    result = await db.execute(select(Article).where(Article.id == id))
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(404,"not found article")

    # 检查是否已经收藏
    existing = await db.execute(
        select(Favorite).where(Favorite.article_id == id).where(Favorite.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400,"已经收藏过该文章")
    
    new_favorite = Favorite(
        article_id = id,
        user_id = user_id
    )

    db.add(new_favorite)
    await db.commit()

    # 清理缓存
    await delete_cache_pattern(f'user_favorites:*user_id={user_id}*')
    await update_version()

    return{
        "msg":"收藏成功",
        "favorite":new_favorite
    }



@router.delete("/favorite/remove/{id}")
async def remove_favorite(
    id:int,
    credentials:HTTPAuthorizationCredentials = Depends(security),
    db:AsyncSession = Depends(get_db)
):
    user_id = verify_login(credentials=credentials)

    result = await db.execute(select(Favorite).where(Favorite.article_id == id).where(Favorite.user_id == user_id))
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(404,"not found favorite")
    
    await db.delete(favorite)
    await db.commit()

    # 清理缓存
    await delete_cache_pattern(f'user_favorites:*user_id={user_id}*')
    await update_version()

    return {
        "msg":"取消收藏成功",
        "favorite":favorite
    }