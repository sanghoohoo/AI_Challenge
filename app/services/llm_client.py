import asyncio
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """LLM 클라이언트 관련 오류"""
    pass


class LLMClient:
    """OpenAI API와의 비동기 통신을 담당하는 클라이언트"""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise LLMClientError("OpenAI API key가 설정되지 않았습니다.")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.max_retries = 3
        self.base_delay = 1.0  # 초기 재시도 지연 시간 (초)
    
    async def _retry_with_exponential_backoff(
        self, 
        func, 
        *args, 
        **kwargs
    ) -> Any:
        """지수 백오프를 사용한 재시도 메커니즘"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                # 재시도 가능한 오류인지 확인
                if not self._is_retryable_error(e):
                    raise e
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"LLM API 호출 실패 (시도 {attempt + 1}/{self.max_retries}). "
                        f"{delay}초 후 재시도합니다. 오류: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"모든 재시도 실패. 최종 오류: {str(e)}")
        
        raise LLMClientError(f"최대 재시도 횟수 초과: {str(last_exception)}")
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """재시도 가능한 오류인지 판단"""
        error_str = str(error).lower()
        
        # 재시도 가능한 오류들
        retryable_errors = [
            "rate limit",
            "timeout",
            "connection",
            "service unavailable",
            "internal server error",
            "bad gateway",
            "gateway timeout"
        ]
        
        return any(err in error_str for err in retryable_errors)
    
    async def generate_completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        프롬프트를 기반으로 텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            model: 사용할 모델명
            temperature: 창의성 수준 (0.0-2.0)
            max_tokens: 최대 토큰 수
            response_format: 응답 형식 (JSON 등)
        
        Returns:
            생성된 텍스트
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
                
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self._retry_with_exponential_backoff(
                self.client.chat.completions.create,
                **kwargs
            )
            
            content = response.choices[0].message.content
            if not content:
                raise LLMClientError("LLM이 빈 응답을 반환했습니다.")
            
            logger.info(f"LLM 응답 생성 완료. 토큰 사용량: {response.usage}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"LLM completion 생성 실패: {str(e)}")
            raise LLMClientError(f"텍스트 생성 중 오류 발생: {str(e)}")
    
    async def generate_json_completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo-1106",  # JSON 모드 지원 모델
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        JSON 형식으로 응답을 요청하는 completion 생성
        
        Args:
            prompt: JSON 형식 응답을 요청하는 프롬프트
            model: JSON 모드를 지원하는 모델명
            temperature: 창의성 수준
            max_tokens: 최대 토큰 수
        
        Returns:
            JSON 형식의 문자열
        """
        # JSON 응답을 명시적으로 요청하는 프롬프트 수정
        json_prompt = f"""{prompt}

중요: 반드시 유효한 JSON 형식으로만 응답해야 합니다. 다른 설명이나 텍스트는 포함하지 마세요."""
        
        return await self.generate_completion(
            prompt=json_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
    
    async def health_check(self) -> bool:
        """LLM 서비스 상태 확인"""
        try:
            test_response = await self.generate_completion(
                prompt="테스트 메시지입니다. '정상'이라고 답해주세요.",
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=10
            )
            
            return "정상" in test_response
            
        except Exception as e:
            logger.error(f"LLM 헬스체크 실패: {str(e)}")
            return False


# 전역 LLM 클라이언트 인스턴스
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """LLM 클라이언트 싱글톤 인스턴스 반환"""
    global _llm_client
    
    if _llm_client is None:
        _llm_client = LLMClient()
    
    return _llm_client