from core.content_enrichment.models import (
    ContentEnrichmentResponse,
    Function,
    OutputFormat,
)
from core.summaries.models import Summaries
from core.summaries.types import Source_Type

'''
    The following list of models are exported for use through Alembic.
    Alembic will read the models here to the latest migration file to create new migration files.
    Add your model here when you are ready to run the revision and generate the migration file.
    - First create a list with all the models and types you want to import.
    - Then add the list to the __all__ variable.
'''

content_enrichment_models = [
    ContentEnrichmentResponse,
    Function,
    OutputFormat
]

summaries_models = [
    Summaries,
    Source_Type
]

__all__ = [
    *content_enrichment_models,
    *summaries_models
]
