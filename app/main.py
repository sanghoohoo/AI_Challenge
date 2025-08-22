from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import coaching

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="이력서 기반 개인 맞춤형 커리어 코치 챗봇 API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경용, 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(
    coaching.router,
    prefix="/api/v1",
    tags=["coaching"]
)


@app.get("/")
async def root():
    """Root endpoint - API 상태 확인용"""
    return {
        "message": "AI Career Coach API is running!",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }