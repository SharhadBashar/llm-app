import uuid
from core.content_enrichment.models import Function

# Test data
VALID_GENERATE_REQUEST = {
    "metadata": {"block_id": "test-block"},
    "output_format": "html",
    "generate": {
        "user_instructions": "Write a test paragraph"
    }
}

INVALID_FUNCTION_REQUEST = {
    "metadata": {"block_id": "test-block"},
    "output_format": "html",
    "invalid_function": {
        "user_instructions": "Write a test paragraph"
    }
}

MISSING_REQUIRED_FIELD_REQUEST = {
    "metadata": {"block_id": "test-block"},
    "output_format": "html",
    "generate": {
        # Missing user_instructions
    }
}

def test_create_content_success(test_client, mock_llm_fetcher, mock_llm_response):
    """Test successful content creation"""
    print(test_client.headers)
    response = test_client.post("/v1/content-enrichment/", json=VALID_GENERATE_REQUEST)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "text" in data
    assert data["text"] == "Test generated content"
    assert isinstance(data["id"], str)

def test_create_content_invalid_function(test_client, mock_llm_fetcher, mock_llm_response):
    """Test content creation with invalid function"""
    response = test_client.post("/v1/content-enrichment/", json=INVALID_FUNCTION_REQUEST)
    assert response.status_code == 400
    
    # Check that the error message contains the key part without strict ordering
    error_detail = response.json()["detail"]
    assert "Request must have exactly one function key from" in error_detail
    
    # Check that all function values are mentioned in the error message
    for f_value in [f.value for f in Function]:
        assert f_value in error_detail

def test_create_content_missing_required_field(test_client, mock_llm_fetcher, mock_llm_response):
    """Test content creation with missing required field"""
    response = test_client.post("/v1/content-enrichment/", json=MISSING_REQUIRED_FIELD_REQUEST)
    assert response.status_code == 400
    assert "Invalid request: Missing required field: user_instructions" in response.json()["detail"]

def test_accept_content_success(test_client, test_db, mock_llm_fetcher, mock_llm_response):
    """Test successful content acceptance"""
    # First create some content
    create_response = test_client.post("/v1/content-enrichment/", json=VALID_GENERATE_REQUEST)
    content_id = create_response.json()["id"]
    print(content_id)
        
    # Then accept it
    accept_response = test_client.post(f"/v1/content-enrichment/{content_id}/accept")
    assert accept_response.status_code == 200
    data = accept_response.json()
    assert data["id"] == content_id
    assert "accepted_at" in data
    assert data["accepted_at"] is not None

def test_accept_content_not_found(test_client):
    """Test accepting non-existent content"""
    non_existent_id = str(uuid.uuid4())
    response = test_client.post(f"/v1/content-enrichment/{non_existent_id}/accept")
    assert response.status_code == 404
    assert f"Content with ID {non_existent_id} not found" in response.json()["detail"]
