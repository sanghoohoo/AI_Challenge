from fastapi import APIRouter, HTTPException, status
from app.schemas.coaching import ResumePayload, CoachingResult, ErrorResponse

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
async def create_coaching_session(payload: ResumePayload) -> CoachingResult:
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
        # TODO: Phase 2에서 실제 LLM 서비스 로직 구현
        # 현재는 임시 응답을 반환
        
        from app.schemas.coaching import InterviewQuestion, LearningPath, LearningStep
        from uuid import uuid4
        
        # 임시 응답 데이터 (Phase 2에서 실제 LLM 호출로 대체)
        sample_questions = [
            InterviewQuestion(
                question=f"{payload.career_summary}을 바탕으로, 가장 도전적이었던 기술적 문제는 무엇이었고 어떻게 해결하셨나요?",
                intent="문제 해결 능력과 기술적 깊이를 평가합니다.",
                category="Technical Deep-Dive"
            ),
            InterviewQuestion(
                question="MSA 전환 과정에서 발생한 데이터 정합성 문제를 어떻게 해결하셨나요?",
                intent="분산 시스템에 대한 이해도를 검증합니다.",
                category="System Design"
            ),
            InterviewQuestion(
                question="팀원과의 기술적 의견 차이가 있을 때 어떻게 합의점을 찾으시나요?",
                intent="협업 능력과 커뮤니케이션 스킬을 평가합니다.",
                category="Behavioral"
            ),
            InterviewQuestion(
                question="현재 시스템에서 성능 병목이 발생한다면 어떤 순서로 문제를 진단하시겠습니까?",
                intent="시스템 성능 최적화에 대한 접근 방식을 평가합니다.",
                category="Problem Solving"
            ),
            InterviewQuestion(
                question="향후 5년간 본인의 기술적 성장 목표는 무엇인가요?",
                intent="자기계발 의지와 장기적 비전을 평가합니다.",
                category="Career Vision"
            )
        ]
        
        sample_learning_path = LearningPath(
            summary=f"현재 {', '.join(payload.technical_skills[:3])} 경험을 바탕으로 시니어 개발자로 성장하기 위한 체계적인 학습 경로를 제안합니다.",
            steps=[
                LearningStep(
                    title="아키텍처 설계 역량 강화",
                    description="대규모 시스템 설계 경험을 쌓기 위한 사이드 프로젝트 진행",
                    resources=["System Design Interview", "마이크로서비스 패턴", "클린 아키텍처"]
                ),
                LearningStep(
                    title="기술 리더십 개발",
                    description="코드 리뷰 문화 도입 및 기술 문서화 경험 쌓기",
                    resources=["Effective Code Review", "기술 블로그 운영", "컨퍼런스 발표"]
                ),
                LearningStep(
                    title="최신 기술 스택 학습",
                    description="클라우드 네이티브 기술 스택으로 토이 프로젝트 구현",
                    resources=["Kubernetes", "Docker", "AWS/GCP 인증"]
                )
            ]
        )
        
        result = CoachingResult(
            session_id=uuid4(),
            interview_questions=sample_questions,
            learning_path=sample_learning_path
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코칭 세션 생성 중 오류가 발생했습니다: {str(e)}"
        )