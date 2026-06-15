import logging
from typing import Dict, Any, Optional, List
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

DISPATCH_SYSTEM_PROMPT = """You are the Dispatch Agent for FreightGPT UAE.
Responsibilities: Truck Assignment, Driver Assignment, Route Planning, Fuel Optimization, ETA Prediction.
Optimize for cost efficiency, timeliness, and driver satisfaction.
Consider GCC road networks, traffic patterns, border crossings, rest stops, and fuel stations.
Always have alternative plans for contingencies."""


class DispatchAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("dispatch", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "dispatch_load")
        load = input_data.get("load", {})
        fleet = input_data.get("available_fleet", {})
        drivers = input_data.get("available_drivers", [])

        if action == "assign_truck":
            return await self._assign_truck(load, fleet)
        elif action == "assign_driver":
            return await self._assign_driver(load, drivers)
        elif action == "plan_route":
            return await self._plan_route(load)
        elif action == "optimize_fuel":
            return await self._optimize_fuel(load, input_data.get("route", {}))
        elif action == "predict_eta":
            return await self._predict_eta(load, input_data.get("route", {}))
        elif action == "dispatch_load":
            return await self._dispatch_load(load, fleet, drivers)
        else:
            return await self._dispatch_load(load, fleet, drivers)

    async def _assign_truck(self, load: Dict[str, Any], fleet: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Assign the optimal truck for this load:
Load: {load}
Available Fleet: {fleet}

Consider: truck type match (trailer/reefer/flatbed etc), capacity, current location, maintenance status,
equipment compatibility. Return: recommended_truck_id, reasoning, match_score, alternative_options."""
        result = await self.think(prompt, DISPATCH_SYSTEM_PROMPT)
        return {"truck_assignment": result}

    async def _assign_driver(self, load: Dict[str, Any], drivers: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"""Assign the optimal driver for this load:
Load: {load}
Available Drivers: {drivers}

Consider: driving hours compliance (UAE/GCC regulations), language match for destination,
experience with route, ratings, rest status, license endorsements.
Return: recommended_driver_id, reasoning, match_score, hours_available."""
        result = await self.think(prompt, DISPATCH_SYSTEM_PROMPT)
        return {"driver_assignment": result}

    async def _plan_route(self, load: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Plan optimal route for this load:
Load: {load}

Consider: GCC road network, distance optimization, toll roads, traffic patterns by time of day,
border crossings (if international), rest stops, fuel stations, driving time regulations.
Provide: route_description, distance_km, estimated_hours, waypoints, alternative_routes,
toll_cost_estimate, recommended_departure_time."""
        result = await self.think(prompt, DISPATCH_SYSTEM_PROMPT)
        return {"route_plan": result}

    async def _optimize_fuel(self, load: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Optimize fuel strategy for this route:
Load: {load}
Route: {route}

Consider: fuel prices across GCC countries (UAE, Saudi Arabia, Qatar, Oman, Bahrain),
fuel station locations along route, truck fuel efficiency, optimal refueling points,
fuel type availability. Return: fuel_stops, estimated_fuel_cost, cost_saving_recommendations."""
        result = await self.think(prompt, DISPATCH_SYSTEM_PROMPT)
        return {"fuel_optimization": result}

    async def _predict_eta(self, load: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Predict ETA for this shipment:
Load: {load}
Route: {route}

Consider: distance, average speed by road type, traffic patterns, border crossing delays (if any),
rest requirements, weather conditions, time of day.
Return: estimated_arrival, confidence_level, factors_affecting_eta, realtime_adjustment_recommendations."""
        result = await self.think(prompt, DISPATCH_SYSTEM_PROMPT)
        return {"eta_prediction": result}

    async def _dispatch_load(self, load: Dict[str, Any], fleet: Dict[str, Any],
                             drivers: List[Dict[str, Any]]) -> Dict[str, Any]:
        truck = await self._assign_truck(load, fleet)
        driver = await self._assign_driver(load, drivers)
        route = await self._plan_route(load)
        eta = await self._predict_eta(load, route)

        return {
            "dispatch_plan": {
                "load_id": load.get("id"),
                "truck": truck,
                "driver": driver,
                "route": route,
                "eta": eta,
            },
            "status": "dispatched" if truck and driver else "pending_assignment",
        }
