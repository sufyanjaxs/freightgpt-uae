from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class InvoiceCreate(BaseModel):
    load_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    currency: str = "AED"
    due_date: date
    payment_terms: str = "net_30"
    notes: Optional[str] = None


class InvoiceResponse(InvoiceCreate):
    id: UUID
    tenant_id: UUID
    invoice_number: str
    status: str
    tax_amount: Decimal
    total_amount: Decimal
    issued_date: date
    paid_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = "AED"
    payment_method: str
    transaction_id: Optional[str] = None


class PaymentResponse(PaymentCreate):
    id: UUID
    tenant_id: UUID
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class PayoutCreate(BaseModel):
    driver_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    payout_type: str


class PayoutResponse(PayoutCreate):
    id: UUID
    tenant_id: UUID
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: UUID
    type: str
    category: str
    amount: Decimal
    currency: str
    description: Optional[str]
    reference_type: Optional[str]
    reference_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfitAnalysisResponse(BaseModel):
    total_revenue: Decimal
    total_cost: Decimal
    net_profit: Decimal
    profit_margin: float
    period: str
    breakdown: dict
