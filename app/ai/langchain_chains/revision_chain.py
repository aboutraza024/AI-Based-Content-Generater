from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm.azure_client import get_azure_llm
from app.ai.prompts.revision_prompts import REVISION_SYSTEM_PROMPT, REVISION_USER_PROMPT
from app.core.logging import logger

def run_revision_chain(
    language: str,
    region: str,
    content_type: str,
    product_name: str,
    target_audience: str,
    confirmed_outline: str,
    previous_content: str,
    revision_feedback: str
) -> str:
    logger.info("Executing revision chain...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", REVISION_SYSTEM_PROMPT),
        ("user", REVISION_USER_PROMPT)
    ])
    llm = get_azure_llm(temperature=0.6)
    chain = prompt | llm

    response = chain.invoke({
        "language": language,
        "region": region,
        "content_type": content_type,
        "product_name": product_name,
        "target_audience": target_audience,
        "confirmed_outline": confirmed_outline,
        "previous_content": previous_content,
        "revision_feedback": revision_feedback
    })

    content = response.content if isinstance(response.content, str) else str(response.content)
    return content.strip()
