from fastapi import APIRouter

from app.v1.docs.hanlders import docs_router
from app.v1.security.handlers import security_router

own_router_v1 = APIRouter()
own_router_v1.include_router(security_router, tags=['Security'])
own_router_v1.include_router(docs_router, tags=['Docs'])
