from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.agent import AgentRun
from schemas.agent import (
    AgentRunCreate, AgentRunResponse, MarketIntelligenceQuery,
    LoadAcquisitionRequest, ShipperSearchQuery, PricingRequest, PricingResponse,
)
from services.agent_orchestrator import orchestrator
from typing import Dict, Any
from uuid import UUID

router = APIRouter()


@router.post("/run", response_model=Dict[str, Any])
async def run_agent(
    data: AgentRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await orchestrator.run_agent(
        agent_type=data.agent_type,
        input_data=data.input_data,
        tenant_id=str(current_user.tenant_id),
    )

    run_log = AgentRun(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        agent_type=data.agent_type,
        status=result.get("status", "completed"),
        input_data=data.input_data,
        output_data=result.get("output", {}),
        error=result.get("error"),
        duration_ms=result.get("duration_ms"),
        model_used=result.get("model_used"),
    )
    db.add(run_log)

    return result


@router.post("/workflow/{workflow_name}")
async def run_workflow(
    workflow_name: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await orchestrator.run_workflow(workflow_name, data)
    return result


@router.get("/runs", response_model=list[AgentRunResponse])
async def list_agent_runs(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select, desc
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.tenant_id == current_user.tenant_id)
        .order_by(desc(AgentRun.created_at))
        .limit(limit)
    )
    runs = result.scalars().all()
    return [AgentRunResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    result = await db.execute(
        select(AgentRun).where(AgentRun.id == run_id, AgentRun.tenant_id == current_user.tenant_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return AgentRunResponse.model_validate(run)


@router.post("/market-intelligence")
async def market_intelligence(
    query: MarketIntelligenceQuery,
    current_user: User = Depends(get_current_user),
):
    result = await orchestrator.run_agent("market_intelligence", {
        "action": "analyze_market",
        "query": query.query,
    })
    return result


@router.post("/pricing/calculate", response_model=PricingResponse)
async def calculate_pricing(
    data: PricingRequest,
    current_user: User = Depends(get_current_user),
):
    result = await orchestrator.run_agent("pricing", {
        "action": "calculate_price",
        **data.model_dump(),
    })
    output = result.get("output", {})
    pricing = output.get("pricing", {})
    return PricingResponse(
        minimum_rate=0, target_rate=0, aggressive_bid=0, premium_bid=0,
        breakdown={"raw_result": pricing},
    )
