from __future__ import annotations
import enum, os, sys
from datetime import datetime
from typing import List, Optional

# Windows path fix
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from config.settings import settings

_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if _sqlite else {},
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

class Base(DeclarativeBase):
    pass

class DealStatus(str, enum.Enum):
    LEAD = "lead"; QUALIFIED = "qualified"; PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"; WON = "won"; LOST = "lost"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"; IN_PROGRESS = "in_progress"
    COMPLETED = "completed"; CANCELLED = "cancelled"

class ActivityType(str, enum.Enum):
    CALL = "call"; EMAIL = "email"; MEETING = "meeting"; NOTE = "note"; ORDER = "order"

class ApiKeyStatus(str, enum.Enum):
    ACTIVE = "active"; REVOKED = "revoked"; EXPIRED = "expired"

class ApiKey(Base):
    __tablename__ = "api_keys"
    id          : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_hash    : Mapped[str]           = mapped_column(String(64), unique=True, nullable=False, index=True)
    key_prefix  : Mapped[str]           = mapped_column(String(16), nullable=False)
    name        : Mapped[str]           = mapped_column(String(100), nullable=False)
    description : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status      : Mapped[ApiKeyStatus]  = mapped_column(SAEnum(ApiKeyStatus), default=ApiKeyStatus.ACTIVE)
    scopes      : Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at  : Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at  : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    id          : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name        : Mapped[str]           = mapped_column(String(200), nullable=False, index=True)
    company     : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone       : Mapped[Optional[str]] = mapped_column(String(60),  nullable=True)
    address     : Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    city        : Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state       : Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country     : Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    territory   : Mapped[Optional[str]] = mapped_column(String(20),  nullable=True, index=True)
    industry    : Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email       : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active   : Mapped[bool]          = mapped_column(Boolean, default=True)
    hf_source   : Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at  : Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    updated_at  : Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacts    : Mapped[List["Contact"]]  = relationship("Contact",  back_populates="customer", cascade="all, delete-orphan")
    deals       : Mapped[List["Deal"]]     = relationship("Deal",     back_populates="customer", cascade="all, delete-orphan")
    activities  : Mapped[List["Activity"]] = relationship("Activity", back_populates="customer")

class Contact(Base):
    __tablename__ = "contacts"
    id          : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id : Mapped[int]           = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    first_name  : Mapped[str]           = mapped_column(String(100), nullable=False)
    last_name   : Mapped[str]           = mapped_column(String(100), nullable=False)
    email       : Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone       : Mapped[Optional[str]] = mapped_column(String(60),  nullable=True)
    title       : Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary  : Mapped[bool]          = mapped_column(Boolean, default=False)
    created_at  : Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    updated_at  : Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer    : Mapped["Customer"]    = relationship("Customer", back_populates="contacts")

class Deal(Base):
    __tablename__ = "deals"
    id                  : Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id         : Mapped[int]            = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    title               : Mapped[str]            = mapped_column(String(300), nullable=False)
    order_number        : Mapped[Optional[str]]  = mapped_column(String(20),  nullable=True, index=True)
    hf_status           : Mapped[Optional[str]]  = mapped_column(String(30),  nullable=True)
    product_line        : Mapped[Optional[str]]  = mapped_column(String(100), nullable=True, index=True)
    product_code        : Mapped[Optional[str]]  = mapped_column(String(30),  nullable=True)
    quantity_ordered    : Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    price_each          : Mapped[Optional[float]]= mapped_column(Numeric(10,2), nullable=True)
    msrp                : Mapped[Optional[float]]= mapped_column(Numeric(10,2), nullable=True)
    revenue             : Mapped[Optional[float]]= mapped_column(Numeric(15,2), nullable=True)
    deal_size           : Mapped[Optional[str]]  = mapped_column(String(10),  nullable=True)
    quarter             : Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    order_month         : Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    order_year          : Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    order_date          : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status              : Mapped[DealStatus]     = mapped_column(SAEnum(DealStatus), default=DealStatus.LEAD, index=True)
    value               : Mapped[Optional[float]]= mapped_column(Numeric(15,2), nullable=True)
    probability         : Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    expected_close_date : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_at           : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes               : Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at          : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    updated_at          : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer    : Mapped["Customer"]       = relationship("Customer",  back_populates="deals")
    tasks       : Mapped[List["Task"]]     = relationship("Task",      back_populates="deal")
    activities  : Mapped[List["Activity"]] = relationship("Activity",  back_populates="deal")

class Task(Base):
    __tablename__ = "tasks"
    id          : Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    deal_id     : Mapped[Optional[int]]  = mapped_column(ForeignKey("deals.id"), nullable=True, index=True)
    title       : Mapped[str]            = mapped_column(String(300), nullable=False)
    description : Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    status      : Mapped[TaskStatus]     = mapped_column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    due_date    : Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    assigned_to : Mapped[Optional[str]]  = mapped_column(String(200), nullable=True)
    created_at  : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    updated_at  : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deal        : Mapped[Optional["Deal"]] = relationship("Deal", back_populates="tasks")

class Activity(Base):
    __tablename__ = "activities"
    id          : Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id : Mapped[Optional[int]]  = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    deal_id     : Mapped[Optional[int]]  = mapped_column(ForeignKey("deals.id"),     nullable=True, index=True)
    type        : Mapped[ActivityType]   = mapped_column(SAEnum(ActivityType), nullable=False)
    subject     : Mapped[str]            = mapped_column(String(300), nullable=False)
    description : Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    occurred_at : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    created_at  : Mapped[datetime]       = mapped_column(DateTime, default=datetime.utcnow)
    customer    : Mapped[Optional["Customer"]] = relationship("Customer", back_populates="activities")
    deal        : Mapped[Optional["Deal"]]     = relationship("Deal",     back_populates="activities")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
