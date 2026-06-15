from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AgentRunResponse(BaseModel):
    id: UUID
    agent_type: str
    status: str
    input_data: dict
    output_data: dict
    error: Optional[str]
    duration_ms: Optional[int]
    model_used: Optional[str]
    tokens_used: Optional[int]
    cost: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class AgentTaskResponse(BaseModel):
    id: UUID
    task_name: str
    status: str
    input_data: dict
    output_data: dict
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AgentRunCreate(BaseModel):
    agent_type: str
    input_data: dict


class MarketIntelligenceQuery(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    max_results: int = 10


class LoadAcquisitionRequest(BaseModel):
    load_id: UUID
    max_bid_amount: Optional[float] = None


class ShipperSearchQuery(BaseModel):
    industry: Optional[str] = None
    location: Optional[str] = None
    min_size: Optional[str] = None


class PricingRequest(BaseModel):
    origin_city: str
    destination_city: str
    distance_km: float
    weight_kg: float
    equipment_type: str
    truck_type: str


class PricingResponse(BaseModel):
    minimum_rate: float
    target_rate: float
    aggressive_bid: float
    premium_bid: float
    breakdown: dict
