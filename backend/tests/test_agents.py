import pytest
from agents.pricing import PricingAgent
from agents.market_intelligence import MarketIntelligenceAgent
from agents.sales import SalesAgent


@pytest.mark.asyncio
async def test_pricing_agent():
    agent = PricingAgent(model="gpt-4")
    result = await agent.execute({
        "action": "calculate_price",
        "origin_city": "Dubai",
        "destination_city": "Abu Dhabi",
        "distance_km": 150,
        "weight_kg": 5000,
        "equipment_type": "trailer",
        "truck_type": "trailer",
    })
    assert "pricing" in result


@pytest.mark.asyncio
async def test_market_intelligence_agent():
    agent = MarketIntelligenceAgent()
    result = await agent.execute({
        "action": "analyze_market",
        "context": "Current freight rates in UAE",
    })
    assert "market_report" in result


@pytest.mark.asyncio
async def test_sales_agent():
    agent = SalesAgent()
    result = await agent.execute({
        "action": "handle_inquiry",
        "channel": "email",
        "message": "What are your rates for Dubai to Riyadh?",
        "customer": {"name": "Test Corp", "email": "test@corp.com"},
        "language": "en",
    })
    assert "response" in result


@pytest.mark.asyncio
async def test_agent_orchestrator():
    from services.agent_orchestrator import orchestrator
    result = await orchestrator.run_agent("pricing", {
        "origin_city": "Dubai",
        "destination_city": "Sharjah",
        "distance_km": 50,
        "weight_kg": 2000,
        "equipment_type": "box_truck",
        "truck_type": "box_truck",
    })
    assert result["agent_type"] == "pricing"
    assert result["status"] in ("completed", "failed")
