from __future__ import annotations
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy.ext.asyncio import AsyncSession
from src.crm.services import CustomerService, DealService, ContactService, TaskService, ActivityService
from src.db.models import DealStatus, ActivityType

TOOLS = [
    {"name": "list_customers",        "description": "Müşteri listesi. Filtreler: search, country, territory, industry"},
    {"name": "get_customer",          "description": "Tek müşteri detayı. Parametre: customer_id"},
    {"name": "create_customer",       "description": "Yeni müşteri oluştur"},
    {"name": "update_customer",       "description": "Müşteri güncelle"},
    {"name": "list_deals",            "description": "Deal listesi. Filtreler: customer_id, status, product_line, deal_size, order_year, quarter"},
    {"name": "get_deal",              "description": "Tek deal detayı. Parametre: deal_id"},
    {"name": "create_deal",           "description": "Yeni deal oluştur"},
    {"name": "update_deal",           "description": "Deal güncelle"},
    {"name": "list_contacts",         "description": "Müşteri kontakları. Parametre: customer_id"},
    {"name": "create_contact",        "description": "Yeni kontak ekle"},
    {"name": "list_tasks",            "description": "Deal görevleri. Parametre: deal_id"},
    {"name": "create_task",           "description": "Yeni görev ekle"},
    {"name": "list_activities",       "description": "Aktivite geçmişi. Filtreler: customer_id, deal_id"},
    {"name": "create_activity",       "description": "Aktivite kaydet"},
    {"name": "pipeline_summary",      "description": "Pipeline özeti — status bazlı"},
    {"name": "stats_by_product_line", "description": "PRODUCTLINE bazlı analiz"},
    {"name": "stats_by_deal_size",    "description": "DEALSIZE dağılımı"},
    {"name": "stats_by_year_quarter", "description": "Yıl/çeyrek timeline"},
    {"name": "stats_by_territory",    "description": "TERRITORY bazlı müşteri dağılımı"},
    {"name": "stats_by_country",      "description": "Ülke bazlı müşteri sayısı"},
    {"name": "top_customers",         "description": "En yüksek gelirli müşteriler. Parametre: limit (default 10)"},
]


async def handle(method: str, params: dict, db: AsyncSession) -> dict:
    name = params.get("name", "")
    args = params.get("arguments", {})

    if method == "tools/list":
        return {"tools": TOOLS}

    if method != "tools/call":
        return {"error": f"Unknown method: {method}"}

    try:
        # ── Customers ──────────────────────────────────────────────────────
        if name == "list_customers":
            rows = await CustomerService.list(db, **{k: args.get(k) for k in ["skip","limit","search","country","territory","industry"] if k in args or k in ["skip","limit"]})
            return {"result": [{"id":r.id,"name":r.name,"country":r.country,"territory":r.territory,"industry":r.industry} for r in rows]}

        if name == "get_customer":
            r = await CustomerService.get(db, args["customer_id"])
            if not r:
                return {"error": "Not found"}
            return {"result": {"id":r.id,"name":r.name,"company":r.company,"phone":r.phone,"city":r.city,"country":r.country,"territory":r.territory,"industry":r.industry}}

        if name == "create_customer":
            r = await CustomerService.create(db, args)
            return {"result": {"id": r.id, "name": r.name}}

        if name == "update_customer":
            cid = args.pop("customer_id")
            r = await CustomerService.update(db, cid, args)
            return {"result": {"id": r.id}} if r else {"error": "Not found"}

        # ── Deals ──────────────────────────────────────────────────────────
        if name == "list_deals":
            rows = await DealService.list(db, **{k: args[k] for k in ["skip","limit","customer_id","status","product_line","deal_size","order_year","quarter"] if k in args})
            return {"result": [{"id":r.id,"title":r.title,"status":r.status,"product_line":r.product_line,"deal_size":r.deal_size,"revenue":float(r.revenue or 0)} for r in rows]}

        if name == "get_deal":
            r = await DealService.get(db, args["deal_id"])
            if not r:
                return {"error": "Not found"}
            return {"result": {"id":r.id,"title":r.title,"order_number":r.order_number,"product_line":r.product_line,"deal_size":r.deal_size,"revenue":float(r.revenue or 0),"status":r.status,"order_year":r.order_year,"quarter":r.quarter}}

        if name == "create_deal":
            r = await DealService.create(db, args)
            return {"result": {"id": r.id, "title": r.title}}

        if name == "update_deal":
            did = args.pop("deal_id")
            r = await DealService.update(db, did, args)
            return {"result": {"id": r.id}} if r else {"error": "Not found"}

        # ── Contacts ───────────────────────────────────────────────────────
        if name == "list_contacts":
            rows = await ContactService.list(db, args["customer_id"])
            return {"result": [{"id":r.id,"first_name":r.first_name,"last_name":r.last_name,"email":r.email,"is_primary":r.is_primary} for r in rows]}

        if name == "create_contact":
            r = await ContactService.create(db, args)
            return {"result": {"id": r.id}}

        # ── Tasks ──────────────────────────────────────────────────────────
        if name == "list_tasks":
            rows = await TaskService.list(db, args["deal_id"])
            return {"result": [{"id":r.id,"title":r.title,"status":r.status,"due_date":str(r.due_date)} for r in rows]}

        if name == "create_task":
            r = await TaskService.create(db, args)
            return {"result": {"id": r.id}}

        # ── Activities ─────────────────────────────────────────────────────
        if name == "list_activities":
            rows = await ActivityService.list(db, customer_id=args.get("customer_id"), deal_id=args.get("deal_id"))
            return {"result": [{"id":r.id,"type":r.type,"subject":r.subject,"occurred_at":str(r.occurred_at)} for r in rows]}

        if name == "create_activity":
            r = await ActivityService.create(db, args)
            return {"result": {"id": r.id}}

        # ── Analytics ──────────────────────────────────────────────────────
        if name == "pipeline_summary":
            return {"result": await DealService.pipeline_summary(db)}

        if name == "stats_by_product_line":
            return {"result": await DealService.stats_by_product_line(db)}

        if name == "stats_by_deal_size":
            return {"result": await DealService.stats_by_deal_size(db)}

        if name == "stats_by_year_quarter":
            return {"result": await DealService.stats_by_year_quarter(db)}

        if name == "stats_by_territory":
            return {"result": await CustomerService.stats_by_territory(db)}

        if name == "stats_by_country":
            return {"result": await CustomerService.stats_by_country(db)}

        if name == "top_customers":
            return {"result": await DealService.top_customers(db, limit=args.get("limit", 10))}

        return {"error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"error": str(e)}
