import uuid
import pytest
import logfire
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app
from settings import API_KEY

@pytest.fixture
def test_client():
    logfire.configure(send_to_logfire = False)
    client = TestClient(app, headers = {'Authorization': f'Bearer {API_KEY}'})
    return client

VALID_SUMMARIES_REQUEST = {
    "entity_id": str(uuid.uuid4()),
    "entity_name": "Test Hotel",
    "source_type": "client_supplier_reviews",
    "sources": [
        {
            "id": str(uuid.uuid4()),
            "review": "Great service and clean rooms"
        },
        {
            "id": str(uuid.uuid4()),
            "review": "Excellent location and friendly staff"
        },
        {
            "id": str(uuid.uuid4()),
            "review": "Good value for money, would recommend"
        }
    ]
}

INVALID_SUMMARIES_REQUEST = {
    "entity_id": "invalid-uuid",
    "entity_name": "Test Hotel",
    "source_type": "client_supplier_reviews",
    "sources": [
        {
            "id": str(uuid.uuid4()),
            "review": "Great service"
        }
    ]
}

@pytest.fixture
def mock_http_client():
    logfire.configure(send_to_logfire = False)
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'status': 'success'})
        
        mock_session_instance = AsyncMock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session_instance.__aexit__ = AsyncMock(return_value=None)
        
        mock_session.return_value = mock_session_instance
        yield mock_session_instance

def test__summaries__successful_post_request(test_client):
    logfire.configure(send_to_logfire = False)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'status': 'success'})
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    mock_session = AsyncMock()
    mock_session.post = MagicMock(return_value=mock_response)
    
    with patch('aiohttp.ClientSession') as mock_client_session, patch('core.summaries.summaries.logfire'):
        mock_client_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_client_session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('core.summaries.summaries.Summaries') as mock_summaries_class:
            mock_summaries_instance = MagicMock()
            mock_summaries_class.return_value = mock_summaries_instance
            
            response = test_client.post('/v1/summaries/', json=VALID_SUMMARIES_REQUEST)
            
            assert response.status_code == 200
            data = response.json()
            assert 'status' in data
            assert VALID_SUMMARIES_REQUEST['entity_id'] in data['status']
            assert 'recieved' in data['status']


def test__summaries__invalid_data(test_client):
    logfire.configure(send_to_logfire = False)
    response = test_client.post("/v1/summaries/", json=INVALID_SUMMARIES_REQUEST)
    
    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert len(error_detail) > 0

@patch('aiohttp.ClientSession')
def test__summaries_post__exception(mock_client_session, test_client):
    logfire.configure(send_to_logfire = False)
    mock_session = MagicMock()
    mock_client_session.return_value.__aenter__.return_value = mock_session
    mock_client_session.return_value.__aexit__.return_value = None
    
    with patch('app.v1.routes.summaries.Summaries') as mock_summaries_class:
        mock_summaries_class.side_effect = Exception('Database connection failed')
        
        response = test_client.post('/v1/summaries/', json=VALID_SUMMARIES_REQUEST)
        
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert 'Database connection failed' in data['detail']

@patch('aiohttp.ClientSession')
@patch('app.v1.routes.summaries.Summaries')
def test__summaries__background_task_started_successfully(mock_summaries_class, mock_client_session, test_client, monkeypatch):
    logfire.configure(send_to_logfire = False)
    mock_session = MagicMock()
    mock_client_session.return_value.__aenter__.return_value = mock_session
    mock_client_session.return_value.__aexit__.return_value = None
    
    mock_summaries_instance = MagicMock()
    mock_summaries_instance.generate = MagicMock()
    mock_summaries_class.return_value = mock_summaries_instance
    background_tasks_calls = []
    from fastapi import BackgroundTasks
    original_add_task = BackgroundTasks.add_task
    
    def track_add_task(self, func, *args, **kwargs):
        logfire.configure(send_to_logfire = False)
        background_tasks_calls.append((func, args, kwargs))
        return None
    
    monkeypatch.setattr(BackgroundTasks, 'add_task', track_add_task)
    response = test_client.post('/v1/summaries/', json=VALID_SUMMARIES_REQUEST)
    assert response.status_code == 200
    mock_summaries_class.assert_called_once()
    assert len(background_tasks_calls) == 1
    task_func, task_args, task_kwargs = background_tasks_calls[0]
    assert task_func == mock_summaries_instance.generate
    assert len(task_args) == 1
    request_arg = task_args[0]
    assert str(request_arg.entity_id) == VALID_SUMMARIES_REQUEST['entity_id']
