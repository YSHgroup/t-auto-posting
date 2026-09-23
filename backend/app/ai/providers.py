"""
AI provider abstractions (OpenAI and Claude)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base for AI providers"""
    
    @abstractmethod
    async def analyze_group(self, group_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze group information"""
        pass
    
    @abstractmethod
    async def recommend_post(self, group_analysis: Dict, available_posts: list) -> Optional[Dict]:
        """Recommend best post for a group"""
        pass
    
    @abstractmethod
    async def analyze_messages_for_opportunities(self, messages: list) -> Optional[list]:
        """Analyze messages to find investor/partnership opportunities"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI ChatGPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            logger.error("OpenAI library not installed")
            self.client = None
        
        self.model = model
        self.api_key = api_key
    
    async def analyze_group(self, group_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze group for posting suitability"""
        if not self.client:
            return None
        
        prompt = self._build_group_analysis_prompt(group_info)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing Telegram groups and recommending posting strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return None
    
    async def recommend_post(self, group_analysis: Dict, available_posts: list) -> Optional[Dict]:
        """Recommend best post for group"""
        if not self.client:
            return None
        
        prompt = self._build_recommendation_prompt(group_analysis, available_posts)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at matching posts to Telegram groups."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"OpenAI recommendation error: {e}")
            return None
    
    async def analyze_messages_for_opportunities(self, messages: list) -> Optional[list]:
        """Find investor/partner opportunities in messages"""
        if not self.client:
            return None
        
        prompt = self._build_opportunity_prompt(messages)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying investment and partnership opportunities from conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            return result.get("opportunities", [])
        except Exception as e:
            logger.error(f"OpenAI opportunity analysis error: {e}")
            return None
    
    def _build_group_analysis_prompt(self, group_info: Dict) -> str:
        return f"""
Analyze this Telegram group and provide detailed assessment.

Group Information:
- Name: {group_info.get('name')}
- Members: {group_info.get('member_count')}
- Description: {group_info.get('description')}
- Recent messages: {group_info.get('messages_text')}

Provide a JSON response with:
{{
  "group_types": ["developer", "business", ...],
  "partnership_suitability": "Suitable|Possibly Suitable|Not Recommended",
  "partnership_reason": "...",
  "job_suitability": "Suitable|Possibly Suitable|Not Recommended",
  "job_reason": "...",
  "posting_style": ["professional", "casual", ...],
  "risks": ["spam", "aggressive", ...],
  "communication_style": ["formal", "technical", ...],
  "confidence_score": 85
}}
"""
    
    def _build_recommendation_prompt(self, group_analysis: Dict, posts: list) -> str:
        return f"""
Given this group analysis and available posts, recommend the best post.

Group Analysis:
{json.dumps(group_analysis, indent=2)}

Available Posts:
{json.dumps([{"id": p.get("id"), "title": p.get("title"), "content": p.get("content"), "type": p.get("type")} for p in posts], indent=2)}

Provide JSON response:
{{
  "recommended_post_id": 1,
  "reason": "...",
  "compatibility_score": 85,
  "alternatives": [2, 3]
}}
"""
    
    def _build_opportunity_prompt(self, messages: list) -> str:
        return f"""
Analyze these chat messages to identify investment and partnership opportunities.

Messages:
{json.dumps(messages[:20], indent=2)}

Provide JSON response:
{{
  "opportunities": [
    {{
      "user_id": "...",
      "type": "Investment|Partnership",
      "evidence": "...",
      "confidence": "High|Medium|Low",
      "reason": "..."
    }}
  ]
}}
"""


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            logger.error("Anthropic library not installed")
            self.client = None
        
        self.model = model
        self.api_key = api_key
    
    async def analyze_group(self, group_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze group for posting suitability"""
        if not self.client:
            return None
        
        prompt = self._build_group_analysis_prompt(group_info)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return None
    
    async def recommend_post(self, group_analysis: Dict, available_posts: list) -> Optional[Dict]:
        """Recommend best post for group"""
        if not self.client:
            return None
        
        prompt = self._build_recommendation_prompt(group_analysis, available_posts)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"Claude recommendation error: {e}")
            return None
    
    async def analyze_messages_for_opportunities(self, messages: list) -> Optional[list]:
        """Find investor/partner opportunities in messages"""
        if not self.client:
            return None
        
        prompt = self._build_opportunity_prompt(messages)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            result = json.loads(response_text)
            return result.get("opportunities", [])
        except Exception as e:
            logger.error(f"Claude opportunity analysis error: {e}")
            return None
    
    def _build_group_analysis_prompt(self, group_info: Dict) -> str:
        return f"""
Analyze this Telegram group and provide detailed assessment.

Group Information:
- Name: {group_info.get('name')}
- Members: {group_info.get('member_count')}
- Description: {group_info.get('description')}
- Recent messages: {group_info.get('messages_text')}

Provide a JSON response with:
{{
  "group_types": ["developer", "business", ...],
  "partnership_suitability": "Suitable|Possibly Suitable|Not Recommended",
  "partnership_reason": "...",
  "job_suitability": "Suitable|Possibly Suitable|Not Recommended",
  "job_reason": "...",
  "posting_style": ["professional", "casual", ...],
  "risks": ["spam", "aggressive", ...],
  "communication_style": ["formal", "technical", ...],
  "confidence_score": 85
}}
"""
    
    def _build_recommendation_prompt(self, group_analysis: Dict, posts: list) -> str:
        return f"""
Given this group analysis and available posts, recommend the best post.

Group Analysis:
{json.dumps(group_analysis, indent=2)}

Available Posts:
{json.dumps([{"id": p.get("id"), "title": p.get("title"), "content": p.get("content"), "type": p.get("type")} for p in posts], indent=2)}

Provide JSON response:
{{
  "recommended_post_id": 1,
  "reason": "...",
  "compatibility_score": 85,
  "alternatives": [2, 3]
}}
"""
    
    def _build_opportunity_prompt(self, messages: list) -> str:
        return f"""
Analyze these chat messages to identify investment and partnership opportunities.

Messages:
{json.dumps(messages[:20], indent=2)}

Provide JSON response:
{{
  "opportunities": [
    {{
      "user_id": "...",
      "type": "Investment|Partnership",
      "evidence": "...",
      "confidence": "High|Medium|Low",
      "reason": "..."
    }}
  ]
}}
"""


def get_ai_provider(provider_type: str, api_key: str) -> Optional[AIProvider]:
    """Factory function to get AI provider"""
    if provider_type.lower() == "openai":
        return OpenAIProvider(api_key)
    elif provider_type.lower() == "claude":
        return ClaudeProvider(api_key)
    else:
        logger.error(f"Unknown AI provider: {provider_type}")
        return None
