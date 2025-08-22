import json
import logging
from typing import List
from uuid import uuid4

from app.schemas.coaching import (
    ResumePayload,
    CoachingResult,
    InterviewQuestion,
    LearningPath,
    LearningStep,
)
from app.services.llm_client import get_llm_client, LLMClientError
from app.services.prompt_builder import get_prompt_builder
from app.services.quality_evaluator import get_quality_evaluator

logger = logging.getLogger(__name__)


class CoachingServiceError(Exception):
    """코칭 서비스 관련 오류"""

    pass


class CoachingService:
    """커리어 코칭 핵심 비즈니스 로직을 담당하는 서비스"""

    def __init__(self):
        self.llm_client = get_llm_client()
        self.prompt_builder = get_prompt_builder()
        self.quality_evaluator = get_quality_evaluator()

    async def create_coaching_session(
        self, resume_data: ResumePayload, enable_quality_optimization: bool = True
    ) -> CoachingResult:
        """
        이력서 데이터를 기반으로 개인 맞춤형 코칭 세션 생성

        Args:
            resume_data: 이력서 정보

        Returns:
            생성된 코칭 결과

        Raises:
            CoachingServiceError: 코칭 세션 생성 실패
        """
        try:
            logger.info(f"코칭 세션 생성 시작: {resume_data.career_summary[:50]}...")

            if enable_quality_optimization:
                # 품질 최적화 모드: 여러 전략으로 생성하고 최고 품질 선택
                result = await self._create_optimized_session(resume_data)
            else:
                # 일반 모드: 단일 전략으로 생성
                result = await self._create_standard_session(resume_data)

            logger.info(f"코칭 세션 생성 완료: {result.session_id}")
            return result

        except Exception as e:
            logger.error(f"코칭 세션 생성 실패: {str(e)}")
            raise CoachingServiceError(f"코칭 세션 생성 중 오류 발생: {str(e)}")

    async def _create_optimized_session(
        self, resume_data: ResumePayload
    ) -> CoachingResult:
        """품질 최적화된 코칭 세션 생성 (A/B 테스트)"""
        import asyncio

        logger.info("품질 최적화 모드로 세션 생성 중...")

        # 다양한 전략으로 병렬 생성
        strategies = ["balanced", "technical_deep", "system_design"]
        personas = ["senior_engineer", "tech_lead", "platform_architect"]

        tasks = []
        for strategy in strategies:
            for persona in personas:
                task = self._generate_candidate_session(resume_data, persona, strategy)
                tasks.append(task)

        # 모든 후보 결과 생성
        candidates = await asyncio.gather(*tasks, return_exceptions=True)

        # 유효한 결과만 필터링
        valid_candidates = []
        for candidate in candidates:
            if not isinstance(candidate, Exception):
                try:
                    # 품질 평가
                    quality_score = self.quality_evaluator.evaluate_coaching_result(
                        candidate, resume_data
                    )
                    valid_candidates.append((candidate, quality_score))
                    logger.info(f"후보 세션 품질 점수: {quality_score.overall:.2f}")
                except Exception as e:
                    logger.warning(f"품질 평가 실패: {str(e)}")

        if not valid_candidates:
            logger.warning("모든 최적화 시도 실패, 표준 모드로 대체")
            return await self._create_standard_session(resume_data)

        # 최고 품질 선택
        best_candidate, best_score = max(valid_candidates, key=lambda x: x[1].overall)

        logger.info(f"최적 세션 선택됨. 품질 점수: {best_score.overall:.2f}")
        logger.info(
            f"개선 제안: {self.quality_evaluator.generate_improvement_suggestions(best_score)}"
        )

        return best_candidate

    async def _create_standard_session(
        self, resume_data: ResumePayload
    ) -> CoachingResult:
        """표준 코칭 세션 생성"""

        # 병렬로 면접 질문과 학습 경로 생성
        interview_questions_task = self._generate_interview_questions(resume_data)
        learning_path_task = self._generate_learning_path(resume_data)

        # 두 작업 동시 실행
        import asyncio

        interview_questions, learning_path = await asyncio.gather(
            interview_questions_task, learning_path_task, return_exceptions=True
        )

        # 예외 처리
        if isinstance(interview_questions, Exception):
            raise interview_questions
        if isinstance(learning_path, Exception):
            raise learning_path

        # 결과 조합
        result = CoachingResult(
            session_id=uuid4(),
            interview_questions=interview_questions,
            learning_path=learning_path,
        )

        return result

    async def _generate_candidate_session(
        self, resume_data: ResumePayload, persona: str, strategy: str
    ) -> CoachingResult:
        """특정 페르소나와 전략으로 후보 세션 생성"""
        try:
            # 커스텀 프롬프트로 생성
            interview_questions = await self._generate_interview_questions(
                resume_data, persona, strategy
            )
            learning_path = await self._generate_learning_path(resume_data, persona)

            return CoachingResult(
                session_id=uuid4(),
                interview_questions=interview_questions,
                learning_path=learning_path,
            )
        except Exception as e:
            logger.warning(
                f"후보 세션 생성 실패 (persona={persona}, strategy={strategy}): {str(e)}"
            )
            raise e

    async def _generate_interview_questions(
        self, resume_data: ResumePayload, persona_type: str = None, strategy: str = None
    ) -> List[InterviewQuestion]:
        """면접 질문 생성"""
        try:
            # 프롬프트 구성
            prompt = self.prompt_builder.build_interview_questions_prompt(
                resume_data, persona_type, strategy
            )

            # LLM 호출
            response = await self.llm_client.generate_json_completion(
                prompt=prompt,
                model="gpt-3.5-turbo-1106",
                temperature=0.7,
                max_tokens=2000,
            )

            # JSON 파싱
            try:
                parsed_response = json.loads(response)
                questions_data = parsed_response.get("interview_questions", [])

                if len(questions_data) != 5:
                    raise ValueError(
                        f"예상된 5개 질문이 아닌 {len(questions_data)}개 질문이 생성됨"
                    )

                # Pydantic 모델로 변환
                questions = []
                for q_data in questions_data:
                    question = InterviewQuestion(
                        question=q_data["question"],
                        intent=q_data["intent"],
                        category=q_data["category"],
                    )
                    questions.append(question)

                logger.info(f"면접 질문 {len(questions)}개 생성 완료")
                return questions

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"LLM 응답 파싱 실패, 대체 로직 사용: {str(e)}")
                return self._generate_fallback_questions(resume_data)

        except LLMClientError as e:
            logger.error(f"LLM 호출 실패: {str(e)}")
            raise CoachingServiceError(f"면접 질문 생성 실패: {str(e)}")

    async def _generate_learning_path(
        self, resume_data: ResumePayload, persona_type: str = None
    ) -> LearningPath:
        """학습 경로 생성"""
        try:
            # 프롬프트 구성
            prompt = self.prompt_builder.build_learning_path_prompt(
                resume_data, persona_type
            )

            # LLM 호출
            response = await self.llm_client.generate_json_completion(
                prompt=prompt,
                model="gpt-3.5-turbo-1106",
                temperature=0.7,
                max_tokens=1500,
            )

            # JSON 파싱
            try:
                parsed_response = json.loads(response)
                path_data = parsed_response.get("learning_path", {})

                # 학습 단계 변환
                steps = []
                for step_data in path_data.get("steps", []):
                    step = LearningStep(
                        title=step_data["title"],
                        description=step_data["description"],
                        resources=step_data["resources"],
                    )
                    steps.append(step)

                learning_path = LearningPath(summary=path_data["summary"], steps=steps)

                logger.info(f"학습 경로 생성 완료: {len(steps)}개 단계")
                return learning_path

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"LLM 응답 파싱 실패, 대체 로직 사용: {str(e)}")
                return self._generate_fallback_learning_path(resume_data)

        except LLMClientError as e:
            logger.error(f"LLM 호출 실패: {str(e)}")
            raise CoachingServiceError(f"학습 경로 생성 실패: {str(e)}")

    def _generate_fallback_questions(
        self, resume_data: ResumePayload
    ) -> List[InterviewQuestion]:
        """LLM 실패 시 대체 면접 질문 생성"""
        logger.info("대체 면접 질문 생성 중...")

        # 기술 스킬 기반 질문 생성
        primary_skills = resume_data.technical_skills[:3]

        questions = [
            InterviewQuestion(
                question=f"{resume_data.career_summary}을 바탕으로, 가장 도전적이었던 기술적 문제는 무엇이었고 어떻게 해결하셨나요?",
                intent="문제 해결 능력과 기술적 깊이를 평가합니다.",
                category="Technical Deep-Dive",
            ),
            InterviewQuestion(
                question=f"{', '.join(primary_skills)} 기술을 사용한 프로젝트에서 성능 최적화를 어떻게 진행하셨나요?",
                intent="성능 최적화 경험과 기술적 접근 방식을 검증합니다.",
                category="System Design",
            ),
            InterviewQuestion(
                question="팀원과 기술적 의견 차이가 있을 때 어떻게 해결하시나요?",
                intent="협업 능력과 커뮤니케이션 스킬을 평가합니다.",
                category="Behavioral",
            ),
            InterviewQuestion(
                question="현재 시스템에서 장애가 발생했을 때의 대응 절차를 설명해주세요.",
                intent="장애 대응 능력과 시스템 운영 경험을 평가합니다.",
                category="Problem Solving",
            ),
            InterviewQuestion(
                question="향후 3-5년간 기술적 성장 목표는 무엇인가요?",
                intent="자기계발 의지와 장기적 비전을 평가합니다.",
                category="Career Vision",
            ),
        ]

        return questions

    def _generate_fallback_learning_path(
        self, resume_data: ResumePayload
    ) -> LearningPath:
        """LLM 실패 시 대체 학습 경로 생성"""
        logger.info("대체 학습 경로 생성 중...")

        primary_skills = resume_data.technical_skills[:3]

        steps = [
            LearningStep(
                title="기술적 깊이 강화",
                description=f"현재 보유한 {', '.join(primary_skills)} 기술의 고급 개념과 최적화 기법을 학습하고 실제 프로젝트에 적용",
                resources=[f"{skill} 고급 가이드" for skill in primary_skills[:2]]
                + ["성능 최적화 패턴"],
            ),
            LearningStep(
                title="시스템 설계 역량 개발",
                description="대규모 시스템 아키텍처 설계 경험을 쌓기 위한 사이드 프로젝트 진행",
                resources=[
                    "System Design Interview",
                    "마이크로서비스 아키텍처",
                    "분산 시스템 설계",
                ],
            ),
            LearningStep(
                title="기술 리더십 함양",
                description="코드 리뷰 문화 구축, 기술 문서 작성, 팀 내 지식 공유 활동 참여",
                resources=[
                    "Effective Code Review",
                    "기술 블로깅",
                    "컨퍼런스 발표 준비",
                ],
            ),
        ]

        return LearningPath(
            summary=f"현재 {', '.join(primary_skills)} 경험을 바탕으로 시니어 개발자로 성장하기 위한 체계적인 학습 경로를 제안합니다.",
            steps=steps,
        )

    async def health_check(self) -> bool:
        """서비스 상태 확인"""
        try:
            return await self.llm_client.health_check()
        except Exception as e:
            logger.error(f"코칭 서비스 헬스체크 실패: {str(e)}")
            return False


# 전역 코칭 서비스 인스턴스
_coaching_service = None


def get_coaching_service() -> CoachingService:
    """코칭 서비스 싱글톤 인스턴스 반환"""
    global _coaching_service

    if _coaching_service is None:
        _coaching_service = CoachingService()

    return _coaching_service
