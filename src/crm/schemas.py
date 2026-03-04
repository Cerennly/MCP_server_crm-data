from __future__ import annotations
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.db.models import DealStatus, TaskStatus, ActivityType

# ── Customer ──────────────────────────────────────────────────────────────────
class CustomerCreate(BaseModel):
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    territory: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None

class CustomerUpdate(CustomerCreate):
    name: Optional[str] = None

class CustomerOut(BaseModel):
    id: int
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    territory: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Contact ───────────────────────────────────────────────────────────────────
class ContactCreate(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool = False

class ContactOut(BaseModel):
    id: int
    customer_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    is_primary: bool
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Deal ──────────────────────────────────────────────────────────────────────
class DealCreate(BaseModel):
    customer_id: int
    title: str
    order_number: Optional[str] = None
    product_line: Optional[str] = None
    product_code: Optional[str] = None
    quantity_ordered: Optional[int] = None
    price_each: Optional[float] = None
    msrp: Optional[float] = None
    revenue: Optional[float] = None
    deal_size: Optional[str] = None
    quarter: Optional[int] = None
    order_month: Optional[int] = None
    order_year: Optional[int] = None
    status: DealStatus = DealStatus.LEAD
    value: Optional[float] = None
    probability: Optional[int] = None
    notes: Optional[str] = None

class DealUpdate(DealCreate):
    customer_id: Optional[int] = None
    title: Optional[str] = None

class DealOut(BaseModel):
    id: int
    customer_id: int
    title: str
    order_number: Optional[str] = None
    product_line: Optional[str] = None
    deal_size: Optional[str] = None
    revenue: Optional[float] = None
    value: Optional[float] = None
    status: DealStatus
    order_year: Optional[int] = None
    quarter: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Task ──────────────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    deal_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    deal_id: Optional[int] = None
    title: str
    status: TaskStatus
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Activity ──────────────────────────────────────────────────────────────────
class ActivityCreate(BaseModel):
    customer_id: Optional[int] = None
    deal_id: Optional[int] = None
    type: ActivityType
    subject: str
    description: Optional[str] = None

class ActivityOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    deal_id: Optional[int] = None
    type: ActivityType
    subject: str
    occurred_at: datetime
    model_config = {"from_attributes": True}

# ── API Key ───────────────────────────────────────────────────────────────────
class ApiKeyCreate(BaseModel):
    name: str
    scopes: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class ApiKeyOut(BaseModel):
    id: int
    key_prefix: str
    name: str
    scopes: Optional[str] = None
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
