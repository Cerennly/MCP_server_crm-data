from __future__ import annotations
import hashlib, os, secrets, sys
from datetime import datetime
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import ApiKey, ApiKeyStatus
from config.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query  = APIKeyQuery(name="api_key",    auto_error=False)

def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def generate_key() -> str:
    return settings.API_KEY_PREFIX + secrets.token_urlsafe(32)

async def get_api_key(
    db: AsyncSession,
    header_key: Optional[str] = None,
    query_key:  Optional[str] = None,
) -> ApiKey:
    raw = header_key or query_key
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")

    # Master key bypass
    if raw == settings.MASTER_API_KEY:
        return ApiKey(
            id=0, key_hash="master", key_prefix="master",
            name="Master", scopes='["*"]', status=ApiKeyStatus.ACTIVE,
        )

    result = await db.execute(select(ApiKey).where(ApiKey.key_hash == _hash(raw)))
    api_key = result.scalar_one_or_none()

    if not api_key or api_key.status != ApiKeyStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expired")

    api_key.last_used_at = datetime.utcnow()
    return api_key

def has_scope(api_key: ApiKey, required: str) -> bool:
    import json
    if not api_key.scopes:
        return False
    scopes = json.loads(api_key.scopes)
    return "*" in scopes or required in scopes

async def create_api_key(db: AsyncSession, name: str, scopes: list, description: str = "") -> tuple[str, ApiKey]:
    raw = generate_key()
    record = ApiKey(
        key_hash=_hash(raw), key_prefix=raw[:12],
        name=name, description=description,
        scopes=__import__("json").dumps(scopes),
        status=ApiKeyStatus.ACTIVE,
    )
    db.add(record)
    await db.flush()
    return raw, record
