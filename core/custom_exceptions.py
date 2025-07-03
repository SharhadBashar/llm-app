from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    '''Convert validation errors to 400 Bad Request with friendly messages'''
    missing_fields = []
    invalid_fields = []
    other_errors = []

    for error in exc.errors():
        if (error['type'] == 'missing'):
            missing_fields.append(error['loc'][-1])
        elif (error['type'] == 'value_error'):
            # For invalid function keys, just show the key name
            print(error)
            invalid_key = error['msg']
            invalid_fields.append(f'{invalid_key}')
        else:
            other_errors.append(error['msg'])
    
    error_messages = []
    
    if missing_fields:
        if (len(missing_fields) == 1):
            error_messages.append(f'Missing required field: {missing_fields[0]}')
        else:
            error_messages.append(f'Missing required fields: {", ".join(missing_fields)}')
    
    if invalid_fields:
        if (len(invalid_fields) == 1):
            error_messages.append(f'Invalid value: {invalid_fields[0]}')
        else:
            error_messages.append(f'Invalid values: {", ".join(invalid_fields)}')
    
    if other_errors:
        error_messages.extend(other_errors)
    
    return JSONResponse(
        status_code = 400,
        content = {'detail': 'Invalid request: ' + '; '.join(error_messages)}
    ) 
