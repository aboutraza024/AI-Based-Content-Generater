from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm.azure_client import get_azure_llm
from app.ai.prompts.outline_prompts import OUTLINE_SYSTEM_PROMPT, OUTLINE_USER_PROMPT
from app.core.logging import logger

def run_outline_chain(
    language: str,
    region: str,
    content_type: str,
    product_name: str,
    target_audience: str,
    tone: str,
    sense: str,
    word_count: int,
    competitor_summary: str
) -> str:
    logger.info(f"Writing outline for audience: {target_audience}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", OUTLINE_SYSTEM_PROMPT),
        ("user", OUTLINE_USER_PROMPT)
    ])
    llm = get_azure_llm(temperature=0.4)
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
        "competitor_summary": competitor_summary
    })

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content.strip()
