from __future__ import annotations
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from typing import List, Optional
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Customer, Contact, Deal, Task, Activity, DealStatus


class CustomerService:
    @staticmethod
    async def list(db: AsyncSession, skip=0, limit=50,
                   search=None, country=None, territory=None, industry=None):
        q = select(Customer).where(Customer.is_active == True)
        if search:
            q = q.where(Customer.name.ilike(f"%{search}%"))
        if country:
            q = q.where(Customer.country == country)
        if territory:
            q = q.where(Customer.territory == territory)
        if industry:
            q = q.where(Customer.industry == industry)
        q = q.offset(skip).limit(limit)
        return (await db.execute(q)).scalars().all()

    @staticmethod
    async def get(db: AsyncSession, cid: int):
        return (await db.execute(select(Customer).where(Customer.id == cid))).scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: dict):
        obj = Customer(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, cid: int, data: dict):
        obj = await CustomerService.get(db, cid)
        if not obj:
            return None
        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def stats_by_territory(db: AsyncSession):
        q = select(Customer.territory, func.count(Customer.id)).group_by(Customer.territory)
        rows = (await db.execute(q)).all()
        return [{"territory": r[0], "count": r[1]} for r in rows]

    @staticmethod
    async def stats_by_country(db: AsyncSession):
        q = select(Customer.country, func.count(Customer.id)).group_by(Customer.country).order_by(func.count(Customer.id).desc()).limit(20)
        rows = (await db.execute(q)).all()
        return [{"country": r[0], "count": r[1]} for r in rows]


class DealService:
    @staticmethod
    async def list(db: AsyncSession, skip=0, limit=50,
                   customer_id=None, status=None, product_line=None,
                   deal_size=None, order_year=None, quarter=None):
        q = select(Deal)
        if customer_id:
            q = q.where(Deal.customer_id == customer_id)
        if status:
            q = q.where(Deal.status == status)
        if product_line:
            q = q.where(Deal.product_line == product_line)
        if deal_size:
            q = q.where(Deal.deal_size == deal_size)
        if order_year:
            q = q.where(Deal.order_year == order_year)
        if quarter:
            q = q.where(Deal.quarter == quarter)
        q = q.offset(skip).limit(limit)
        return (await db.execute(q)).scalars().all()

    @staticmethod
    async def get(db: AsyncSession, did: int):
        return (await db.execute(select(Deal).where(Deal.id == did))).scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: dict):
        obj = Deal(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, did: int, data: dict):
        obj = await DealService.get(db, did)
        if not obj:
            return None
        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def pipeline_summary(db: AsyncSession):
        q = select(Deal.status, func.count(Deal.id), func.sum(Deal.value)).group_by(Deal.status)
        rows = (await db.execute(q)).all()
        return [{"status": r[0], "count": r[1], "total_value": float(r[2] or 0)} for r in rows]

    @staticmethod
    async def stats_by_product_line(db: AsyncSession):
        q = select(Deal.product_line, func.count(Deal.id), func.sum(Deal.revenue), func.avg(Deal.price_each)).group_by(Deal.product_line).order_by(func.sum(Deal.revenue).desc())
        rows = (await db.execute(q)).all()
        return [{"product_line": r[0], "count": r[1], "total_revenue": float(r[2] or 0), "avg_price": float(r[3] or 0)} for r in rows]

    @staticmethod
    async def stats_by_deal_size(db: AsyncSession):
        q = select(Deal.deal_size, func.count(Deal.id), func.sum(Deal.revenue)).group_by(Deal.deal_size)
        rows = (await db.execute(q)).all()
        return [{"deal_size": r[0], "count": r[1], "total_revenue": float(r[2] or 0)} for r in rows]

    @staticmethod
    async def stats_by_year_quarter(db: AsyncSession):
        q = select(Deal.order_year, Deal.quarter, func.count(Deal.id), func.sum(Deal.revenue)).group_by(Deal.order_year, Deal.quarter).order_by(Deal.order_year, Deal.quarter)
        rows = (await db.execute(q)).all()
        return [{"year": r[0], "quarter": r[1], "count": r[2], "revenue": float(r[3] or 0)} for r in rows]

    @staticmethod
    async def top_customers(db: AsyncSession, limit=10):
        q = select(Customer.name, func.sum(Deal.revenue).label("total")).join(Deal).group_by(Customer.id).order_by(func.sum(Deal.revenue).desc()).limit(limit)
        rows = (await db.execute(q)).all()
        return [{"customer": r[0], "total_revenue": float(r[1] or 0)} for r in rows]


class ContactService:
    @staticmethod
    async def list(db: AsyncSession, customer_id: int):
        q = select(Contact).where(Contact.customer_id == customer_id)
        return (await db.execute(q)).scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: dict):
        obj = Contact(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj


class TaskService:
    @staticmethod
    async def list(db: AsyncSession, deal_id: int):
        q = select(Task).where(Task.deal_id == deal_id)
        return (await db.execute(q)).scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: dict):
        obj = Task(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj


class ActivityService:
    @staticmethod
    async def list(db: AsyncSession, customer_id=None, deal_id=None, limit=50):
        q = select(Activity)
        if customer_id:
            q = q.where(Activity.customer_id == customer_id)
        if deal_id:
            q = q.where(Activity.deal_id == deal_id)
        q = q.order_by(Activity.occurred_at.desc()).limit(limit)
        return (await db.execute(q)).scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: dict):
        obj = Activity(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj
