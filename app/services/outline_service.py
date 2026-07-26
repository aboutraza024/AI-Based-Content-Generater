import asyncio
from app.schemas.outline import OutlineRequest, OutlineResponse, CompetitorAnalysis
from app.ai.langgraph.competitor_search_graph import run_competitor_analysis
from app.ai.langchain_chains.outline_chain import run_outline_chain
from app.core.logging import logger

class OutlineService:
    async def generate_outline_async(self, req: OutlineRequest) -> OutlineResponse:
        logger.info(f"Generating outline for '{req.product_name}'")

        # Look at what competitors are already covering
        comp_res = await asyncio.to_thread(
            run_competitor_analysis,
            product_name=req.product_name,
            content_type=req.content_type.value,
            sense=req.sense or "Standard intended topic coverage"
        )

        analysis_data = comp_res.get("analysis", {})
        query_used = comp_res.get("query_used", "")

        competitor_analysis = CompetitorAnalysis(
            topics_covered=analysis_data.get("topics_covered", []),
            style_structure=analysis_data.get("style_structure", "Standard informational structure"),
            depth_scope=analysis_data.get("depth_scope", "Comprehensive coverage"),
            summary=analysis_data.get("summary", "Competitor content analyzed successfully.")
        )

        # Then build the outline itself
        outline_markdown = await asyncio.to_thread(
            run_outline_chain,
            language=req.language,
            region=req.region.value,
            content_type=req.content_type.value,
            product_name=req.product_name,
            target_audience=req.target_audience or "General Audience",
            tone=req.tone.value,
            sense=req.sense or "Standard intended topic coverage",
            word_count=req.word_count,
            competitor_summary=competitor_analysis.summary
        )

        return OutlineResponse(
            outline=outline_markdown,
            competitor_analysis=competitor_analysis,
            query_used=query_used,
            request_params=req.model_dump(),
            success=True
        )

outline_service = OutlineService()
