import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
import psycopg2
from app.main import app
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from llms.factory import LLMFetcher
from core.content_enrichment import (
    ContentEnrichmentRequest, GenerateContext, RewriteContext
)
from settings import (
    API_KEY, TEST_DB_NAME, TEST_DB_USER,
    TEST_DB_PASSWORD, TEST_DB_HOST, TEST_DB_PORT,
    DB_USER, DB_PASSWORD
)
from db import get_db


TEST_DB_URL = (
    f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}"
    f"@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)

def create_test_db():
    """Create test database if it doesn't exist"""
    # Connect to default database to create test database
    conn = psycopg2.connect(
        dbname="postgres",
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        host=TEST_DB_HOST,
        port=TEST_DB_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,))
    exists = cur.fetchone()
    
    if not exists:
        cur.execute(f'CREATE DATABASE {TEST_DB_NAME}')
    
    cur.close()
    conn.close()

def run_migrations():
    """Run alembic migrations on test database"""
    alembic_cfg = Config("alembic.ini")
    # Override the database URL in the Alembic config
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    # Override the import of DATABASE_URL in env.py
    import db
    db.DATABASE_URL = TEST_DB_URL
    command.upgrade(alembic_cfg, "head")

@pytest.fixture(scope="session", autouse=True)
def setup_test_db(request):
    """Create test database and run migrations"""
    create_test_db()
    run_migrations()
    
    def cleanup():
        # Clean up test database after all tests
        # First, close the SQLAlchemy engine to release all connections
        engine.dispose()
        
        # Then connect to postgres to drop the test database
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=TEST_DB_HOST,
            port=TEST_DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Terminate all connections to the test database
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
            AND pid <> pg_backend_pid()
        """)
        
        # Now drop the database
        cur.execute(f'DROP DATABASE IF EXISTS {TEST_DB_NAME}')
        cur.close()
        conn.close()
    
    # Register the cleanup function to run after all tests
    request.addfinalizer(cleanup)

# Create test database engine
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Fixture to provide a test database session"""
    # Create a new session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def mock_llm_response():
    """Mock LLM response fixture"""
    mock = MagicMock()
    mock.output_text = "Test generated content"
    mock.model = "gpt-4.1-mini"
    mock.usage = MagicMock()
    mock.usage.input_tokens = 1000000  # this costs $0.40
    mock.usage.output_tokens = 1000  # this costs $0.0016
    mock.usage.total_tokens = 1001000
    mock.usage.input_tokens_details = MagicMock()
    mock.usage.input_tokens_details.cached_tokens = 0
    mock.usage.output_tokens_details = MagicMock()
    mock.usage.output_tokens_details.reasoning_tokens = 0
    mock.cost = 0.4016
    return mock

@pytest.fixture(autouse=True)
def mock_llm_fetcher(mock_llm_response):
    """
    Replace the LLMFetcher *inside the real ContentGenerator module*.
    """
    cg_module = sys.modules['core.content_enrichment.ContentGenerator']
    with patch.object(cg_module, 'LLMFetcher') as mock_cls:
        mock_instance = MagicMock(spec=LLMFetcher)
        mock_instance.model = 'gpt-4.1-mini'

        mock_instance.async_client = MagicMock()
        mock_instance.async_client.responses = AsyncMock()
        mock_instance.async_client.responses.create.return_value = mock_llm_response

        mock_cls.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def test_client(test_db):
    """Fixture to provide a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create client with default headers including Authorization
    client = TestClient(app, headers={"Authorization": f"Bearer {API_KEY}"})
    return client

# Test request fixtures
@pytest.fixture
def generate_request_html():
    """Fixture for generate request with HTML output"""
    return ContentEnrichmentRequest(
        metadata={"block_id": "test-block"},
        output_format="html",
        generate=GenerateContext(
            user_instructions="Test instructions"
        )
    )

@pytest.fixture
def generate_request_text():
    """Fixture for generate request with text output"""
    return ContentEnrichmentRequest(
        metadata={"block_id": "test-block"},
        output_format="text",
        generate=GenerateContext(
            user_instructions="Test instructions"
        )
    )

@pytest.fixture
def generate_with_existing_html():
    """Fixture for generate request with existing text and HTML output"""
    return ContentEnrichmentRequest(
        metadata={"block_id": "test-block"},
        output_format="html",
        generate=GenerateContext(
            user_instructions="Test instructions",
            existing_text="Existing content"
        )
    )

@pytest.fixture
def elaborate_request_html():
    """Fixture for elaborate request with HTML output"""
    return ContentEnrichmentRequest(
        metadata={"block_id": "test-block"},
        output_format="html",
        elaborate=RewriteContext(
            existing_text="Existing content"
        )
    )

@pytest.fixture
def change_tone_request_html():
    """Fixture for change tone request with HTML output"""
    return ContentEnrichmentRequest(
        metadata={"block_id": "test-block"},
        output_format="html",
        change_my_tone=RewriteContext(
            existing_text="Existing content",
            tone="sophisticated"
        )
    ) 