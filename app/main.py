import logging
import logging.config
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from core.custom_exceptions import validation_exception_handler
from app.api import api_router
from app.middleware.auth import verify_api_key
from settings import validate_environment

# Custom filter class to only allow INFO level logs
class InfoOnlyFilter:
    def filter(self, record):
        """Only allow INFO level logs to pass through"""
        return record.levelno == logging.INFO

# Use dictConfig for cleaner logging setup
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
            'formatter': 'default',
            'filters': ['info_only'],  # Only let INFO logs through to stdout
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'level': 'WARNING',
            'formatter': 'default',
        },
    },
    'filters': {
        'info_only': {
            # Custom filter that only allows INFO level logs to pass through
            # This prevents INFO logs from also going to stderr handler
            '()': InfoOnlyFilter,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['stdout', 'stderr'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

validate_environment()

app = FastAPI()

# Add middleware
app.middleware('http')(verify_api_key)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)

@app.get('/')
async def root():
    return {'message': 'Welcome to Fora AI V2'}

@app.get('/status')
async def status():
    return {'message': 'Fora AI V2 is up and running 😊'}
