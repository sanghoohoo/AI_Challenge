import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.schemas.coaching import (
    CoachingResult,
    InterviewQuestion,
    LearningPath,
    LearningStep,
)
from uuid import uuid4


@pytest.fixture
def client():
    """테스트 클라이언트 픽스처"""
    return TestClient(app)


@pytest.fixture
def sample_request():
    """샘플 요청 데이터"""
    return {
        "career_summary": "3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
        "job_duties": "주문 및 결제 시스템 MSA 전환 프로젝트 리딩, Python 기반 데이터 배치 처리 시스템 구축",
        "technical_skills": ["Spring Boot", "MSA", "Python", "AWS EC2", "MySQL"],
    }


@pytest.fixture
def mock_coaching_result():
    """모킹된 코칭 결과"""
    return CoachingResult(
        session_id=uuid4(),
        interview_questions=[
            InterviewQuestion(
                question="테스트 면접 질문",
                intent="테스트 의도",
                category="Technical Deep-Dive",
            )
        ],
        learning_path=LearningPath(
            summary="테스트 학습 경로 요약",
            steps=[
                LearningStep(
                    title="테스트 단계",
                    description="테스트 설명",
                    resources=["테스트 리소스"],
                )
            ],
        ),
    )


class TestRootEndpoints:
    """루트 엔드포인트 테스트"""

    def test_root_endpoint(self, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "AI Career Coach API is running!"

    def test_health_endpoint(self, client):
        """헬스체크 엔드포인트 테스트"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "environment" in data


class TestCoachingEndpoints:
    """코칭 엔드포인트 테스트"""

    @patch("app.services.coaching_service.CoachingService.create_coaching_session")
    def test_create_coaching_session_success(
        self, mock_create_session, client, sample_request, mock_coaching_result
    ):
        """코칭 세션 생성 성공 테스트"""
        # 5개 질문으로 수정
        mock_result = CoachingResult(
            session_id=uuid4(),
            interview_questions=[
                InterviewQuestion(
                    question=f"테스트 면접 질문 {i+1}",
                    intent=f"테스트 의도 {i+1}",
                    category="Technical Deep-Dive",
                ) for i in range(5)
            ],
            learning_path=LearningPath(
                summary="테스트 학습 경로 요약",
                steps=[
                    LearningStep(
                        title="테스트 단계",
                        description="테스트 설명",
                        resources=["테스트 리소스"],
                    )
                ],
            ),
        )
        mock_create_session.return_value = mock_result

        response = client.post("/api/v1/coaching-sessions", json=sample_request)

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "interview_questions" in data
        assert "learning_path" in data
        assert len(data["interview_questions"]) == 5
        assert "summary" in data["learning_path"]
        assert "steps" in data["learning_path"]

    def test_create_coaching_session_invalid_request(self, client):
        """잘못된 요청 데이터 테스트"""
        invalid_request = {
            "career_summary": "",  # 빈 문자열
            "job_duties": "a",  # 너무 짧음
            "technical_skills": [],  # 빈 배열
        }

        response = client.post("/api/v1/coaching-sessions", json=invalid_request)

        assert response.status_code == 422  # Validation Error

    def test_create_coaching_session_missing_fields(self, client):
        """필수 필드 누락 테스트"""
        incomplete_request = {
            "career_summary": "3년차 개발자"
            # job_duties와 technical_skills 누락
        }

        response = client.post("/api/v1/coaching-sessions", json=incomplete_request)

        assert response.status_code == 422

    def test_create_coaching_session_field_validation(self, client):
        """필드 유효성 검사 테스트"""
        # 너무 짧은 career_summary
        short_summary_request = {
            "career_summary": "짧음",  # 10자 미만
            "job_duties": "충분히 긴 직무 설명입니다",
            "technical_skills": ["Python"],
        }

        response = client.post("/api/v1/coaching-sessions", json=short_summary_request)
        assert response.status_code == 422

        # 너무 많은 기술 스킬
        too_many_skills_request = {
            "career_summary": "충분히 긴 경력 요약입니다",
            "job_duties": "충분히 긴 직무 설명입니다",
            "technical_skills": [f"skill_{i}" for i in range(25)],  # 20개 초과
        }

        response = client.post(
            "/api/v1/coaching-sessions", json=too_many_skills_request
        )
        assert response.status_code == 422

    @patch("app.services.coaching_service.CoachingService.create_coaching_session")
    def test_create_coaching_session_service_error(
        self, mock_create_session, client, sample_request
    ):
        """코칭 서비스 오류 테스트"""
        from app.services.coaching_service import CoachingServiceError

        mock_create_session.side_effect = CoachingServiceError("테스트 서비스 오류")

        response = client.post("/api/v1/coaching-sessions", json=sample_request)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    @patch("app.services.coaching_service.CoachingService.create_coaching_session")
    def test_create_coaching_session_llm_error(
        self, mock_create_session, client, sample_request
    ):
        """LLM 서비스 오류 테스트"""
        from app.services.coaching_service import CoachingServiceError

        mock_create_session.side_effect = CoachingServiceError("LLM API 호출 실패")

        response = client.post("/api/v1/coaching-sessions", json=sample_request)

        assert response.status_code == 503  # LLM 관련 오류는 503
        data = response.json()
        assert "AI 서비스 일시적 오류" in data["detail"]

    @patch("app.services.coaching_service.CoachingService.health_check")
    def test_health_check_success(self, mock_health_check, client):
        """헬스체크 성공 테스트"""
        mock_health_check.return_value = True

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["llm_service"] == "available"
        assert "message" in data

    @patch("app.services.coaching_service.CoachingService.health_check")
    def test_health_check_failure(self, mock_health_check, client):
        """헬스체크 실패 테스트"""
        mock_health_check.return_value = False

        response = client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert "LLM 서비스 연결 불가" in data["detail"]

    def test_response_format_validation(self, client, sample_request):
        """응답 형식 검증 테스트"""
        # 실제 API 호출 없이 스키마 검증
        from app.schemas.coaching import CoachingResult

        # 스키마 검증을 위한 샘플 데이터
        sample_response = {
            "session_id": str(uuid4()),
            "interview_questions": [
                {
                    "question": f"테스트 질문 {i+1}",
                    "intent": f"테스트 의도 {i+1}",
                    "category": "Technical Deep-Dive",
                } for i in range(5)
            ],
            "learning_path": {
                "summary": "테스트 요약",
                "steps": [
                    {
                        "title": "테스트 제목",
                        "description": "테스트 설명",
                        "resources": ["리소스1", "리소스2"],
                    }
                ],
            },
        }

        # Pydantic 스키마로 검증
        result = CoachingResult(**sample_response)
        assert result.session_id is not None
        assert len(result.interview_questions) == 5
        assert result.learning_path.summary == "테스트 요약"

    def test_cors_headers(self, client, sample_request):
        """CORS 헤더 테스트"""
        response = client.options("/api/v1/coaching-sessions")

        # CORS 관련 헤더 확인
        assert response.status_code in [200, 204]


class TestAPIDocumentation:
    """API 문서 관련 테스트"""

    def test_openapi_schema_accessible(self, client):
        """OpenAPI 스키마 접근 테스트"""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_ui_accessible(self, client):
        """Swagger UI 접근 테스트"""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_accessible(self, client):
        """ReDoc 접근 테스트"""
        response = client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
