from app import mongo

from . import get_api_header


def get_tos_request(**kwargs):
    req = {
        "model": "iPhone6S",
        "os_type": "iOS",
        "os_ver": "9.7.2",
        "app_type": "ARCI199999",
        "app_ver": "01.00.01",
        "language": "KO",
    }
    for key, value in kwargs.items():
        req[key] = value
    return req


def test_right_case(client, flask_app):
    response = client.post('/terms-of-service',
                           headers=get_api_header(),
                           json=get_tos_request(auth=True))
    assert response.status_code == 201

    with flask_app.app_context():
        user = mongo.db.users.find_one({"token": "test"})
        assert user['model'] == 'iPhone6S'


def test_wrong_cases(client, flask_app):
    # send wrong parameter
    response = client.post('/terms-of-service',
                           headers=get_api_header(),
                           json=get_tos_request(wrong=True))
    assert 'Auth variable is invalid' in response.json['message']

    # send invalid parameter
    response = client.post('/terms-of-service',
                           headers=get_api_header(),
                           json=get_tos_request(auth=False))
    assert 'Auth variable is invalid' in response.json['message']

    # send duplicated parameter
    test_right_case(client, flask_app)
    response = client.post('/terms-of-service',
                           headers=get_api_header(),
                           json=get_tos_request(auth=True))
    assert 'User is already exist' in response.json['message']
