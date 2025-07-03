from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import psycopg2
import time
import json
import logging
from datetime import datetime, timezone

from core.content_enrichment import (
    ContentEnrichmentRequest, ParsedContentEnrichmentResponse,
    Function, ContentEnrichmentResponse,
    ContentGenerator
)

from db import get_db, BaseDBOperations

logger = logging.getLogger(__name__)

content_enrichment_router = APIRouter()
content_db = BaseDBOperations(ContentEnrichmentResponse)

@content_enrichment_router.post("/", response_model=ParsedContentEnrichmentResponse)
async def content_enrichment(
    request: ContentEnrichmentRequest,
    db: Session = Depends(get_db)
):
    try:
        request_uuid = uuid.uuid4()
        function_key, context = request.get_function_data()
        
        # Log input data
        context_data = context.model_dump()
        # Truncate long text fields
        if context_data.get('existing_text'):
            context_data['existing_text'] = context_data['existing_text'][:200] + "..." if len(context_data['existing_text']) > 200 else context_data['existing_text']
        if context_data.get('user_instructions'):
            context_data['user_instructions'] = context_data['user_instructions'][:200] + "..." if len(context_data['user_instructions']) > 200 else context_data['user_instructions']
        
        logger.info(f"{request_uuid}, [INPUT] Function: {function_key}, Metadata: {json.dumps(request.metadata)}, Output Format: {request.output_format}, Context: {json.dumps(context_data)}")

        start_time = time.time()
        
        # Handle all business logic
        generator = ContentGenerator(request)
        response, model, cost = await generator.generate()

        # Escape new lines and truncate response for logging
        response_preview = response[:300] + "..." if len(response) > 300 else response
        response_preview_clean = response_preview.strip().replace('\n', '\\n')
        logger.info(f"{request_uuid}, [OUTPUT]: {response_preview_clean}")

        # Calculate latency in milliseconds
        generation_time = time.time()
        latency_ms = int((generation_time - start_time) * 1000)

        # Store everything - passing the enum value (lowercase) instead of the enum itself
        stored_content = content_db.create(db, {
            "content_metadata": request.metadata,
            "function": generator.function_key,
            "tone": generator.context.tone,
            "user_instructions": generator.context.user_instructions,
            "existing_text": generator.context.existing_text,
            "ai_response": response,
            "output_format": generator.output_format,
            "ai_model": model,
            "latency_ms": latency_ms,
            "cost_usd": cost
        })

        return ParsedContentEnrichmentResponse(
            id=str(stored_content.id),
            text=stored_content.ai_response
        )
    except ValueError as e:
        logger.exception(f"{request_uuid}, ValueError occurred")
        raise HTTPException(status_code=400, detail=f"{request_uuid}, {str(e)}")
    except (psycopg2.errors.InvalidTextRepresentation) as e:
        logger.exception(f"{request_uuid}, Invalid enum value error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"{request_uuid}, Invalid function value: {generator.function_key}. Valid values are: {', '.join([f.value for f in Function])}"
        )
    except Exception as e:
        logger.exception(f"{request_uuid}, Error in /v1/content-enrichment endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"{request_uuid}, Content enrichment failed")

@content_enrichment_router.post("/{content_id}/accept")
async def accept_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Mark a piece of generated content as accepted by setting accepted_at to the current time.
    
    Args:
        content_id: UUID of the content to accept
        db: Database session
        
    Returns:
        The updated content object
    """
    try:
        request_uuid = uuid.uuid4()
        logger.info(f"{request_uuid}, [INPUT] Accept Content ID: {content_id}")
        
        # Get the content
        content = content_db.get(db, content_id)
        if not content:
            logger.exception(f"{request_uuid}, Content not found: {content_id}")
            raise HTTPException(
                status_code=404,
                detail=f"{request_uuid}, Content with ID {content_id} not found"
            )

        # Update accepted_at
        updated_content = content_db.update(db, content.id, {
            "accepted_at": datetime.now(timezone.utc)
        })
        if not updated_content:
            logger.exception(f"{request_uuid}, Content update failed: {content.id}")
            raise HTTPException(
                status_code=404,
                detail=f"{request_uuid}, Couldn't update enriched content with ID {content.id}, because it was not found"
            )

        logger.info(f"{request_uuid}, [ACCEPTED]: {updated_content.id} at {updated_content.accepted_at}")
        
        return {
            "id": str(updated_content.id),
            "accepted_at": updated_content.accepted_at
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions without wrapping them in 500
        logger.exception(f"{request_uuid}, Re-raising HTTPException from accept_content: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        db.rollback()
        logger.exception(f"{request_uuid}, Error type: {type(e)}, Error accepting content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to accept content"
        )