from typing import Optional, List, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_openai import AzureChatOpenAI
from app.core.config import settings
from app.core.logging import logger

class MockAzureChatOpenAI(BaseChatModel):
    """Stand-in AI used for local testing when no Azure key is set."""
    model_name: str = "mock-gpt-4o"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> ChatResult:
        prompt_text = " ".join([m.content for m in messages if isinstance(m.content, str)])
        
        # Smart responses based on prompt keywords
        if "competitor" in prompt_text.lower() and "analysis" in prompt_text.lower():
            response_content = (
                "Competitor Analysis:\n"
                "- Top topics: Feature comparisons, user benefits, pricing structure, setup guides.\n"
                "- Style & structure: Action-oriented section headers with concise bullet points.\n"
                "- Depth & scope: Covers overview, core features, implementation steps, and FAQs."
            )
        elif "outline" in prompt_text.lower():
            response_content = (
                "# Outline: Master Content Guide\n\n"
                "## 1. Introduction\n"
                "- Purpose & core value proposition\n"
                "- Target audience overview\n\n"
                "## 2. Core Features & Key Benefits\n"
                "- Primary features explained in detail\n"
                "- How this solves key pain points\n\n"
                "## 3. Practical Implementation & Best Practices\n"
                "- Step-by-step walkthrough\n"
                "- Insider tips for maximum results\n\n"
                "## 4. Frequently Asked Questions\n"
                "- Common user inquiries\n"
                "- Clarifying edge cases\n\n"
                "## 5. Conclusion & Actionable Next Steps\n"
                "- Final takeaway summary\n"
                "- Call to action"
            )
        elif "meta description" in prompt_text.lower() or "meta tags" in prompt_text.lower():
            response_content = (
                "META_DESCRIPTION: Learn everything about this solution with our comprehensive, step-by-step human guide.\n"
                "META_TAGS: guide, overview, step-by-step, ultimate guide, best practices, features"
            )
        elif "humanize" in prompt_text.lower() or "rewrite" in prompt_text.lower():
            # Generate clean, simple humanized text without buzzwords
            response_content = (
                "When you look at modern content writing tools, speed and clarity matter most. "
                "This guide walks you through every detail step by step. You get actionable insights "
                "without fluffy jargon or overly complex phrasing. "
                "Each section gives direct answers so you can make informed decisions quickly."
            )
        else:
            response_content = (
                "Here is the generated content tailored to your request. "
                "It covers every requested section in clear, direct language with smooth transitions."
            )

        generation = ChatGeneration(message=AIMessage(content=response_content))
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "mock_azure_chat_openai"

def get_azure_llm(temperature: float = 0.7) -> BaseChatModel:
    """
    Returns configured AzureChatOpenAI instance if credentials exist,
    otherwise returns MockAzureChatOpenAI fallback.
    """
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        try:
            logger.info("Initializing AzureChatOpenAI client...")
            return AzureChatOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                temperature=temperature
            )
        except Exception as e:
            logger.warning(f"Failed to initialize AzureChatOpenAI: {e}. Falling back to Mock client.")
            return MockAzureChatOpenAI()
    else:
        logger.info("No Azure OpenAI API key found in environment. Using Mock LLM model.")
        return MockAzureChatOpenAI()
