from app import mongo
from . import get_api_header


def get_auth_request(**kwargs):
    req = {
        'photo': None,
        'gps_type': 0,
        'latitude': 37.5572363,
        'longitude': 127.0431279,
        'random_num': 'should be added'
    }
    for key, value in kwargs.items():
        req[key] = value
    return req


def test_right_case(client, flask_app, auth):
    auth.register()
    response = client.post('/authenticity',
                           headers=get_api_header(),
                           json=get_auth_request(random_num='1234'))
    assert response.status_code == 201
    assert response.json.get('result') is True
    with flask_app.app_context():
        cert = mongo.db.certifications.find_one({'random_num': '1234'})
        assert cert.get('random_num') == '1234'
        assert cert.get('count') == 1
        assert cert.get('list')[0]['gps_type'] == 0


def test_wrong_cases(client, flask_app, auth):
    # user without register
    response = client.post('/authenticity',
                           headers=get_api_header(token='test_2'),
                           json=get_auth_request(random_num='1234'))
    assert response.status_code == 401
    assert 'User is not exist or user is not agree to terms-of-service.' in response.json['message']

    # filter duplicated authenticity with same user
    test_right_case(client, flask_app, auth)
    response = client.post('/authenticity',
                           headers=get_api_header(),
                           json=get_auth_request(random_num='1234'))
    assert response.json.get('result') is True
    with flask_app.app_context():
        cert = mongo.db.certifications.find_one({'random_num': '1234'})
        assert cert.get('count') == 2
        assert len(cert.get('list')) == 2
        user = mongo.db.users.find_one({'token': 'test'})
        assert len(user.get('certifications')) == 2

    # duplicated authenticity with different user
    auth.register(token='test_1')
    response = client.post('/authenticity',
                           headers=get_api_header(token='test_1'),
                           json=get_auth_request(random_num='1234'))
    assert response.status_code == 201
    assert response.json.get('result') is False
    with flask_app.app_context():
        cert = mongo.db.certifications.find_one({'random_num': '1234'})
        assert cert.get('count') == 3
        assert len(cert.get('list')) == 3
        assert cert.get('list')[2]['token'] == 'test_1'
        user = mongo.db.users.find_one({'token': 'test_1'})
        assert len(user.get('certifications')) == 1
