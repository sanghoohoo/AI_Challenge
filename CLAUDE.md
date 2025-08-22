# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Challenge project for developing a personalized career coaching chatbot API. The goal is to create a backend API that generates customized interview questions and learning paths based on a user's resume information using generative AI.

## Key Requirements

**Core Functionality:**
- Accept resume information (career summary, job duties, technical skills) via API
- Generate 5 personalized interview questions using LLM
- Provide customized learning path recommendations
- Return structured JSON responses (not raw text)

**Technical Constraints:**
- Backend API development only (no file parsing required)
- Text input for resume data instead of file upload
- Focus on prompt engineering and API design quality

## Architecture Guidelines

**Recommended Tech Stack:**
- **FastAPI + Python** - Optimal for I/O-intensive LLM API calls with native async support
- **Direct LLM SDK integration** - Use official Python SDKs (e.g., OpenAI) rather than frameworks like LangChain for this focused use case
- **Stateless design** - No database required, focus on clean API contracts

**Project Structure:**
```
/app
├── main.py                 # FastAPI app instance
├── api/endpoints/          # API route handlers
├── core/config.py          # Environment variables
├── schemas/                # Pydantic models for requests/responses
├── services/
│   ├── llm_client.py       # LLM API integration with retry logic
│   └── prompt_builder.py   # Prompt engineering logic
└── tests/                  # Test suite
```

## API Design

**Primary Endpoint:** `POST /coaching-sessions`

**Request Format:**
```json
{
  "career_summary": "3년차 백엔드 개발자, Spring Boot/MSA/Python 기반 커머스 서비스 개발",
  "job_duties": "주문 및 결제 시스템 MSA 전환 프로젝트 리딩",
  "technical_skills": ["Spring Boot", "Python", "AWS", "MSA"]
}
```

**Response Format:**
```json
{
  "sessionId": "uuid",
  "interview_questions": [
    {
      "question": "구체적인 면접 질문",
      "intent": "이 질문의 평가 목적",
      "category": "Technical Deep-Dive"
    }
  ],
  "learning_path": {
    "summary": "학습 경로 요약",
    "steps": [
      {
        "title": "학습 단계 제목",
        "description": "구체적인 실행 방안",
        "resources": ["검색 키워드"]
      }
    ]
  }
}
```

## Prompt Engineering Strategy

**Core Techniques:**
- **Persona-based prompting** - Assign specific expert roles (e.g., "Silicon Valley senior engineer interviewer")
- **Few-shot examples** - Include 2-3 high-quality examples in prompts
- **Chain-of-thought** - Force step-by-step analysis before generating final questions
- **Defensive prompting** - Protect against prompt injection attacks

**Quality Requirements:**
- Questions must be specific to the user's experience, not generic
- Learning paths must be actionable and concrete
- Responses should demonstrate deep technical understanding

## Development Commands

Since this is a new project, common commands will be:

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Run tests
pytest

# Check code quality
black .
flake8 .
```

## Security Considerations

- Store LLM API keys in environment variables, never in code
- Implement input sanitization to prevent prompt injection
- Use HTTPS for all communications
- Include rate limiting for production deployment

## Evaluation Criteria Focus

The project will be evaluated on:
1. **AI Integration Creativity** - Sophisticated prompt engineering strategies
2. **Backend Architecture** - Clean, scalable API design
3. **Practical Utility** - How useful the generated content is for real job seekers

## Development Progress Tracking

**Progress Status:** Check `development_plan.md` for current development phase and completed tasks.

**Development Phases:**
- Phase 1: 기반 구축 (1-2일) - Project setup and basic structure
- Phase 2: 핵심 로직 개발 (2-3일) - Core logic implementation
- Phase 3: 프롬프트 최적화 (2-3일) - Prompt engineering optimization
- Phase 4: 테스트 및 문서화 (1-2일) - Testing and documentation
- Phase 5: 최종 제출 준비 (1일) - Final submission preparation

**Current Development Status:** 
To check current progress, refer to the checklist items in `development_plan.md`. Each phase contains specific tasks with checkboxes to track completion status.

**Key Milestones:**
- [ ] FastAPI project structure setup
- [ ] LLM client implementation with retry logic
- [ ] Prompt engineering system (PCT framework + Few-shot + CoT)
- [ ] API endpoint implementation
- [ ] Test suite completion
- [ ] Final submission package ready

## File Context

- `competition_rules.txt` - Original challenge requirements and submission guidelines
- `gemini_responce.txt` - Comprehensive strategy document with detailed implementation guidance including FastAPI architecture decisions, multi-layer prompting techniques, and evaluation optimization strategies
- `development_plan.md` - Korean development plan with 5-phase roadmap, technical specifications, and progress tracking checklists