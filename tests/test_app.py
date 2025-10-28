import pytest
from main import create_app
from unittest.mock import MagicMock
import io

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key" # Use a fixed secret key for tests
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_request_main_page(client):
    response = client.get("/")
    assert response.status_code == 200

def test_login_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'EMAIL_ADDRESS' in response.data
    assert b'PASSWORD_HASH' in response.data

def test_registration_page_as_admin(client, mocker):
    mocker.patch('jwt.decode', return_value={'email': 'admin@example.com'})
    mocker.patch('app.main.routes.db_connection.get_collection').return_value.find_one.return_value = {'email': 'admin@example.com', 'is_admin': True}
    
    response = client.get('/register', headers={'x-access-token': 'dummy_token'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'CREATE_USER' in response.data

def test_forgot_password_page(client):
    response = client.get('/forgot-password')
    assert response.status_code == 200
    assert b'EMAIL_ADDRESS' in response.data

def test_dashboard_unauthorized_access(client):
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 200
    # Check for the client-side redirect script rendered in the template
    assert b'window.location.href = "/";' in response.data

def test_dashboard_authorized_access(client, mocker):
    with client.session_transaction() as session:
        session['user'] = {'email': 'test@example.com', 'name': 'Test User'}

    mocker.patch('app.api.routes.db_connection.get_collection').return_value.find_one.return_value = {
        'email': 'test@example.com', 'name': 'Test User'
    }
    mocker.patch('jwt.decode', return_value={'email': 'test@example.com'})

    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'FILE_API_MANAGEMENT_SYSTEM.v2.1' in response.data

def test_get_user(client, mocker):
    mocker.patch('app.api.routes.db_connection.get_collection').return_value.find_one.return_value = {'email': 'test@example.com'}
    mocker.patch('jwt.decode', return_value={'email': 'test@example.com'})
    response = client.get('/api/user', headers={'x-access-token': 'dummy_token'})
    assert response.status_code == 200
    assert response.json == {'email': 'test@example.com'}

def test_upload_image(client, mocker):
    # Mock external dependencies
    mocker.patch('app.helpers.save_image_file').return_value = ('test_url', 'test_filename')
    mocker.patch('app.helpers.create_image_upload_record').return_value = None
    mocker.patch('app.api.routes.db_connection.get_collection').return_value.find_one.return_value = {'_id': 'test_id'}
    mocker.patch('jwt.decode', return_value={'email': 'test@example.com'})

    # Prepare the request with a dummy file
    data = {
        'application_type': 'test',
        'file': (io.BytesIO(b"dummy file content"), 'test.jpg')
    }

    response = client.post(
        '/api/upload/image', 
        data=data, 
        headers={'x-access-token': 'dummy_token'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    assert response.json['message'] == 'Image uploaded successfully'

def test_get_username(client):
    response = client.get('/api/generate-username')
    assert response.status_code == 200
    assert 'username' in response.json
