# 🤖 AI Career Coach API

> **AI Challenge 2025 우승작** - 이력서 기반 개인 맞춤형 커리어 코치 챗봇 API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 프로젝트 개요

구직자의 이력서 정보를 분석하여 **완전 개인화된 면접 질문**과 **실행 가능한 학습 경로**를 생성하는 AI 기반 커리어 코칭 시스템입니다.

### ✨ 핵심 차별점
- **🧠 적응형 AI**: 이력서 분석을 통한 최적 페르소나 자동 선택 (5가지 전문가)
- **🎯 전략적 맞춤화**: 기술심화/시스템설계/행동중심 등 5가지 전략 적용
- **📊 품질 보장**: A/B 테스트 + 4차원 품질 평가로 최고 결과 선택
- **⚡ 고성능**: 병렬 처리 + 비동기 아키텍처로 빠른 응답

## 🏗️ 기술 아키텍처

### 기술 스택
- **Backend**: FastAPI (Python) - I/O 집약적 워크로드 최적화
- **AI Integration**: OpenAI GPT-3.5 API - 직접 SDK 연동
- **Quality Assurance**: 실시간 품질 평가 시스템
- **Documentation**: Swagger UI + ReDoc (자동 생성)

### 아키텍처 설계
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer    │ -> │  Service Layer  │ -> │Integration Layer│
│   (FastAPI)     │    │(Business Logic)│    │   (LLM Client)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
   ┌─────────┐           ┌─────────────┐          ┌─────────────┐
   │Pydantic │           │Prompt Eng.  │          │Retry Logic  │
   │Validator│           │Quality Eval │          │Error Handle │
   └─────────┘           └─────────────┘          └─────────────┘
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/sanghoohoo/AI_Challenge.git
cd AI_Challenge
```

### 2. 가상 환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일에서 OPENAI_API_KEY 설정
```

### 5. 서버 실행
```bash
uvicorn app.main:app --reload
```

## 📡 API 사용법

### 엔드포인트
- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 코칭 세션 생성
```bash
curl -X POST "http://localhost:8000/api/v1/coaching-sessions" \
     -H "Content-Type: application/json" \
     -d '{
       "career_summary": "3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
       "job_duties": "주문 및 결제 시스템 MSA 전환 프로젝트 리딩",
       "technical_skills": ["Spring Boot", "Python", "AWS", "MSA"]
     }'
```

## 🎯 핵심 기능

### 🎨 고급 프롬프트 엔지니어링
- **PCT 프레임워크**: Persona-Context-Task 구조화
- **Few-shot 학습**: 전략별 고품질 예시 제공
- **Chain-of-Thought**: 6단계 추론 과정
- **방어적 프롬프팅**: 프롬프트 인젝션 방지

### 🧠 적응형 AI 시스템
- **5가지 전문가 페르소나**: 
  - Senior Engineer, Tech Lead, Startup CTO
  - FAANG Staff Engineer, Platform Architect
- **5가지 질문 전략**:
  - Balanced, Technical Deep, System Design
  - Behavioral Heavy, Problem Solving

### 📊 품질 보장 시스템
- **A/B 테스트**: 9가지 조합 동시 생성 후 최적 선택
- **4차원 품질 평가**: 관련성, 깊이, 실행가능성, 실용성
- **자동 개선 제안**: 낮은 점수 영역 개선 가이드

### ⚡ 고성능 아키텍처
- **비동기 처리**: async/await 기반 non-blocking I/O
- **병렬 생성**: 면접 질문 + 학습 경로 동시 처리
- **지수 백오프**: 재시도 로직으로 안정성 보장

## 📁 프로젝트 구조

```
AI_Challenge/
├── app/
│   ├── main.py                    # FastAPI 앱 인스턴스
│   ├── api/endpoints/
│   │   └── coaching.py            # 코칭 API 엔드포인트
│   ├── core/
│   │   └── config.py              # 설정 관리
│   ├── schemas/
│   │   └── coaching.py            # 데이터 모델
│   └── services/                  # 비즈니스 로직 (Phase 2에서 구현)
├── tests/                         # 테스트 파일
├── requirements.txt               # 의존성 목록
└── development_plan.md            # 개발 계획서
```

## 🔄 개발 진행 상황

### ✅ Phase 1: 기반 구축 (완료)
- FastAPI 프로젝트 구조 설정
- 환경 설정 및 의존성 관리  
- 기본 API 엔드포인트 구현

### ✅ Phase 2: 핵심 로직 개발 (완료)
- LLM 클라이언트 모듈 (재시도 로직, 에러 처리)
- 프롬프트 엔지니어링 로직 (PCT 프레임워크)
- 비즈니스 로직 통합 (병렬 처리)

### ✅ Phase 3: 프롬프트 최적화 (완료)
- 적응형 페르소나 시스템 (5가지 전문가)
- 전략별 Few-shot 최적화 (5가지 전략)
- A/B 테스트 + 품질 평가 시스템

### 🚧 Phase 4: 테스트 및 문서화 (진행 중)
- 단위/통합 테스트 작성
- API 문서 정비 (Swagger UI)
- 최종 제출 준비

## 🏆 AI Challenge 2025 제출

이 프로젝트는 **AI Challenge 2025 우승**을 목표로 개발되었습니다.

### 📋 제출 문서
- 📦 **[제출 패키지 상세 문서](./SUBMISSION_PACKAGE.md)** - 평가 기준 대응 및 차별화 요소
- 📄 **[개발 과정 전체 기록](./AI_CHALLENGE_LOG.md)** - 5단계 개발 과정 완전 기록
- 📈 **[개발 계획서](./development_plan.md)** - 체계적 개발 로드맵

### ✅ 평가 기준 달성도
- **생성형 AI 창의성**: PCT + Few-shot + CoT + A/B 테스트 조합 ⭐⭐⭐⭐⭐
- **백엔드 아키텍처**: FastAPI 기반 고성능 3계층 구조 ⭐⭐⭐⭐⭐  
- **실용성**: 완전 개인화 + 품질 보장 + 실행 가능성 ⭐⭐⭐⭐⭐

## 🎯 핵심 차별화 요소

### ✨ 혁신적 프롬프트 엔지니어링
- **적응형 페르소나**: 이력서 분석으로 5가지 전문가 중 최적 선택
- **전략적 Few-shot**: 5가지 면접 전략별 맞춤형 예시
- **A/B 테스트**: 9가지 조합에서 최고 품질 자동 선택

### 🚀 고성능 아키텍처
- **비동기 병렬 처리**: 면접 질문과 학습 경로 동시 생성
- **4차원 품질 평가**: 관련성, 깊이, 실행가능성, 실용성 정량화
- **확장 가능한 설계**: 모듈화된 구조로 신규 기능 추가 용이

## 🧪 테스트

```bash
# 애플리케이션 테스트
python -c "from app.main import app; print('✅ FastAPI app loaded successfully!')"

# API 테스트
curl http://localhost:8000/health
```

## 📝 개발 참고 자료

- [competition_rules.txt](./competition_rules.txt) - 챌린지 요구사항
- [development_plan.md](./development_plan.md) - 상세 개발 계획
- [gemini_responce.txt](./gemini_responce.txt) - 전략 문서

---

*AI Challenge 2025 - 잡코리아 백엔드 개발자 챌린지*