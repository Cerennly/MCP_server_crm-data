from __future__ import annotations
import os, sys

# Windows uyumlu path fix — her zaman projenin kök dizinini ekle
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader, APIKeyQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from src.db.models import create_tables, get_db
from src.auth.api_key import get_api_key, create_api_key, has_scope
from src.crm.schemas import (
    CustomerCreate, CustomerUpdate, CustomerOut,
    ContactCreate, ContactOut,
    DealCreate, DealUpdate, DealOut,
    TaskCreate, TaskOut,
    ActivityCreate, ActivityOut,
    ApiKeyCreate, ApiKeyOut,
)
from src.crm.services import CustomerService, DealService, ContactService, TaskService, ActivityService
from src.mcp.handler import handle as mcp_handle, TOOLS

_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_query  = APIKeyQuery(name="api_key",    auto_error=False)

async def auth(
    h: Optional[str] = Depends(_header),
    q: Optional[str] = Depends(_query),
    db: AsyncSession  = Depends(get_db),
):
    return await get_api_key(db, h, q)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    logger.info(f"CRM MCP Server {settings.MCP_SERVER_VERSION} başlatıldı — http://localhost:{settings.PORT}/docs")
    yield

app = FastAPI(
    title="CRM MCP Server",
    version=settings.MCP_SERVER_VERSION,
    description="HuggingFace adityaswami89/Salesdata tabanlı CRM + MCP API",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": settings.MCP_SERVER_VERSION}


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/auth/keys", tags=["auth"])
async def new_api_key(body: ApiKeyCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    raw, record = await create_api_key(db, body.name, body.scopes, body.description or "")
    return {"key": raw, "id": record.id, "name": record.name}

@app.get("/auth/keys", tags=["auth"])
async def list_keys(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    from sqlalchemy import select
    from src.db.models import ApiKey
    rows = (await db.execute(select(ApiKey))).scalars().all()
    return [{"id": r.id, "name": r.name, "prefix": r.key_prefix, "status": r.status} for r in rows]


# ── Customers ─────────────────────────────────────────────────────────────────
@app.get("/customers", tags=["customers"])
async def list_customers(
    search:    Optional[str] = None,
    country:   Optional[str] = None,
    territory: Optional[str] = None,
    industry:  Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db), _=Depends(auth),
):
    rows = await CustomerService.list(db, skip, limit, search, country, territory, industry)
    return [CustomerOut.model_validate(r) for r in rows]

@app.get("/customers/analytics/territory", tags=["analytics"])
async def territory_stats(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await CustomerService.stats_by_territory(db)

@app.get("/customers/analytics/country", tags=["analytics"])
async def country_stats(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await CustomerService.stats_by_country(db)

@app.get("/customers/{cid}", tags=["customers"])
async def get_customer(cid: int, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await CustomerService.get(db, cid)
    if not r:
        raise HTTPException(404, "Not found")
    return CustomerOut.model_validate(r)

@app.post("/customers", tags=["customers"])
async def create_customer(body: CustomerCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await CustomerService.create(db, body.model_dump(exclude_none=True))
    return CustomerOut.model_validate(r)

@app.patch("/customers/{cid}", tags=["customers"])
async def update_customer(cid: int, body: CustomerUpdate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await CustomerService.update(db, cid, body.model_dump(exclude_none=True))
    if not r:
        raise HTTPException(404, "Not found")
    return CustomerOut.model_validate(r)


# ── Deals ─────────────────────────────────────────────────────────────────────
@app.get("/deals", tags=["deals"])
async def list_deals(
    customer_id:  Optional[int] = None,
    status:       Optional[str] = None,
    product_line: Optional[str] = None,
    deal_size:    Optional[str] = None,
    order_year:   Optional[int] = None,
    quarter:      Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db), _=Depends(auth),
):
    rows = await DealService.list(db, skip, limit, customer_id, status, product_line, deal_size, order_year, quarter)
    return [DealOut.model_validate(r) for r in rows]

@app.get("/deals/analytics/pipeline",      tags=["analytics"])
async def pipeline(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await DealService.pipeline_summary(db)

@app.get("/deals/analytics/product-line",  tags=["analytics"])
async def by_product_line(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await DealService.stats_by_product_line(db)

@app.get("/deals/analytics/deal-size",     tags=["analytics"])
async def by_deal_size(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await DealService.stats_by_deal_size(db)

@app.get("/deals/analytics/timeline",      tags=["analytics"])
async def by_timeline(db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await DealService.stats_by_year_quarter(db)

@app.get("/deals/analytics/top-customers", tags=["analytics"])
async def top_customers(limit: int = 10, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return await DealService.top_customers(db, limit)

@app.get("/deals/{did}", tags=["deals"])
async def get_deal(did: int, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await DealService.get(db, did)
    if not r:
        raise HTTPException(404, "Not found")
    return DealOut.model_validate(r)

@app.post("/deals", tags=["deals"])
async def create_deal(body: DealCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await DealService.create(db, body.model_dump(exclude_none=True))
    return DealOut.model_validate(r)

@app.patch("/deals/{did}", tags=["deals"])
async def update_deal(did: int, body: DealUpdate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await DealService.update(db, did, body.model_dump(exclude_none=True))
    if not r:
        raise HTTPException(404, "Not found")
    return DealOut.model_validate(r)


# ── Contacts ──────────────────────────────────────────────────────────────────
@app.get("/customers/{cid}/contacts", tags=["contacts"])
async def list_contacts(cid: int, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return [ContactOut.model_validate(r) for r in await ContactService.list(db, cid)]

@app.post("/contacts", tags=["contacts"])
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await ContactService.create(db, body.model_dump(exclude_none=True))
    return ContactOut.model_validate(r)


# ── Tasks ─────────────────────────────────────────────────────────────────────
@app.get("/deals/{did}/tasks", tags=["tasks"])
async def list_tasks(did: int, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    return [TaskOut.model_validate(r) for r in await TaskService.list(db, did)]

@app.post("/tasks", tags=["tasks"])
async def create_task(body: TaskCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await TaskService.create(db, body.model_dump(exclude_none=True))
    return TaskOut.model_validate(r)


# ── Activities ────────────────────────────────────────────────────────────────
@app.get("/activities", tags=["activities"])
async def list_activities(
    customer_id: Optional[int] = None,
    deal_id:     Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db), _=Depends(auth),
):
    return [ActivityOut.model_validate(r) for r in await ActivityService.list(db, customer_id, deal_id, limit)]

@app.post("/activities", tags=["activities"])
async def create_activity(body: ActivityCreate, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    r = await ActivityService.create(db, body.model_dump(exclude_none=True))
    return ActivityOut.model_validate(r)


# ── MCP ───────────────────────────────────────────────────────────────────────
@app.get("/mcp/info", tags=["mcp"])
async def mcp_info():
    return {"name": settings.MCP_SERVER_NAME, "version": settings.MCP_SERVER_VERSION, "tools": len(TOOLS)}

@app.post("/mcp/http", tags=["mcp"])
async def mcp_http(request: Request, db: AsyncSession = Depends(get_db), _=Depends(auth)):
    body = await request.json()
    method = body.get("method", "")
    params = body.get("params", {})
    result = await mcp_handle(method, params, db)
    return {"jsonrpc": "2.0", "id": body.get("id"), "result": result}


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)
