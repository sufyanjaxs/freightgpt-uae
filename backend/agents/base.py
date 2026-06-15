import logging
import time
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from core.llm_router import llm_router
from core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, agent_type: str, model: str = "gpt-4"):
        self.agent_type = agent_type
        self.model = model
        self.llm = llm_router

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        run_id = uuid.uuid4()
        logger.info(f"[{self.agent_type}] Run {run_id} started with input: {input_data}")

        try:
            result = await self.execute(input_data)
            duration = int((time.time() - start_time) * 1000)
            logger.info(f"[{self.agent_type}] Run {run_id} completed in {duration}ms")
            return {
                "run_id": str(run_id),
                "agent_type": self.agent_type,
                "status": "completed",
                "output": result,
                "duration_ms": duration,
                "model_used": self.model,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            logger.error(f"[{self.agent_type}] Run {run_id} failed: {str(e)}")
            return {
                "run_id": str(run_id),
                "agent_type": self.agent_type,
                "status": "failed",
                "error": str(e),
                "duration_ms": duration,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def think(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return await self.llm.route(
            prompt=prompt,
            model=self.model,
            system_prompt=system_prompt,
        )

    async def think_structured(self, prompt: str, output_model: type, system_prompt: Optional[str] = None) -> Any:
        return await self.llm.generate_structured(
            prompt=prompt,
            output_model=output_model,
            model=self.model,
            system_prompt=system_prompt,
        )
