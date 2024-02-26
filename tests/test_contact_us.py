from app import mongo
from . import get_api_header


def get_contact_request():
    return {
        'email': 'test@test.com',
        'tel': '82-1012341234',
        'report_type': 0,
        'report_content': 'test contact'
    }


def test_right_case(client, flask_app, auth):
    auth.register()
    response = client.post('/contact-us',
                           headers=get_api_header(),
                           json=get_contact_request())
    assert response.status_code == 201
