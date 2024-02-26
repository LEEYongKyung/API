import pytest

from app import create_app, mongo
from tests import get_api_header
from tests.test_tos import get_tos_request


@pytest.fixture
def flask_app():
    """Create and configure a new app & db instance for each test."""
    app = create_app(config_name='testing')
    with app.app_context():
        mongo.cx.drop_database(app.config['MONGO_DB_NAME'])

    yield app
    with app.app_context():
        mongo.cx.drop_database(app.config['MONGO_DB_NAME'])


@pytest.fixture
def client(flask_app):
    """A test client for the app."""
    return flask_app.test_client()


@pytest.fixture
def runner(flask_app):
    """A test runner for the app's Click commands."""
    return flask_app.test_cli_runner()


class AuthAction(object):
    def __init__(self, flask_client):
        self._client = flask_client

    def register(self, token='test'):
        return self._client.post('/terms-of-service',
                                 headers=get_api_header(token=token),
                                 json=get_tos_request(auth=True))


@pytest.fixture
def auth(client):
    return AuthAction(client)
