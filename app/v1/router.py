from fastapi import APIRouter

from app.v1.routes.summaries import summaries_router
from app.v1.routes.content_enrichment import content_enrichment_router

v1_router = APIRouter()

v1_router.include_router(content_enrichment_router, prefix = '/content-enrichment', tags = ['Content Enrichment'])
v1_router.include_router(summaries_router, prefix = '/summaries', tags = ['Summaries'])
