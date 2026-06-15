import logging
from typing import Dict, Any, Optional, Type
from agents import (
    MarketIntelligenceAgent,
    LoadAcquisitionAgent,
    ShipperAcquisitionAgent,
    SalesAgent,
    DispatchAgent,
    DriverCopilotAgent,
    PricingAgent,
    DocumentAIAgent,
    FinanceAgent,
    CEOAgent,
)
from core.database import redis_client
from core.config import settings
import json

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self):
        self._agents = {
            "market_intelligence": MarketIntelligenceAgent,
            "load_acquisition": LoadAcquisitionAgent,
            "shipper_acquisition": ShipperAcquisitionAgent,
            "sales": SalesAgent,
            "dispatch": DispatchAgent,
            "driver_copilot": DriverCopilotAgent,
            "pricing": PricingAgent,
            "document_ai": DocumentAIAgent,
            "finance": FinanceAgent,
            "ceo": CEOAgent,
        }

    def get_agent(self, agent_type: str):
        agent_class = self._agents.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class()

    async def run_agent(self, agent_type: str, input_data: Dict[str, Any],
                        tenant_id: Optional[str] = None) -> Dict[str, Any]:
        agent = self.get_agent(agent_type)
        result = await agent.run(input_data)

        if redis_client:
            cache_key = f"agent_run:{agent_type}:{result.get('run_id')}"
            await redis_client.setex(cache_key, 3600, json.dumps(result))

        return result

    async def run_workflow(self, workflow_name: str,
                           input_data: Dict[str, Any]) -> Dict[str, Any]:
        workflows = {
            "acquire_load": self._workflow_acquire_load,
            "dispatch_shipment": self._workflow_dispatch_shipment,
            "process_document": self._workflow_process_document,
            "generate_report": self._workflow_generate_report,
            "onboard_shipper": self._workflow_onboard_shipper,
        }
        workflow = workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        return await workflow(input_data)

    async def _workflow_acquire_load(self, data: Dict[str, Any]) -> Dict[str, Any]:
        load_data = data.get("load_data", {})
        fleet = data.get("fleet_status", {})

        evaluation = await self.run_agent("load_acquisition", {
            "action": "evaluate_load", "load_data": load_data, "fleet_status": fleet
        })

        if evaluation.get("status") != "completed":
            return {"workflow": "acquire_load", "status": "failed", "step": "evaluation"}

        pricing = await self.run_agent("pricing", {
            "action": "calculate_price", **load_data
        })

        bid = await self.run_agent("load_acquisition", {
            "action": "prepare_bid", "load_data": load_data, "pricing": pricing.get("output", {})
        })

        return {
            "workflow": "acquire_load",
            "status": "completed",
            "evaluation": evaluation,
            "pricing": pricing,
            "bid": bid,
        }

    async def _workflow_dispatch_shipment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        load = data.get("load", {})
        fleet = data.get("available_fleet", {})
        drivers = data.get("available_drivers", [])

        dispatch = await self.run_agent("dispatch", {
            "action": "dispatch_load", "load": load,
            "available_fleet": fleet, "available_drivers": drivers
        })

        return {"workflow": "dispatch_shipment", "status": "completed", "dispatch": dispatch}

    async def _workflow_process_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        doc_result = await self.run_agent("document_ai", {
            "action": "process_document",
            "document_type": data.get("document_type", "pod"),
            "ocr_text": data.get("ocr_text", ""),
            "file_metadata": data.get("file_metadata", {}),
        })
        return {"workflow": "process_document", "status": "completed", "document": doc_result}

    async def _workflow_generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        metrics = data.get("metrics", {})
        agent_reports = data.get("agent_reports", {})
        report = await self.run_agent("ceo", {
            "action": data.get("report_type", "daily_report"),
            "metrics": metrics, "agent_reports": agent_reports,
        })
        return {"workflow": "generate_report", "status": "completed", "report": report}

    async def _workflow_onboard_shipper(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lead = await self.run_agent("shipper_acquisition", {
            "action": "find_leads",
            "target_market": data.get("market", "UAE"),
            "industry": data.get("industry", "import_export"),
            "location": data.get("location", "Dubai"),
        })
        outreach = await self.run_agent("sales", {
            "action": "handle_inquiry",
            "channel": "email",
            "message": data.get("initial_message", "Introduction"),
            "customer": {"company": data.get("company_name", "")},
        })
        return {"workflow": "onboard_shipper", "status": "completed", "lead": lead, "outreach": outreach}


orchestrator = AgentOrchestrator()
