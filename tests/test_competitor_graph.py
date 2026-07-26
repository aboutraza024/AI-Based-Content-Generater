import pytest
from app.ai.langgraph.competitor_search_graph import run_competitor_analysis
from app.ai.tools.tavily_search import search_competitors

def test_tavily_search_live():
    results = search_competitors("AI content generator tools", max_results=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]
    assert "snippet" in results[0]

def test_competitor_search_graph_execution():
    res = run_competitor_analysis(
        product_name="AI Writing Assistant",
        content_type="commercial",
        sense="Position as premier alternative for agency copywriters"
    )
    assert "analysis" in res
    assert "query_used" in res
    analysis = res["analysis"]
    assert "topics_covered" in analysis
    assert "style_structure" in analysis
    assert "depth_scope" in analysis
