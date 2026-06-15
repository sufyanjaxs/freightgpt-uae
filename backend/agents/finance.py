import logging
from typing import Dict, Any, Optional
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

FINANCE_SYSTEM_PROMPT = """You are the Finance Agent for FreightGPT UAE.
Handle: Invoices, Collections, Factoring, Profit Analysis, Tax Reports.
Ensure financial accuracy, optimize cash flow, manage receivables, and ensure GCC tax compliance (VAT).
Track profitability per load, per route, per customer, and per driver."""


class FinanceAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("finance", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "analyze_profit")
        financial_data = input_data.get("financial_data", {})
        period = input_data.get("period", "this_month")

        if action == "generate_invoice":
            return await self._generate_invoice(input_data.get("load_data", {}))
        elif action == "process_payment":
            return await self._process_payment(input_data.get("payment_data", {}))
        elif action == "analyze_profit":
            return await self._analyze_profit(financial_data, period)
        elif action == "collections_analysis":
            return await self._collections_analysis(financial_data)
        elif action == "factoring_eligibility":
            return await self._factoring_eligibility(input_data.get("invoices", []))
        elif action == "tax_report":
            return await self._generate_tax_report(financial_data, period)
        elif action == "cash_flow_forecast":
            return await self._cash_flow_forecast(financial_data)
        else:
            return await self._analyze_profit(financial_data, period)

    async def _generate_invoice(self, load_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Generate a professional invoice for freight service:
Load Details: {load_data}

Create invoice with: unique invoice number, shipper/customer details, load details,
rate breakdown, VAT calculation (5% UAE VAT), payment terms, due date,
banking details, FreightGPT UAE branding.
Format for professional GCC business use."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"invoice": result}

    async def _process_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Process payment reconciliation:
Payment Data: {payment_data}

Verify: amount matches invoice, payment method, transaction reference,
allocate to correct invoice, update accounts receivable, trigger notifications.
Handle: bank transfers, cards, cheques (common in GCC), factoring payments."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"payment_processed": result}

    async def _analyze_profit(self, financial_data: Dict[str, Any], period: str) -> Dict[str, Any]:
        prompt = f"""Perform comprehensive profit analysis:
Financial Data: {financial_data}
Period: {period}

Analyze: total revenue, total costs (fuel, driver, maintenance, tolls, overhead),
gross profit, net profit, profit margin, profit per load, profit per route,
profit per customer, profit per driver.
Identify trends, top performers, and areas for improvement.
Provide specific recommendations to increase profitability."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"profit_analysis": result}

    async def _collections_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Analyze accounts receivable and collections:
Financial Data: {financial_data}

Analyze: aging report (current, 30, 60, 90+ days), dunning strategy recommendations,
high-risk accounts, collection priorities, expected recovery timeline.
Consider GCC payment culture and typical payment terms."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"collections_analysis": result}

    async def _factoring_eligibility(self, invoices: list) -> Dict[str, Any]:
        prompt = f"""Evaluate invoice factoring eligibility:
Invoices: {invoices}

Assess: invoice quality, customer creditworthiness, invoice age, total eligible amount,
advance rate, discount rate/commission, expected funding timeline.
Provide recommendation on which invoices to factor and optimal timing."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"factoring_analysis": result}

    async def _generate_tax_report(self, financial_data: Dict[str, Any], period: str) -> Dict[str, Any]:
        prompt = f"""Generate VAT/Tax report for GCC compliance:
Financial Data: {financial_data}
Period: {period}

Calculate: output VAT (5% UAE rate, 15% Saudi rate), input VAT recoverable,
net VAT payable/refundable, VAT return preparation checklist.
Handle multi-country GCC operations with different VAT rates."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"tax_report": result}

    async def _cash_flow_forecast(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Generate cash flow forecast:
Financial Data: {financial_data}

Project: expected inflows (collections, payments), expected outflows (driver payments,
fuel, maintenance, overhead), net cash position, funding gap analysis,
recommended actions to optimize cash flow.
30/60/90 day forecast horizon."""
        result = await self.think(prompt, FINANCE_SYSTEM_PROMPT)
        return {"cash_flow_forecast": result}
