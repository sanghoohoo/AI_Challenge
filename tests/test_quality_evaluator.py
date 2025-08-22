from app.services.quality_evaluator import QualityEvaluator, QualityScore
from app.schemas.coaching import (
    ResumePayload,
    CoachingResult,
    InterviewQuestion,
    LearningPath,
    LearningStep,
)
from uuid import uuid4


class TestQualityEvaluator:
    """품질 평가자 단위 테스트"""

    def setup_method(self):
        """각 테스트 전 실행"""
        self.evaluator = QualityEvaluator()
        self.sample_resume = ResumePayload(
            career_summary="3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
            job_duties="주문 및 결제 시스템 MSA 전환 프로젝트 리딩",
            technical_skills=["Spring Boot", "MSA", "Python", "AWS", "MySQL"],
        )

    def test_calculate_relevance_high_score(self):
        """높은 관련성 점수 테스트"""
        text = "spring boot msa python aws 커머스 주문 결제 시스템"
        score = self.evaluator._calculate_relevance(text, self.sample_resume)
        assert score >= 4.0

    def test_calculate_relevance_low_score(self):
        """낮은 관련성 점수 테스트"""
        text = "react vue angular frontend javascript"
        score = self.evaluator._calculate_relevance(text, self.sample_resume)
        assert score <= 2.0

    def test_calculate_depth_high_score(self):
        """높은 깊이 점수 테스트"""
        question_text = "구체적으로 단계별 아키텍처 설계 과정을 설명하며 trade-off와 경험을 바탕으로 최적화 방법론을 제시해주세요"
        intent_text = "시스템 설계 능력과 기술적 깊이를 평가합니다"
        score = self.evaluator._calculate_depth(question_text, intent_text)
        assert score >= 4.0

    def test_calculate_depth_low_score(self):
        """낮은 깊이 점수 테스트"""
        question_text = "개발하세요"
        intent_text = "평가"
        score = self.evaluator._calculate_depth(question_text, intent_text)
        assert score <= 2.0

    def test_calculate_question_answerability_high(self):
        """높은 답변가능성 점수 테스트"""
        question_text = (
            "프로젝트에서 실제로 경험한 구체적인 사례를 단계별로 설명해주세요"
        )
        score = self.evaluator._calculate_question_answerability(question_text)
        assert score >= 4.0

    def test_calculate_question_answerability_low(self):
        """낮은 답변가능성 점수 테스트"""
        question_text = "일반적으로 보통 대부분의 경우"
        score = self.evaluator._calculate_question_answerability(question_text)
        assert score <= 3.0

    def test_calculate_learning_actionability_high(self):
        """높은 실행가능성 점수 테스트"""
        steps = [
            type(
                "Step",
                (),
                {
                    "title": "프로젝트 구축",
                    "description": "구체적인 구현과 학습을 통해 실습 진행",
                    "resources": ["Spring Boot", "MSA 패턴"],
                },
            )()
        ]
        score = self.evaluator._calculate_learning_actionability(steps)
        assert score >= 3.0

    def test_calculate_learning_actionability_low(self):
        """낮은 실행가능성 점수 테스트"""
        steps = [
            type(
                "Step", (), {"title": "학습", "description": "공부", "resources": []}
            )()
        ]
        score = self.evaluator._calculate_learning_actionability(steps)
        assert score <= 3.0

    def test_evaluate_interview_questions_quality(self):
        """면접 질문 품질 평가 테스트"""
        questions = [
            InterviewQuestion(
                question="Spring Boot MSA 전환 프로젝트에서 구체적으로 어떤 아키텍처 패턴을 적용했나요?",
                intent="MSA 설계 능력과 실무 경험을 평가합니다",
                category="Technical Deep-Dive",
            ),
            InterviewQuestion(
                question="커머스 시스템에서 결제 서비스의 트랜잭션 처리를 어떻게 구현했나요?",
                intent="분산 트랜잭션 처리 능력을 검증합니다",
                category="System Design",
            ),
        ]

        score = self.evaluator._evaluate_interview_questions(
            questions, self.sample_resume
        )

        assert isinstance(score, QualityScore)
        assert 1.0 <= score.relevance <= 5.0
        assert 1.0 <= score.depth <= 5.0
        assert 1.0 <= score.actionability <= 5.0
        assert 1.0 <= score.practicality <= 5.0
        assert score.overall > 0

    def test_evaluate_learning_path_quality(self):
        """학습 경로 품질 평가 테스트"""
        learning_path = LearningPath(
            summary="Spring Boot와 MSA 기반 커머스 시스템 구축 경험을 바탕으로 확장성 있는 아키텍처 설계 능력을 강화",
            steps=[
                LearningStep(
                    title="MSA 아키텍처 심화",
                    description=(
                        "3개의 마이크로서비스로 구성된 주문 처리 시스템을 "
                        "구축하고 gRPC 통신을 적용하여 실무 경험 확장"
                    ),
                    resources=["MSA 패턴", "gRPC", "분산 시스템 설계"],
                ),
                LearningStep(
                    title="성능 최적화 프로젝트",
                    description="현재 Python 배치 처리 시스템의 성능을 측정하고 병목점을 찾아 구체적인 최적화 방안 적용",
                    resources=["Python 성능 튜닝", "프로파일링", "캐싱 전략"],
                ),
            ],
        )

        score = self.evaluator._evaluate_learning_path(
            learning_path, self.sample_resume
        )

        assert isinstance(score, QualityScore)
        assert score.relevance >= 3.0  # MSA, Python 등 관련 키워드 포함
        assert score.actionability >= 3.0  # 구체적인 프로젝트 제안

    def test_evaluate_coaching_result_overall(self):
        """전체 코칭 결과 품질 평가 테스트"""
        result = CoachingResult(
            session_id=uuid4(),
            interview_questions=[
                InterviewQuestion(
                    question="MSA 전환 프로젝트에서 마주한 주요 기술적 도전과제는?",
                    intent="실무 경험과 문제 해결 능력 평가",
                    category="Technical Deep-Dive",
                ),
                InterviewQuestion(
                    question="Spring Boot 성능 최적화 경험",
                    intent="기술적 깊이 평가",
                    category="Technical Deep-Dive",
                ),
                InterviewQuestion(
                    question="결제 시스템 설계 과정",
                    intent="시스템 설계 능력",
                    category="System Design",
                ),
                InterviewQuestion(
                    question="팀 리더십 경험",
                    intent="행동 역량 평가",
                    category="Behavioral",
                ),
                InterviewQuestion(
                    question="문제 해결 프로세스",
                    intent="문제 해결 능력",
                    category="Problem Solving",
                ),
            ],
            learning_path=LearningPath(
                summary="현재 백엔드 개발 경험을 바탕으로 시니어 레벨 성장",
                steps=[
                    LearningStep(
                        title="아키텍처 설계 역량 강화",
                        description="대규모 시스템 설계 프로젝트 진행",
                        resources=["시스템 설계", "아키텍처 패턴"],
                    )
                ],
            ),
        )

        score = self.evaluator.evaluate_coaching_result(result, self.sample_resume)

        assert isinstance(score, QualityScore)
        assert 1.0 <= score.overall <= 5.0
        assert score.relevance > 0
        assert score.depth > 0
        assert score.actionability > 0
        assert score.practicality > 0

    def test_generate_improvement_suggestions_low_scores(self):
        """낮은 점수에 대한 개선 제안 테스트"""
        low_score = QualityScore(
            relevance=2.0, depth=2.5, actionability=2.0, practicality=2.5, overall=2.25
        )

        suggestions = self.evaluator.generate_improvement_suggestions(low_score)

        assert len(suggestions) > 0
        assert any("이력서" in suggestion for suggestion in suggestions)
        assert any("구체적" in suggestion for suggestion in suggestions)

    def test_generate_improvement_suggestions_high_scores(self):
        """높은 점수에 대한 개선 제안 테스트"""
        high_score = QualityScore(
            relevance=4.5, depth=4.0, actionability=4.2, practicality=4.1, overall=4.2
        )

        suggestions = self.evaluator.generate_improvement_suggestions(high_score)

        assert "✅ 우수한 품질의 결과물입니다!" in suggestions

    def test_quality_score_to_dict(self):
        """품질 점수의 딕셔너리 변환 테스트"""
        score = QualityScore(
            relevance=4.0, depth=3.5, actionability=4.2, practicality=3.8, overall=3.875
        )

        score_dict = score.to_dict()

        assert isinstance(score_dict, dict)
        assert "relevance" in score_dict
        assert "depth" in score_dict
        assert "actionability" in score_dict
        assert "practicality" in score_dict
        assert "overall" in score_dict
        assert score_dict["relevance"] == 4.0

    def test_empty_steps_handling(self):
        """빈 학습 단계 처리 테스트"""
        empty_steps = []

        depth_score = self.evaluator._calculate_learning_depth(empty_steps)
        actionability_score = self.evaluator._calculate_learning_actionability(
            empty_steps
        )
        practicality_score = self.evaluator._calculate_learning_practicality(
            empty_steps
        )

        assert depth_score == 1.0
        assert actionability_score == 1.0
        assert practicality_score == 1.0
