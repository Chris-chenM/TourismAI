"""FastAPI 入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api import planning, settings

app = FastAPI(
    title="TourismAI - 智能旅游规划助手",
    description="基于大模型智能体 + 高德地图的智能旅游规划系统",
    version="0.1.0",
)

# 跨域（允许 Demo 页面调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(planning.router, tags=["行程规划"])
app.include_router(settings.router, tags=["系统设置"])


# Demo 页面
DEMO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "demo")


@app.get("/demo")
async def demo_page():
    """返回 Demo 测试页面"""
    demo_file = os.path.join(DEMO_DIR, "index.html")
    if os.path.exists(demo_file):
        return FileResponse(demo_file)
    return {"message": "demo/index.html 不存在，请创建后访问"}


@app.get("/")
async def root():
    """服务首页"""
    return {
        "service": "TourismAI - 智能旅游规划助手",
        "docs": "/docs",
        "demo": "/demo",
        "api": {
            "生成计划": "POST /api/plan",
            "系统设置": "GET|PUT /api/settings",
        },
    }
