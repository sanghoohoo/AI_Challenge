from typing import List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ResumePayload(BaseModel):
    """Request model for coaching session creation."""

    career_summary: str = Field(
        ...,
        description=(
            "경력 요약 (예: 3년차 백엔드 개발자, "
            "Spring Boot/MSA/Python 기반 커머스 서비스 개발)"
        ),
        min_length=10,
        max_length=500,
    )
    job_duties: str = Field(
        ...,
        description=("수행 직무 (예: 주문 및 결제 시스템 " "MSA 전환 프로젝트 리딩)"),
        min_length=10,
        max_length=1000,
    )
    technical_skills: List[str] = Field(
        ..., description="보유 기술 스킬 리스트", min_items=1, max_items=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "career_summary": "3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
                "job_duties": "주문 및 결제 시스템 MSA 전환 프로젝트 리딩, Python 기반 데이터 배치 처리 시스템 구축",
                "technical_skills": [
                    "Spring Boot",
                    "MSA",
                    "Python",
                    "AWS EC2",
                    "MySQL",
                ],
            }
        }


class InterviewQuestion(BaseModel):
    """Individual interview question model."""

    question: str = Field(..., description="생성된 면접 질문")
    intent: str = Field(..., description="이 질문을 하는 의도")
    category: str = Field(
        ..., description="질문 유형 (예: Technical Deep-Dive, Behavioral, Situational)"
    )


class LearningStep(BaseModel):
    """Individual learning step model."""

    title: str = Field(..., description="학습 단계 제목")
    description: str = Field(..., description="구체적인 실행 방안")
    resources: List[str] = Field(..., description="강의나 서적 검색을 위한 추천 키워드")


class LearningPath(BaseModel):
    """Learning path recommendation model."""

    summary: str = Field(..., description="추천 경로에 대한 고수준 요약")
    steps: List[LearningStep] = Field(..., description="구체적인 학습 단계들")


class CoachingResult(BaseModel):
    """Response model for coaching session."""

    session_id: UUID = Field(
        default_factory=uuid4, description="코칭 세션의 고유 식별자"
    )
    interview_questions: List[InterviewQuestion] = Field(
        ..., description="생성된 면접 질문들 (5개)", min_items=5, max_items=5
    )
    learning_path: LearningPath = Field(..., description="개인 맞춤형 학습 경로")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "interview_questions": [
                    {
                        "question": "이커머스 서비스의 트래픽이 10배 증가했을 때, 현재 아키텍처에서 가장 먼저 병목이 발생할 것으로 예상되는 지점은 어디이며, 이를 해결하기 위한 단계별 계획을 설명해주십시오.",
                        "intent": "시스템 확장성에 대한 이해도와 구체적인 문제 해결 능력을 평가합니다.",
                        "category": "System Design",
                    }
                ],
                "learning_path": {
                    "summary": "현재 보유한 MSA 경험을 바탕으로, 대용량 트래픽 처리 및 분산 시스템의 안정성 확보 역량을 강화하는 것을 추천합니다.",
                    "steps": [
                        {
                            "title": "MSA 지식 심화",
                            "description": "Kafka로 통신하는 3개의 마이크로서비스 사이드 프로젝트 구축",
                            "resources": [
                                "Spring Cloud",
                                "Apache Kafka",
                                "분산 트랜잭션 패턴",
                            ],
                        }
                    ],
                },
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="에러 상세 메시지")
