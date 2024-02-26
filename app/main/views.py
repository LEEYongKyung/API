from datetime import datetime

from flask import request, jsonify

from app import mongo
from . import main
from .errors import bad_request, unauthorized
from ..models import User, Certification as Cert, Report, Contact

from werkzeug.security import generate_password_hash, check_password_hash

@main.route('/generate_password', methods=['POST'])
def generate_password():
    pass_word = request.json.get("password")
    return jsonify({'generate_password': generate_password_hash(pass_word)})

@main.route('/terms-of-service', methods=['POST'])
def tos():    
    # filter wrong parameter
    auth = request.json.get("auth") or None
    if auth is None or auth is False:
        return bad_request('Auth variable is invalid.')

    # filter duplicated user
    user = mongo.db.users.find_one({'token': request.headers.get('token', None)})
    if user is not None:
        return bad_request('User is already exist.')

    user = User.from_json(request.json, request.headers)
    mongo.db.users.insert_one(user)
    return jsonify({'status': 201}), 201


@main.route('/authenticity', methods=['POST'])
def authenticity():
    token = request.headers['token']
    if User.is_not_allowed(token):
        return unauthorized('User is not exist or user is not agree to terms-of-service.')

    date = datetime.utcnow()
    random_num = request.json.get('random_num')
    response = {"status": 201,
                "date": date}

    cert = mongo.db.certifications.find_one({'random_num': random_num})
    if Cert.is_fake(cert=cert, token=token):
        response['result'] = False
        response['result_msg'] = '가품입니다.'
        cert_id = cert['_id']
        Cert.update_fake(json_request=request.json, token=token, date=date)
    else:
        response['result'] = True
        response['result_msg'] = '진품입니다.'
        if cert is None:
            # 첫 인증하였을 경우
            certification = Cert.from_json(json_request=request.json, token=token, date=date)
            cert_id = mongo.db.certifications.insert_one(certification).inserted_id
        else:
            # 동일 유저가 중복 인증하였을 경우
            cert_id = cert['_id']
            Cert.update_single(json_request=request.json, token=token, date=date)
    User.update_cert(token=token, cert_id=cert_id)
    return jsonify(response), 201


@main.route('/report-fake', methods=['POST'])
def report_fake():
    token = request.headers['token']
    if User.is_not_allowed(token):
        return unauthorized('User is not exist or user is not agree to terms-of-service.')

    cert = mongo.db.certifications.find_one({'random_num': request.json.get('random_num')})
    if cert is None:
        return bad_request('Certification is not exist in this random_num.')

    date = datetime.utcnow()
    report = Report.from_json(json_request=request.json, token=token, date=date)
    mongo.db.reports.insert_one(report)
    # TODO: user Update
    return jsonify({'status': 201, 'date': date}), 201


@main.route('/contact-us', methods=['POST'])
def contact_us():
    token = request.headers['token']
    if User.is_not_allowed(token):
        return unauthorized('User is not exist or user is not agree to terms-of-service.')

    date = datetime.utcnow()
    contact = Contact.from_json(json_request=request.json, token=token, date=date)
    mongo.db.contacts.insert_one(contact)
    # TODO: user Update
    return jsonify({'status': 201, 'date': contact['date']}), 201
