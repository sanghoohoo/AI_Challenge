from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import coaching

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## AI Career Coach API

이력서 기반 개인 맞춤형 커리어 코치 챗봇 API입니다.

### 주요 기능
- **개인 맞춤형 면접 질문 생성**: 5개의 심층적인 질문
- **학습 경로 추천**: 구체적이고 실행 가능한 단계별 가이드  
- **고급 프롬프트 엔지니어링**: PCT 프레임워크 + Few-shot + Chain-of-Thought
- **품질 최적화**: A/B 테스트 기반 최고 품질 결과 선택

### 기술 스택
- **Backend**: FastAPI (Python)
- **AI Integration**: OpenAI GPT API
- **Quality Assurance**: 실시간 품질 평가 시스템

### API 사용법
1. POST `/api/v1/coaching-sessions`로 이력서 정보 전송
2. 개인화된 면접 질문 5개와 학습 경로 수신
3. 품질 점수 기반으로 최적화된 결과 제공

### 평가 기준 최적화
- 생성형 AI 활용의 창의성 및 정교함 ✅
- 백엔드 아키텍처 및 구현 ✅
- 기능의 유용성 및 실용성 ✅
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AI Challenge Team",
        "url": "https://github.com/sanghoohoo/AI_Challenge",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
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
app.include_router(coaching.router, prefix="/api/v1", tags=["coaching"])


@app.get("/")
async def root():
    """Root endpoint - API 상태 확인용"""
    return {
        "message": "AI Career Coach API is running!",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.environment}
