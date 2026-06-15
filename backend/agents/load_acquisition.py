import logging
from typing import Dict, Any
from datetime import datetime, timezone
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

LOAD_ACQ_SYSTEM_PROMPT = """You are the Load Acquisition Agent for FreightGPT UAE.
Your workflow: Monitor Load Boards -> New Load Appears -> Calculate Profit -> Check Truck Availability -> Prepare Bid -> Request Approval -> Book Load.
Always calculate profitability before bidding. Consider distance, fuel, tolls, driver cost, maintenance, and profit margin.
Connect through official APIs and authorized integrations only. Never bypass platform rules."""


class LoadAcquisitionAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("load_acquisition", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "acquire_load")
        load_data = input_data.get("load_data", {})
        fleet_status = input_data.get("fleet_status", {})

        if action == "evaluate_load":
            return await self._evaluate_load(load_data, fleet_status)
        elif action == "prepare_bid":
            return await self._prepare_bid(load_data, input_data.get("pricing", {}))
        elif action == "monitor_boards":
            return await self._monitor_boards(input_data)
        elif action == "book_load":
            return await self._book_load(load_data)
        else:
            return await self._acquire_load(load_data, fleet_status)

    async def _evaluate_load(self, load_data: Dict[str, Any], fleet_status: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Evaluate this freight load for acquisition:
Load Details: {load_data}
Fleet Status: {fleet_status}

Analyze: profitability potential, truck availability match, route feasibility, timing compatibility, risk factors.
Return: score (1-100), recommendation (acquire/pass/negotiate), reasoning, suggested bid range."""
        result = await self.think(prompt, LOAD_ACQ_SYSTEM_PROMPT)
        return {"evaluation": result, "load_data": load_data}

    async def _prepare_bid(self, load_data: Dict[str, Any], pricing: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Prepare an optimized bid for this load:
Load Details: {load_data}
Pricing Analysis: {pricing}

Calculate: competitive bid amount, profit margin projection, confidence score, bid strategy (aggressive/standard/premium).
Consider market rates in GCC region, current fleet utilization, and strategic value."""
        result = await self.think(prompt, LOAD_ACQ_SYSTEM_PROMPT)
        return {"bid": result, "prepared_at": datetime.now(timezone.utc).isoformat()}

    async def _monitor_boards(self, config: Dict[str, Any]) -> Dict[str, Any]:
        sources = config.get("sources", ["marketplace_1", "marketplace_2"])
        prompt = f"""Monitor these freight boards/sources for new opportunities: {sources}.
Identify new loads matching our fleet capabilities and preferred routes in GCC.
Return: new_loads_count, prioritized_list, recommended_immediate_actions."""
        result = await self.think(prompt, LOAD_ACQ_SYSTEM_PROMPT)
        return {"monitoring_results": result}

    async def _book_load(self, load_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Process booking for this approved load:
Load Details: {load_data}
Generate: booking confirmation details, carrier assignment recommendation, pickup schedule, document checklist, notification recipients."""
        result = await self.think(prompt, LOAD_ACQ_SYSTEM_PROMPT)
        return {"booking": result}

    async def _acquire_load(self, load_data: Dict[str, Any], fleet_status: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = await self._evaluate_load(load_data, fleet_status)
        if "acquire" in str(evaluation.get("evaluation", "")).lower():
            pricing = {}  # Would come from PricingAgent
            bid = await self._prepare_bid(load_data, pricing)
            return {"strategy": "bid", "evaluation": evaluation, "bid": bid}
        return {"strategy": "pass", "evaluation": evaluation}
