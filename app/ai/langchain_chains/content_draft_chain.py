from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm.azure_client import get_azure_llm
from app.ai.prompts.content_prompts import CONTENT_DRAFT_SYSTEM_PROMPT, CONTENT_DRAFT_USER_PROMPT
from app.core.logging import logger

def run_content_draft_chain(
    language: str,
    region: str,
    content_type: str,
    product_name: str,
    target_audience: str,
    tone: str,
    sense: str,
    word_count: int,
    confirmed_outline: str,
    competitor_summary: str
) -> str:
    logger.info("Writing first draft")
    prompt = ChatPromptTemplate.from_messages([
        ("system", CONTENT_DRAFT_SYSTEM_PROMPT),
        ("user", CONTENT_DRAFT_USER_PROMPT)
    ])
    llm = get_azure_llm(temperature=0.7)
    chain = prompt | llm

    response = chain.invoke({
        "language": language,
        "region": region,
        "content_type": content_type,
        "product_name": product_name,
        "target_audience": target_audience,
        "tone": tone,
        "sense": sense,
        "word_count": word_count,
        "confirmed_outline": confirmed_outline,
        "competitor_summary": competitor_summary or "Standard industry baseline"
    })

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content.strip()
