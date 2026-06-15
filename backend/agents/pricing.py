import logging
from typing import Dict, Any
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

PRICING_SYSTEM_PROMPT = """You are the Pricing AI for FreightGPT UAE.
Calculate optimal pricing based on: Fuel, Distance, Tolls, Driver Cost, Maintenance, Profit Margin.
Output: Minimum Rate, Target Rate, Aggressive Bid, Premium Bid.
Consider GCC-specific factors: fuel subsidies in UAE/Saudi, Salik tolls in Dubai,
border crossing fees, regional rate variations, seasonal demand fluctuations.
Always ensure profitable pricing while remaining competitive."""


class PricingAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("pricing", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "calculate_price")
        origin = input_data.get("origin_city", "")
        destination = input_data.get("destination_city", "")
        distance = input_data.get("distance_km", 0)
        weight = input_data.get("weight_kg", 0)
        equipment = input_data.get("equipment_type", "trailer")
        truck_type = input_data.get("truck_type", "trailer")
        market_rates = input_data.get("market_rates", {})
        operational_costs = input_data.get("operational_costs", {})

        if action == "calculate_price":
            return await self._calculate_price(
                origin, destination, distance, weight, equipment,
                truck_type, market_rates, operational_costs
            )
        elif action == "competitive_analysis":
            return await self._competitive_analysis(
                origin, destination, weight, equipment, market_rates
            )
        elif action == "profit_margin_analysis":
            return await self._calculate_margins(
                input_data.get("rate", 0), operational_costs
            )
        else:
            return await self._calculate_price(
                origin, destination, distance, weight, equipment,
                truck_type, market_rates, operational_costs
            )

    async def _calculate_price(
        self, origin: str, destination: str, distance: float,
        weight: float, equipment: str, truck_type: str,
        market_rates: Dict[str, Any], operational_costs: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Calculate comprehensive pricing for this load:
Route: {origin} -> {destination}
Distance: {distance} km
Weight: {weight} kg
Equipment: {equipment}
Truck Type: {truck_type}
Market Rates: {market_rates}
Operational Costs: {operational_costs}

Calculate:
1. Fuel Cost (based on distance, consumption rate, UAE/GCC fuel prices)
2. Driver Cost (daily rate + allowances)
3. Toll Costs (Salik, GCC road tolls, border fees)
4. Maintenance Allocation
5. Insurance Cost
6. Overhead Allocation

Output pricing tiers:
- Minimum Rate (break-even + 5% margin)
- Target Rate (healthy 15-20% margin)
- Aggressive Bid (win strategy, 8-10% margin)
- Premium Bid (expedited/premium service, 25-30% margin)

Provide detailed breakdown for each tier."""
        result = await self.think(prompt, PRICING_SYSTEM_PROMPT)
        return {"pricing": result}

    async def _competitive_analysis(
        self, origin: str, destination: str, weight: float,
        equipment: str, market_rates: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Perform competitive pricing analysis:
Route: {origin} -> {destination}
Weight: {weight} kg
Equipment: {equipment}
Market Rates: {market_rates}

Analyze: current market rate range, our competitive position, pricing strategy recommendation,
expected win rate at different price points, seasonal rate adjustments for GCC market."""
        result = await self.think(prompt, PRICING_SYSTEM_PROMPT)
        return {"competitive_analysis": result}

    async def _calculate_margins(self, rate: float, costs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Calculate profit margins:
Proposed Rate: {rate} {costs.get('currency', 'AED')}
Operational Costs: {costs}

Calculate: gross margin, net margin, contribution margin, return on route.
Determine if rate is profitable and provide margin improvement recommendations."""
        result = await self.think(prompt, PRICING_SYSTEM_PROMPT)
        return {"margin_analysis": result}
