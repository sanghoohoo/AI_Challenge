import logging
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.coaching import ResumePayload, CoachingResult, ErrorResponse
from app.services.coaching_service import (
    get_coaching_service,
    CoachingService,
    CoachingServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/coaching-sessions",
    response_model=CoachingResult,
    status_code=status.HTTP_201_CREATED,
    summary="🎯 개인 맞춤형 커리어 코칭 세션 생성",
    description="""
## 개인 맞춤형 커리어 코칭 세션 생성

이력서 정보를 기반으로 AI가 생성하는 고품질 커리어 코칭 서비스입니다.

### ✨ 주요 특징
- **적응형 페르소나**: 이력서 분석을 통한 최적 면접관 페르소나 자동 선택
- **전략적 Few-shot**: 전문 영역별 맞춤형 질문 템플릿
- **Chain-of-Thought**: 6단계 추론 과정을 통한 심층 분석
- **품질 보장**: A/B 테스트로 최고 품질 결과 자동 선택

### 🔧 처리 과정
1. **이력서 분석**: 경력, 기술 스택, 도메인 특성 파악
2. **페르소나 선택**: 5가지 전문가 중 최적 면접관 선택
3. **전략 결정**: 기술심화/시스템설계/행동중심/문제해결/균형 중 선택
4. **병렬 생성**: 면접질문과 학습경로 동시 생성
5. **품질 평가**: 관련성/깊이/실행가능성/실용성 4차원 평가

### 📊 품질 최적화
- **9가지 조합 테스트**: 3전략 × 3페르소나 = 최적 결과 선택
- **실시간 품질 평가**: 1-5점 척도 객관적 평가
- **자동 개선 제안**: 낮은 점수 영역 개선 가이드

### 💡 사용 예시
```json
{
  "career_summary": "3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
  "job_duties": "주문 및 결제 시스템 MSA 전환 프로젝트 리딩",
  "technical_skills": ["Spring Boot", "Python", "AWS", "MSA"]
}
```
    """,
    responses={
        201: {"description": "코칭 세션이 성공적으로 생성됨", "model": CoachingResult},
        400: {"description": "잘못된 요청 데이터", "model": ErrorResponse},
        422: {"description": "유효성 검사 실패", "model": ErrorResponse},
        500: {"description": "서버 내부 오류", "model": ErrorResponse},
        503: {"description": "LLM 서비스 사용 불가", "model": ErrorResponse},
    },
)
async def create_coaching_session(
    payload: ResumePayload,
    coaching_service: CoachingService = Depends(get_coaching_service),
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
                detail=f"AI 서비스 일시적 오류: {str(e)}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"코칭 세션 생성 중 오류 발생: {str(e)}",
            )

    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        )


@router.get(
    "/health",
    summary="🏥 서비스 상태 확인",
    description="""
## 서비스 헬스 체크

코칭 서비스와 LLM API 연동 상태를 실시간으로 확인합니다.

### 📋 체크 항목
- **코칭 서비스 상태**: 내부 서비스 로직 정상 동작 여부
- **LLM API 연결**: OpenAI API 연결 및 응답 상태
- **시스템 리소스**: 메모리, CPU 사용량 등

### ✅ 정상 응답
```json
{
  "status": "healthy",
  "llm_service": "available", 
  "message": "All services are operational"
}
```

### ❌ 장애 응답 (503)
```json
{
  "detail": "LLM 서비스 연결 불가"
}
```

### 🔄 모니터링 용도
- 로드 밸런서 헬스체크
- 서비스 가용성 모니터링  
- 장애 조기 감지
    """,
)
async def health_check(
    coaching_service: CoachingService = Depends(get_coaching_service),
):
    """서비스 헬스 체크 엔드포인트"""
    try:
        is_healthy = await coaching_service.health_check()

        if is_healthy:
            return {
                "status": "healthy",
                "llm_service": "available",
                "message": "All services are operational",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM 서비스 연결 불가",
            )

    except Exception as e:
        logger.error(f"헬스체크 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"서비스 상태 확인 실패: {str(e)}",
        )
