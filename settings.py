import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_KEY = os.getenv('FORA_AI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Live DB settings
DB_USER=os.getenv('DB_USER')
DB_HOST=os.getenv('DB_HOST')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_PORT=os.getenv('DB_PORT', '5432')
DB=os.getenv('DB', 'fora')

# Test DB settings
TEST_DB_NAME = 'fora_test_db'
TEST_DB_USER = os.getenv('TEST_DB_USER', 'fora_test')
TEST_DB_PASSWORD = os.getenv('TEST_DB_PASSWORD', 'fora_test')
TEST_DB_HOST = os.getenv('TEST_DB_HOST', 'localhost')
TEST_DB_PORT = os.getenv('TEST_DB_PORT', '5432')


def validate_environment():
    if not API_KEY:
        raise ValueError('Error on startup: FORA_AI_API_KEY credential not set.')
    print('FORA_AI_API_KEY configured')
        
    
    if not OPENAI_API_KEY:
        raise ValueError('Error on startup: OPENAI_API_KEY credential not set.')
    print('OPENAI_API_KEY configured')
        
    
    if not DB_USER or not DB_HOST or not DB_PASSWORD:
        raise ValueError('Error on startup: DB credentials not set.')
    print('DB credentials configured')

    if not TEST_DB_USER or not TEST_DB_HOST or not TEST_DB_PASSWORD:
        print('Warning on startup: TEST_DB credentials not configured.')
