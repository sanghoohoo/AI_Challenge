# AI Career Coach API

이력서 기반 개인 맞춤형 커리어 코치 챗봇 API

## 📋 프로젝트 개요

구직자의 이력서 정보(경력, 직무, 기술 스킬)를 기반으로 생성형 AI가 맞춤형 면접 모의질문을 생성하고, 자기 개발 학습 경로를 제안하여 구직자의 합격률을 높이는 데 도움을 주는 백엔드 챗봇 API입니다.

## 🏗️ 기술 스택

- **Backend**: FastAPI (Python)
- **AI Integration**: OpenAI GPT API
- **Data Validation**: Pydantic
- **Documentation**: Swagger UI (자동 생성)

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

## 🎯 주요 기능

- ✅ **개인 맞춤형 면접 질문 생성**: 5개의 심층적인 질문
- ✅ **학습 경로 추천**: 구체적이고 실행 가능한 단계별 가이드
- ✅ **구조화된 응답**: JSON 형태의 체계적인 데이터 구조
- ✅ **자동 API 문서**: Swagger UI를 통한 대화형 문서

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

### 🚧 Phase 2: 핵심 로직 개발 (진행 중)
- LLM 클라이언트 모듈 구현
- 프롬프트 엔지니어링 로직 개발
- 비즈니스 로직 통합

### ⏳ 다음 단계
- 프롬프트 최적화
- 테스트 및 문서화
- 최종 제출 준비

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