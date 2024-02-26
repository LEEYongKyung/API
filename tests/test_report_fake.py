from app import mongo
from . import get_api_header
from .test_authenticity import get_auth_request


def get_report_request(**kwargs):
    req = {
        'random_num': -1,
        'authenticity_date': '',
        'email': 'test@test.com',
        'tel': '82-1012341234',
        'report_content': 'test report fake'
    }
    for key, value in kwargs.items():
        req[key] = value
    return req


def test_right_case(client, flask_app, auth):
    auth.register()
    response = client.post('/authenticity',
                           headers=get_api_header(),
                           json=get_auth_request(random_num='1234'))
    date = response.json['date']
    response = client.post('/report-fake',
                           headers=get_api_header(),
                           json=get_report_request(random_num='1234', authenticity_date=date))
    assert response.status_code == 201
    with flask_app.app_context():
        report = mongo.db.reports.find_one({'token': 'test'})
        assert report.get('auth_date') == date


def test_wrong_case(client, auth):
    # user without register
    response = client.post('/report-fake',
                           headers=get_api_header(),
                           json=get_auth_request(random_num='1234'))
    assert response.status_code == 401
    assert 'User is not exist or user is not agree to terms-of-service.' in response.json['message']

    auth.register()
    # random_number does not exist in certification
    response = client.post('/report-fake',
                           headers=get_api_header(),
                           json=get_auth_request(random_num='4321'))
    assert response.status_code == 400
    assert 'Certification is not exist in this random_num.' in response.json['message']
