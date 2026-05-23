from fastapi import FastAPI
from route import user_router,article_router,search_router,tools_router,home_router
import uvicorn
import model
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录，用于访问上传的文件
upload_dir = (Path(__file__).parent.parent / "upload").resolve()
print(f"[DEBUG] Static files directory: {upload_dir}")
print(f"[DEBUG] Directory exists: {upload_dir.exists()}")

# 确保upload目录存在
upload_dir.mkdir(parents=True, exist_ok=True)
avatars_dir = upload_dir / "avatars"
avatars_dir.mkdir(parents=True, exist_ok=True)
articles_dir = upload_dir / "article"
articles_dir.mkdir(parents=True, exist_ok=True)
fate_dir = upload_dir / "fate"
fate_dir.mkdir(parents=True, exist_ok=True)

print(f"[DEBUG] All subdirectories created: avatars={avatars_dir.exists()}, article={articles_dir.exists()}, fate={fate_dir.exists()}")

if upload_dir.exists():
    app.mount("/upload", StaticFiles(directory=str(upload_dir)), name="upload")
    print("[DEBUG] Static files mounted successfully")
else:
    print("[ERROR] Upload directory does not exist")

app.include_router(user_router)
app.include_router(article_router)
app.include_router(search_router)
app.include_router(tools_router)
app.include_router(home_router)

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True,reload_excludes=["logs/*", "*.log", "__pycache__/*"])