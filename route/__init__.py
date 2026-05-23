from .user import router as user_router  # 导出 router
from .article import router as article_router
from .search import router as search_router
from .tools import router as tools_router
from .home import router as home_router
__all__ = ["user_router","article_router","search_router","tools_router","home_router"]