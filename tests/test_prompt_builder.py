from app.services.prompt_builder import PromptBuilder
from app.schemas.coaching import ResumePayload


class TestPromptBuilder:
    """프롬프트 빌더 단위 테스트"""

    def setup_method(self):
        """각 테스트 전 실행"""
        self.prompt_builder = PromptBuilder()
        self.sample_resume = ResumePayload(
            career_summary="3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
            job_duties="주문 및 결제 시스템 MSA 전환 프로젝트 리딩, Python 기반 데이터 배치 처리 시스템 구축",
            technical_skills=["Spring Boot", "MSA", "Python", "AWS EC2", "MySQL"],
        )

    def test_select_optimal_persona_aws_experience(self):
        """AWS 경험이 있으면 platform_architect 선택"""
        resume = ResumePayload(
            career_summary="클라우드 엔지니어",
            job_duties="AWS 인프라 구축",
            technical_skills=["AWS", "Docker", "Kubernetes"],
        )

        persona = self.prompt_builder._select_optimal_persona(resume)
        assert persona == "platform_architect"

    def test_select_optimal_persona_startup_experience(self):
        """스타트업 경험이 있으면 startup_cto 선택"""
        resume = ResumePayload(
            career_summary="스타트업 백엔드 개발자",
            job_duties="빠른 개발",
            technical_skills=["Node.js"],
        )

        persona = self.prompt_builder._select_optimal_persona(resume)
        assert persona == "startup_cto"

    def test_select_optimal_persona_lead_experience(self):
        """리드 경험이 있으면 tech_lead 선택"""
        resume = ResumePayload(
            career_summary="팀 리드 개발자",
            job_duties="팀 관리",
            technical_skills=["Java"],
        )

        persona = self.prompt_builder._select_optimal_persona(resume)
        assert persona == "tech_lead"

    def test_select_optimal_persona_default(self):
        """기본값은 senior_engineer"""
        resume = ResumePayload(
            career_summary="일반 개발자",
            job_duties="웹 개발",
            technical_skills=["JavaScript"],
        )

        persona = self.prompt_builder._select_optimal_persona(resume)
        assert persona == "senior_engineer"

    def test_determine_strategy_system_design(self):
        """MSA 키워드가 많으면 system_design 전략"""
        resume = ResumePayload(
            career_summary="MSA 아키텍트",
            job_duties="마이크로서비스 아키텍처 설계, 분산 시스템 구축",
            technical_skills=["MSA"],
        )

        strategy = self.prompt_builder._determine_strategy(resume)
        assert strategy == "system_design"

    def test_determine_strategy_technical_deep(self):
        """고급 기술 스택이 많으면 technical_deep 전략"""
        resume = ResumePayload(
            career_summary="개발자",
            job_duties="개발",
            technical_skills=["Kubernetes", "Kafka", "Redis", "Elasticsearch"],
        )

        strategy = self.prompt_builder._determine_strategy(resume)
        assert strategy == "technical_deep"

    def test_determine_strategy_behavioral_heavy(self):
        """관리 경험이 있으면 behavioral_heavy 전략"""
        resume = ResumePayload(
            career_summary="개발자",
            job_duties="프로젝트 관리, 팀 리딩, 멘토링",
            technical_skills=["Java"],
        )

        strategy = self.prompt_builder._determine_strategy(resume)
        assert strategy == "behavioral_heavy"

    def test_determine_strategy_default(self):
        """기본값은 balanced 전략"""
        resume = ResumePayload(
            career_summary="개발자", job_duties="웹 개발", technical_skills=["Python"]
        )

        strategy = self.prompt_builder._determine_strategy(resume)
        assert strategy == "balanced"

    def test_build_interview_questions_prompt_contains_persona(self):
        """면접 질문 프롬프트에 페르소나가 포함되는지 확인"""
        prompt = self.prompt_builder.build_interview_questions_prompt(
            self.sample_resume
        )

        assert "페르소나 설정" in prompt
        assert "실리콘밸리" in prompt or "기술 리더" in prompt or "스타트업" in prompt

    def test_build_interview_questions_prompt_contains_resume_data(self):
        """면접 질문 프롬프트에 이력서 데이터가 포함되는지 확인"""
        prompt = self.prompt_builder.build_interview_questions_prompt(
            self.sample_resume
        )

        assert "3년차 백엔드 개발자" in prompt
        assert "Spring Boot" in prompt
        assert "MSA" in prompt

    def test_build_interview_questions_prompt_contains_cot(self):
        """면접 질문 프롬프트에 Chain-of-Thought가 포함되는지 확인"""
        prompt = self.prompt_builder.build_interview_questions_prompt(
            self.sample_resume
        )

        assert "연쇄적 사고" in prompt
        assert "경력 수준 평가" in prompt
        assert "개인화 강화" in prompt

    def test_build_interview_questions_prompt_contains_defensive_prompting(self):
        """면접 질문 프롬프트에 방어적 프롬프팅이 포함되는지 확인"""
        prompt = self.prompt_builder.build_interview_questions_prompt(
            self.sample_resume
        )

        assert "방어적 프롬프팅" in prompt
        assert "분석용으로만 사용" in prompt

    def test_build_learning_path_prompt_contains_persona(self):
        """학습 경로 프롬프트에 페르소나가 포함되는지 확인"""
        prompt = self.prompt_builder.build_learning_path_prompt(self.sample_resume)

        assert "페르소나 설정" in prompt
        assert "전문가" in prompt

    def test_build_learning_path_prompt_contains_gap_analysis(self):
        """학습 경로 프롬프트에 격차 분석이 포함되는지 확인"""
        prompt = self.prompt_builder.build_learning_path_prompt(self.sample_resume)

        assert "격차 분석" in prompt
        assert "현재 수준 평가" in prompt
        assert "목표 수준 설정" in prompt

    def test_get_interview_question_examples_strategy_specific(self):
        """전략별로 다른 예시가 반환되는지 확인"""
        system_design_examples = self.prompt_builder._get_interview_question_examples(
            "system_design"
        )
        technical_deep_examples = self.prompt_builder._get_interview_question_examples(
            "technical_deep"
        )

        assert system_design_examples != technical_deep_examples
        assert "System Design" in system_design_examples
        assert "Technical Deep-Dive" in technical_deep_examples

    def test_custom_persona_override(self):
        """명시적 페르소나 지정이 작동하는지 확인"""
        persona = self.prompt_builder._select_optimal_persona(
            self.sample_resume, "faang_staff"
        )
        assert persona == "faang_staff"

    def test_prompt_contains_json_format_requirement(self):
        """프롬프트에 JSON 형식 요구사항이 포함되는지 확인"""
        prompt = self.prompt_builder.build_interview_questions_prompt(
            self.sample_resume
        )

        assert "JSON 형식" in prompt
        assert "interview_questions" in prompt
        assert "question" in prompt
        assert "intent" in prompt
        assert "category" in prompt
