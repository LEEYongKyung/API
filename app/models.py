from datetime import datetime

from app import mongo


class User:
    @staticmethod
    def from_json(json_request, json_headers):
        return {
            'model': json_request.get('model'),
            'os_type': json_request.get('os_type'),
            'os_ver': json_request.get('os_ver'),
            'app_type': json_request.get('app_type'),
            'app_ver': json_request.get('app_ver'),
            'language': json_request.get('language'),
            'token': json_headers.get('token'),

            'tos': True,
            'is_black': False,
            'certifications': [],
            'reports': [],
            'contacts': []
        }

    @staticmethod
    def update_cert(token, cert_id):
        mongo.db.users.update({'token': token},
                              {'$push': {'certifications': cert_id}})

    @staticmethod
    def is_not_allowed(token):
        user = mongo.db.users.find_one({"token": token})
        if user:
            if user['tos']:
                return False
        return True


class Certification:
    db = None

    @classmethod
    def from_json(cls, json_request, token, date):
        json_certification = {
            "random_num": json_request.get('random_num'),
            "count": 1,
            "list": [cls.get_single(json_request, token, date)]
        }
        return json_certification

    @staticmethod
    def get_single(json_request, token, date, result=True):
        return {
            "company": json_request.get('random_num'),
            "token": token,
            "result": result,
            "photo_url": get_photo_url(json_request.get('photo')),
            "gps_type": json_request.get('gps_type'),
            "latitude": json_request.get('latitude'),
            "longitude": json_request.get('longitude'),
            "address": get_address(json_request.get('latitude'), json_request.get('longitude')),
            "data": date
        }

    @classmethod
    def update_fake(cls, json_request, token, date):
        # TODO: 난수 중복 확인하여 새로 추가 혹은 기존 난수에 추가
        mongo.db.certifications.update({'random_num': json_request.get('random_num')},
                                       {'$inc': {'count': 1},
                                        '$push': {'list': cls.get_single(json_request, token, date,
                                                                         result=False)}})

    @classmethod
    def update_single(cls, json_request, token, date):
        mongo.db.certifications.update({'random_num': json_request.get('random_num')},
                                       {'$inc': {'count': 1},
                                        '$push': {'list': cls.get_single(json_request, token, date,
                                                                         result=False)}})

    @staticmethod
    def is_fake(cert, token):
        """
        인증 정보가 없을 경우 -> False
        인증 정보가 있고, 처음으로 인증한 유저가 인증한 경우 -> False
        인증 정보가 있으나, 첫 인증 유저와 다른 유저가 인증하였을 경우 -> True
        """
        # TODO: Random num가 생성 난수 범위 안에 들어가는지 확인 필요
        if cert is None:
            return False
        return cert['list'][0]['token'] != token


def get_company(random_num):
    return 'company'


def get_photo_url(photo):
    return 'photo_url'


def get_address(latitude, longitude):
    return 'address'


class Report:
    @staticmethod
    def from_json(json_request, token, date):
        random_num = json_request.get('random_num')
        cert = mongo.db.certifications.find_one({'random_num': random_num}).get('list')[0]
        return {
            "random_num": random_num,
            "auth_date": json_request.get('authenticity_date'),
            "company": cert.get('company'),
            "token": token,
            "result": cert.get('result'),
            "photo_url": cert.get('photo_url'),
            "gps_type": cert.get('gps_type'),
            "latitude": cert.get('latitude'),
            "longitude": cert.get('longitude'),
            "email": json_request.get('email'),
            "tel": json_request.get('tel'),
            "report_content": json_request.get('report_content'),
            "confirm": False,
            "date": date
        }


class Contact:
    @staticmethod
    def from_json(json_request, token, date):
        return {
            "token": token,
            "email": json_request.get('email'),
            "tel": json_request.get('tel'),
            "report_type": json_request.get('report_type'),
            "report_content": json_request.get('report_content'),
            "confirm": False,
            "date": date
        }
