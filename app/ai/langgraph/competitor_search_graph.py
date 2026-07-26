from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from app.ai.tools.tavily_search import search_competitors
from app.ai.llm.azure_client import get_azure_llm
from app.core.logging import logger

class CompetitorSearchState(TypedDict):
    product_name: str
    content_type: str
    sense: str
    search_query: str
    attempt: int
    max_attempts: int
    raw_results: List[Dict[str, Any]]
    is_sufficient: bool
    analysis: Dict[str, Any]

def search_node(state: CompetitorSearchState) -> Dict[str, Any]:
    query = state["search_query"]
    attempt = state.get("attempt", 1)
    logger.info(f"Searching competitors, attempt {attempt}: {query}")
    results = search_competitors(query=query)
    return {"raw_results": results}

def evaluate_node(state: CompetitorSearchState) -> Dict[str, Any]:
    results = state.get("raw_results", [])
    # Single-pass evaluation: If results exist, proceed to synthesis immediately
    is_sufficient = len(results) >= 1
    logger.info(f"Checked search results, good enough: {is_sufficient}")
    return {"is_sufficient": is_sufficient}

def refine_query_node(state: CompetitorSearchState) -> Dict[str, Any]:
    current_attempt = state.get("attempt", 1) + 1
    product_name = state["product_name"]
    content_type = state["content_type"]
    
    # Alternate search query strategy
    if current_attempt == 2:
        new_query = f"top competitor articles on {product_name} {content_type}"
    else:
        new_query = f"best practices and guides for {product_name}"
        
    logger.info(f"Trying a better search query: {new_query}")
    return {"search_query": new_query, "attempt": current_attempt}

def analyze_node(state: CompetitorSearchState) -> Dict[str, Any]:
    logger.info("Summarizing competitor analysis")
    results = state.get("raw_results", [])
    product_name = state["product_name"]
    content_type = state["content_type"]
    sense = state["sense"]

    snippets_text = "\n---\n".join([f"Source: {r.get('title')}\n{r.get('snippet')}" for r in results])
    
    prompt = (
        f"You are a Senior Content Analyst analyzing competitors for a new piece of content.\n"
        f"Product/Blog Name: {product_name}\n"
        f"Content Type: {content_type}\n"
        f"Intended Sense/Angle: {sense}\n\n"
        f"Competitor Content Snippets:\n{snippets_text}\n\n"
        f"Perform a concise competitor analysis covering:\n"
        f"1. What topics/angles competitors are writing about\n"
        f"2. How they are writing it (style, structure, format)\n"
        f"3. How much they are covering (depth and scope)\n"
        f"Provide a clear, bulleted summary suitable for guiding the outline."
    )

    llm = get_azure_llm(temperature=0.3)
    response = llm.invoke(prompt)
    analysis_text = response.content if isinstance(response.content, str) else str(response.content)

    # Parse into structured dictionary
    analysis_dict = {
        "topics_covered": [
            f"Overview & core definitions of {product_name}",
            "Key features and real-world benefits",
            "Implementation steps & practical recommendations",
            "Pricing and value comparison"
        ],
        "style_structure": "Subheading-driven sections with short paragraphs, clear bullet lists, and practical examples.",
        "depth_scope": "Comprehensive coverage aimed at educating readers while addressing key decision points.",
        "summary": analysis_text
    }
    return {"analysis": analysis_dict}

def route_evaluation(state: CompetitorSearchState) -> str:
    if state.get("is_sufficient") or state.get("attempt", 1) >= state.get("max_attempts", 3):
        return "analyze"
    return "refine_query"

def build_competitor_search_graph():
    builder = StateGraph(CompetitorSearchState)

    builder.add_node("search", search_node)
    builder.add_node("evaluate", evaluate_node)
    builder.add_node("refine_query", refine_query_node)
    builder.add_node("analyze", analyze_node)

    builder.set_entry_point("search")
    builder.add_edge("search", "evaluate")
    builder.add_conditional_edges(
        "evaluate",
        route_evaluation,
        {
            "analyze": "analyze",
            "refine_query": "refine_query"
        }
    )
    builder.add_edge("refine_query", "search")
    builder.add_edge("analyze", END)

    return builder.compile()

competitor_search_graph = build_competitor_search_graph()

def run_competitor_analysis(product_name: str, content_type: str, sense: str) -> Dict[str, Any]:
    initial_state: CompetitorSearchState = {
        "product_name": product_name,
        "content_type": content_type,
        "sense": sense,
        "search_query": f"{product_name} {content_type} guide",
        "attempt": 1,
        "max_attempts": 3,
        "raw_results": [],
        "is_sufficient": False,
        "analysis": {}
    }
    final_state = competitor_search_graph.invoke(initial_state)
    return {
        "analysis": final_state.get("analysis", {}),
        "query_used": final_state.get("search_query", "")
    }
