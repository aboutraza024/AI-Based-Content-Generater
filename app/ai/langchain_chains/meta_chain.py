from typing import Tuple, List
import re
from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm.azure_client import get_azure_llm
from app.ai.prompts.meta_prompts import META_SYSTEM_PROMPT, META_USER_PROMPT
from app.core.logging import logger

def run_meta_chain(
    language: str,
    region: str,
    content_type: str,
    product_name: str,
    final_content: str
) -> Tuple[str, List[str]]:
    logger.info("Writing meta description and tags")
    prompt = ChatPromptTemplate.from_messages([
        ("system", META_SYSTEM_PROMPT),
        ("user", META_USER_PROMPT)
    ])
    llm = get_azure_llm(temperature=0.3)
    chain = prompt | llm

    response = chain.invoke({
        "language": language,
        "region": region,
        "content_type": content_type,
        "product_name": product_name,
        "final_content": final_content[:1500]  # First 1500 chars for context
    })

    raw_output = response.content if isinstance(response.content, str) else str(response.content)

    meta_desc = f"Discover everything about {product_name} in this comprehensive humanized guide."
    meta_tags = [product_name.lower(), content_type, "guide", "overview", "insights"]

    desc_match = re.search(r"META_DESCRIPTION:\s*(.*)", raw_output, re.IGNORECASE)
    if desc_match:
        meta_desc = desc_match.group(1).strip()

    tags_match = re.search(r"META_TAGS:\s*(.*)", raw_output, re.IGNORECASE)
    if tags_match:
        tags_str = tags_match.group(1).strip()
        parsed_tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        if parsed_tags:
            meta_tags = parsed_tags

    return meta_desc, meta_tags
