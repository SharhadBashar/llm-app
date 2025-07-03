from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from settings import API_KEY

api_key_header = APIKeyHeader(name = 'Authorization', auto_error=False)

async def verify_api_key(request: Request, call_next):
    '''
        Middleware to verify the API key in the Authorization header.
        Expected format: Authorization: Bearer {API_KEY}
    '''
    # Skip auth for health check endpoints 
    if request.url.path in ['/', '/status']:
        return await call_next(request)
    
    token = await api_key_header(request)

    if not token:
        return JSONResponse(
            status_code = status.HTTP_401_UNAUTHORIZED,
            content = {'detail': 'Missing Authorization header'}
        )
    
    if token != f'Bearer {API_KEY}':
        return JSONResponse(
            status_code = status.HTTP_401_UNAUTHORIZED,
            content = {'detail': 'Invalid API key'}
        )
    
    return await call_next(request)
