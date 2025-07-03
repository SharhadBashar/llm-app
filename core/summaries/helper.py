import os
from uuid import UUID

from core.summaries.types import Source, Source_Type

def extract_source_data(sources: list[Source]) -> tuple[list[UUID], list[str]]:
    ids = [source.id for source in sources]
    reviews = [source.review for source in sources]
    return ids, reviews

def get_backend_write_endpoint(entity_id: str, source_type: Source_Type):
    if (source_type == Source_Type.CLIENT_SUPPLIER_REVIEWS):
        return f'{os.environ.get("RESTRICTED_BASE_URL")}/v1/suppliers/{entity_id}/client-reviews/summary/'
    else:
        raise KeyError(f'{source_type} is not a valid source type.')
