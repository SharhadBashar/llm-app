from fastapi import APIRouter, HTTPException, BackgroundTasks

from core.summaries.summaries import Summaries
from core.summaries.serializers import Summaries_Request

summaries_router = APIRouter()

@summaries_router.post('/')
async def summaries(request: Summaries_Request, background_tasks: BackgroundTasks):
    try:
        summaries = Summaries()
        background_tasks.add_task(summaries.generate, request)
        return {'status': f'Reviews for supplier: {request.entity_id} recieved.'}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
