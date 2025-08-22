import logging
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.coaching import ResumePayload, CoachingResult, ErrorResponse
from app.services.coaching_service import get_coaching_service, CoachingService, CoachingServiceError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/coaching-sessions",
    response_model=CoachingResult,
    status_code=status.HTTP_201_CREATED,
    summary="개인 맞춤형 커리어 코칭 세션 생성",
    description="이력서 정보를 기반으로 개인 맞춤형 면접 질문과 학습 경로를 생성합니다.",
    responses={
        201: {
            "description": "코칭 세션이 성공적으로 생성됨",
            "model": CoachingResult
        },
        400: {
            "description": "잘못된 요청 데이터",
            "model": ErrorResponse
        },
        422: {
            "description": "유효성 검사 실패",
            "model": ErrorResponse
        },
        500: {
            "description": "서버 내부 오류",
            "model": ErrorResponse
        },
        503: {
            "description": "LLM 서비스 사용 불가",
            "model": ErrorResponse
        }
    }
)
async def create_coaching_session(
    payload: ResumePayload,
    coaching_service: CoachingService = Depends(get_coaching_service)
) -> CoachingResult:
    """
    이력서 정보를 기반으로 개인 맞춤형 커리어 코칭 세션을 생성합니다.
    
    - **career_summary**: 경력 요약 (필수)
    - **job_duties**: 수행 직무 (필수)  
    - **technical_skills**: 보유 기술 스킬 리스트 (필수)
    
    반환값:
    - **session_id**: 고유 세션 식별자
    - **interview_questions**: 5개의 맞춤형 면접 질문
    - **learning_path**: 개인화된 학습 경로 추천
    """
    try:
        logger.info(f"코칭 세션 요청 수신: {payload.career_summary[:50]}...")
        
        # 코칭 서비스를 통한 세션 생성
        result = await coaching_service.create_coaching_session(payload)
        
        logger.info(f"코칭 세션 생성 성공: {result.session_id}")
        return result
        
    except CoachingServiceError as e:
        logger.error(f"코칭 서비스 오류: {str(e)}")
        
        # LLM 서비스 관련 오류는 503으로 처리
        if "LLM" in str(e) or "API" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI 서비스 일시적 오류: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"코칭 세션 생성 중 오류 발생: {str(e)}"
            )
    
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


@router.get(
    "/health",
    summary="서비스 상태 확인",
    description="코칭 서비스와 LLM 연동 상태를 확인합니다."
)
async def health_check(
    coaching_service: CoachingService = Depends(get_coaching_service)
):
    """서비스 헬스 체크 엔드포인트"""
    try:
        is_healthy = await coaching_service.health_check()
        
        if is_healthy:
            return {
                "status": "healthy",
                "llm_service": "available",
                "message": "All services are operational"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM 서비스 연결 불가"
            )
            
    except Exception as e:
        logger.error(f"헬스체크 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"서비스 상태 확인 실패: {str(e)}"
        )