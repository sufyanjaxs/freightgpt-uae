from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from core.database import get_db
from core.security import get_current_user, require_role
from db.models.user import User, UserRole
from db.models.finance import Invoice, Payment, Payout, Transaction
from schemas.finance import (
    InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentResponse,
    PayoutCreate, PayoutResponse, TransactionResponse, ProfitAnalysisResponse,
)
from typing import List
from uuid import UUID
from decimal import Decimal

router = APIRouter()


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Invoice).where(Invoice.tenant_id == current_user.tenant_id)
        .order_by(Invoice.created_at.desc())
    )
    invoices = result.scalars().all()
    return [InvoiceResponse.model_validate(inv) for inv in invoices]


@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date
    count = await db.scalar(
        select(func.count()).select_from(Invoice).where(Invoice.tenant_id == current_user.tenant_id)
    )
    invoice = Invoice(
        tenant_id=current_user.tenant_id,
        invoice_number=f"INV-{current_user.tenant_id.hex[:6].upper()}-{(count or 0) + 1:05d}",
        tax_amount=data.amount * Decimal("0.05"),
        total_amount=data.amount * Decimal("1.05"),
        issued_date=date.today(),
        **data.model_dump(),
    )
    db.add(invoice)
    await db.flush()
    return InvoiceResponse.model_validate(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == current_user.tenant_id)
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse.model_validate(invoice)


@router.post("/payments", response_model=PaymentResponse)
async def record_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = await db.execute(
        select(Invoice).where(Invoice.id == data.invoice_id, Invoice.tenant_id == current_user.tenant_id)
    )
    invoice = invoice.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    payment = Payment(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(payment)

    invoice.status = "paid"
    from datetime import datetime, timezone
    invoice.paid_date = datetime.now(timezone.utc).date()

    await db.flush()
    return PaymentResponse.model_validate(payment)


@router.get("/payouts", response_model=List[PayoutResponse])
async def list_payouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Payout).where(Payout.tenant_id == current_user.tenant_id)
        .order_by(Payout.created_at.desc())
    )
    payouts = result.scalars().all()
    return [PayoutResponse.model_validate(p) for p in payouts]


@router.post("/payouts", response_model=PayoutResponse)
async def create_payout(
    data: PayoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payout = Payout(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(payout)
    await db.flush()
    return PayoutResponse.model_validate(payout)


@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Transaction).where(Transaction.tenant_id == current_user.tenant_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/profit-analysis", response_model=ProfitAnalysisResponse)
async def profit_analysis(
    period: str = "this_month",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    if period == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "this_quarter":
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = now - timedelta(days=30)

    revenue_result = await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0))
        .where(
            and_(
                Invoice.tenant_id == current_user.tenant_id,
                Invoice.created_at >= start_date,
                Invoice.status == "paid",
            )
        )
    )
    total_revenue = revenue_result.scalar() or Decimal("0")

    cost_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            and_(
                Transaction.tenant_id == current_user.tenant_id,
                Transaction.created_at >= start_date,
                Transaction.type == "expense",
            )
        )
    )
    total_cost = cost_result.scalar() or Decimal("0")

    net_profit = total_revenue - total_cost
    profit_margin = float(net_profit / total_revenue * 100) if total_revenue > 0 else 0

    return ProfitAnalysisResponse(
        total_revenue=total_revenue,
        total_cost=total_cost,
        net_profit=net_profit,
        profit_margin=round(profit_margin, 2),
        period=period,
        breakdown={"period": period, "revenue_count": 0, "cost_count": 0},
    )
