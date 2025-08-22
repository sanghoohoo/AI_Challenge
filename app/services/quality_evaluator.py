import re
from typing import List, Dict, Any
from dataclasses import dataclass
from app.schemas.coaching import CoachingResult, ResumePayload


@dataclass
class QualityScore:
    """품질 평가 점수"""
    relevance: float  # 관련성 (1-5점)
    depth: float      # 깊이 (1-5점)
    actionability: float  # 실행가능성 (1-5점)
    practicality: float   # 실용성 (1-5점)
    overall: float    # 전체 점수
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "relevance": self.relevance,
            "depth": self.depth,
            "actionability": self.actionability,
            "practicality": self.practicality,
            "overall": self.overall
        }


class QualityEvaluator:
    """AI 결과물 품질 평가 시스템"""
    
    def __init__(self):
        # 고품질 키워드 사전
        self.technical_depth_keywords = [
            "구체적으로", "단계별", "trade-off", "장단점", "최적화", 
            "아키텍처", "패턴", "전략", "방법론", "구현", "경험"
        ]
        
        self.actionable_keywords = [
            "프로젝트", "구축", "학습", "실습", "적용", "구현", 
            "연습", "경험", "실행", "진행", "개발"
        ]
        
        self.relevance_keywords = [
            "MSA", "마이크로서비스", "Spring Boot", "Python", "AWS", 
            "커머스", "결제", "주문", "배치", "처리"
        ]
    
    def evaluate_coaching_result(self, result: CoachingResult, resume_data: ResumePayload) -> QualityScore:
        """코칭 결과 전체 품질 평가"""
        
        # 면접 질문 평가
        questions_score = self._evaluate_interview_questions(result.interview_questions, resume_data)
        
        # 학습 경로 평가
        learning_path_score = self._evaluate_learning_path(result.learning_path, resume_data)
        
        # 가중 평균 (면접 질문 60%, 학습 경로 40%)
        overall_relevance = questions_score.relevance * 0.6 + learning_path_score.relevance * 0.4
        overall_depth = questions_score.depth * 0.6 + learning_path_score.depth * 0.4
        overall_actionability = questions_score.actionability * 0.6 + learning_path_score.actionability * 0.4
        overall_practicality = questions_score.practicality * 0.6 + learning_path_score.practicality * 0.4
        
        overall = (overall_relevance + overall_depth + overall_actionability + overall_practicality) / 4
        
        return QualityScore(
            relevance=overall_relevance,
            depth=overall_depth,
            actionability=overall_actionability,
            practicality=overall_practicality,
            overall=overall
        )
    
    def _evaluate_interview_questions(self, questions: List, resume_data: ResumePayload) -> QualityScore:
        """면접 질문 품질 평가"""
        
        scores = []
        for question in questions:
            question_text = question.question.lower()
            intent_text = question.intent.lower()
            
            # 관련성 평가
            relevance = self._calculate_relevance(question_text, resume_data)
            
            # 깊이 평가
            depth = self._calculate_depth(question_text, intent_text)
            
            # 실행가능성 평가 (면접 질문의 경우 답변 가능성)
            actionability = self._calculate_question_answerability(question_text)
            
            # 실용성 평가
            practicality = self._calculate_question_practicality(question_text, intent_text)
            
            question_score = QualityScore(
                relevance=relevance,
                depth=depth,
                actionability=actionability,
                practicality=practicality,
                overall=(relevance + depth + actionability + practicality) / 4
            )
            scores.append(question_score)
        
        # 평균 계산
        if not scores:
            return QualityScore(0, 0, 0, 0, 0)
        
        avg_relevance = sum(s.relevance for s in scores) / len(scores)
        avg_depth = sum(s.depth for s in scores) / len(scores)
        avg_actionability = sum(s.actionability for s in scores) / len(scores)
        avg_practicality = sum(s.practicality for s in scores) / len(scores)
        avg_overall = sum(s.overall for s in scores) / len(scores)
        
        return QualityScore(avg_relevance, avg_depth, avg_actionability, avg_practicality, avg_overall)
    
    def _evaluate_learning_path(self, learning_path, resume_data: ResumePayload) -> QualityScore:
        """학습 경로 품질 평가"""
        
        summary_text = learning_path.summary.lower()
        all_steps_text = " ".join([step.title + " " + step.description for step in learning_path.steps]).lower()
        
        # 관련성 평가
        relevance = self._calculate_relevance(summary_text + " " + all_steps_text, resume_data)
        
        # 깊이 평가
        depth = self._calculate_learning_depth(learning_path.steps)
        
        # 실행가능성 평가
        actionability = self._calculate_learning_actionability(learning_path.steps)
        
        # 실용성 평가
        practicality = self._calculate_learning_practicality(learning_path.steps)
        
        overall = (relevance + depth + actionability + practicality) / 4
        
        return QualityScore(relevance, depth, actionability, practicality, overall)
    
    def _calculate_relevance(self, text: str, resume_data: ResumePayload) -> float:
        """관련성 점수 계산 (1-5점)"""
        
        # 이력서 키워드 추출
        resume_keywords = []
        resume_keywords.extend(resume_data.career_summary.lower().split())
        resume_keywords.extend(resume_data.job_duties.lower().split())
        resume_keywords.extend([skill.lower() for skill in resume_data.technical_skills])
        
        # 키워드 매칭 점수
        matches = 0
        total_keywords = len(resume_keywords)
        
        for keyword in resume_keywords:
            if len(keyword) > 2 and keyword in text:  # 2글자 이상의 키워드만 체크
                matches += 1
        
        if total_keywords == 0:
            return 3.0
        
        match_ratio = matches / total_keywords
        
        # 점수 구간화
        if match_ratio >= 0.3:
            return 5.0
        elif match_ratio >= 0.2:
            return 4.0
        elif match_ratio >= 0.1:
            return 3.0
        elif match_ratio >= 0.05:
            return 2.0
        else:
            return 1.0
    
    def _calculate_depth(self, question_text: str, intent_text: str) -> float:
        """깊이 점수 계산 (1-5점)"""
        
        depth_indicators = 0
        
        # 기술적 깊이 키워드 체크
        for keyword in self.technical_depth_keywords:
            if keyword in question_text or keyword in intent_text:
                depth_indicators += 1
        
        # 질문의 복잡도 체크
        if len(question_text) > 100:  # 긴 질문은 보통 더 복합적
            depth_indicators += 1
        
        if "?" in question_text and question_text.count("?") == 1:  # 단일 명확한 질문
            depth_indicators += 1
        
        # 구체적인 상황/예시 언급
        if any(keyword in question_text for keyword in ["예시", "사례", "경험", "상황"]):
            depth_indicators += 2
        
        # 점수 변환
        if depth_indicators >= 5:
            return 5.0
        elif depth_indicators >= 4:
            return 4.0
        elif depth_indicators >= 3:
            return 3.0
        elif depth_indicators >= 2:
            return 2.0
        else:
            return 1.0
    
    def _calculate_question_answerability(self, question_text: str) -> float:
        """질문의 답변 가능성 평가 (1-5점)"""
        
        answerability_score = 3.0  # 기본 점수
        
        # 너무 추상적인 질문은 감점
        if any(word in question_text for word in ["일반적으로", "보통", "대부분"]):
            answerability_score -= 1.0
        
        # 구체적인 경험을 묻는 질문은 가점
        if any(word in question_text for word in ["경험", "사례", "프로젝트에서", "실제로"]):
            answerability_score += 1.0
        
        # 단계별/구체적 설명을 요구하는 질문은 가점
        if any(word in question_text for word in ["단계별", "구체적으로", "어떻게", "방법"]):
            answerability_score += 0.5
        
        return max(1.0, min(5.0, answerability_score))
    
    def _calculate_question_practicality(self, question_text: str, intent_text: str) -> float:
        """질문의 실용성 평가 (1-5점)"""
        
        practicality_score = 3.0  # 기본 점수
        
        # 실무 중심 질문은 가점
        if any(word in question_text for word in ["실무", "프로덕션", "운영", "실제"]):
            practicality_score += 1.0
        
        # 평가 의도가 명확한 경우 가점
        if any(word in intent_text for word in ["평가", "검증", "확인", "측정"]):
            practicality_score += 0.5
        
        # 너무 이론적인 질문은 감점
        if any(word in question_text for word in ["이론적으로", "개념적으로", "일반론"]):
            practicality_score -= 1.0
        
        return max(1.0, min(5.0, practicality_score))
    
    def _calculate_learning_depth(self, steps: List) -> float:
        """학습 경로 깊이 평가 (1-5점)"""
        
        if not steps:
            return 1.0
        
        depth_score = 0
        
        for step in steps:
            step_text = (step.title + " " + step.description).lower()
            
            # 구체적인 프로젝트 언급
            if any(word in step_text for word in ["프로젝트", "구축", "개발", "구현"]):
                depth_score += 1
            
            # 기술적 세부사항 언급
            if any(word in step_text for word in ["아키텍처", "패턴", "최적화", "설계"]):
                depth_score += 1
            
            # 단계별 구체성
            if len(step.description) > 50:  # 상세한 설명
                depth_score += 0.5
        
        # 정규화
        max_possible = len(steps) * 2.5
        normalized_score = (depth_score / max_possible) * 5 if max_possible > 0 else 3.0
        
        return max(1.0, min(5.0, normalized_score))
    
    def _calculate_learning_actionability(self, steps: List) -> float:
        """학습 경로 실행가능성 평가 (1-5점)"""
        
        if not steps:
            return 1.0
        
        actionability_score = 0
        
        for step in steps:
            step_text = (step.title + " " + step.description).lower()
            
            # 실행 가능한 동작 언급
            actionable_count = sum(1 for word in self.actionable_keywords if word in step_text)
            actionability_score += min(actionable_count, 3)  # 최대 3점
            
            # 구체적인 자료/리소스 제공
            if step.resources and len(step.resources) > 0:
                actionability_score += 1
        
        # 정규화
        max_possible = len(steps) * 4
        normalized_score = (actionability_score / max_possible) * 5 if max_possible > 0 else 3.0
        
        return max(1.0, min(5.0, normalized_score))
    
    def _calculate_learning_practicality(self, steps: List) -> float:
        """학습 경로 실용성 평가 (1-5점)"""
        
        if not steps:
            return 1.0
        
        practicality_score = 0
        
        for step in steps:
            step_text = (step.title + " " + step.description).lower()
            
            # 현실적인 제안
            if any(word in step_text for word in ["사이드 프로젝트", "토이 프로젝트", "연습", "실습"]):
                practicality_score += 1
            
            # 커리어 관련성
            if any(word in step_text for word in ["승진", "이직", "성장", "역량", "스킬"]):
                practicality_score += 1
            
            # 구체적인 기술/도구 언급
            if any(word in step_text for word in ["kubernetes", "docker", "aws", "spring", "python"]):
                practicality_score += 0.5
        
        # 정규화
        max_possible = len(steps) * 2.5
        normalized_score = (practicality_score / max_possible) * 5 if max_possible > 0 else 3.0
        
        return max(1.0, min(5.0, normalized_score))
    
    def generate_improvement_suggestions(self, score: QualityScore) -> List[str]:
        """품질 점수를 바탕으로 개선 제안 생성"""
        
        suggestions = []
        
        if score.relevance < 3.0:
            suggestions.append("이력서의 구체적인 기술 스택과 프로젝트 경험을 더 직접적으로 언급하세요.")
        
        if score.depth < 3.0:
            suggestions.append("질문과 학습 단계를 더 구체적이고 심층적으로 만드세요.")
        
        if score.actionability < 3.0:
            suggestions.append("더 실행 가능하고 구체적인 액션 아이템을 제공하세요.")
        
        if score.practicality < 3.0:
            suggestions.append("실무와 더 밀접한 관련이 있는 내용으로 구성하세요.")
        
        if score.overall >= 4.0:
            suggestions.append("✅ 우수한 품질의 결과물입니다!")
        
        return suggestions


def get_quality_evaluator() -> QualityEvaluator:
    """품질 평가자 인스턴스 반환"""
    return QualityEvaluator()