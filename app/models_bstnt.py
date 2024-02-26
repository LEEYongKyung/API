# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime,Enum, ForeignKey, Index, Integer, SmallInteger, String, Text
from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Index, Integer, SmallInteger, String, Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Permission:
    VIEW = 1
    QUESTION = 2
    WRITE = 4
    ALL_MENU = 8
    ICRAFT_SUPER_ADMIN = 16

class TdAdmin(db.Model):
    __tablename__ = 'td_admin'

    idx = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(20), nullable=False, unique=True)
    pwd = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Integer, nullable=False, index=True)
    position = db.Column(db.String(20))
    department = db.Column(db.String(45))
    state = db.Column(Enum('Registered', 'Deleted', 'Paused'), nullable=False)
    registrant = db.Column(db.String(20))
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime, nullable=False)
    dtLastConnected = db.Column(db.DateTime)
    note = db.Column(db.Text)
    failCount = db.Column(db.SmallInteger, server_default=db.FetchedValue())

    def to_json(self):
        json_user = {
            'idx': self.idx,
            'id': self.id,
            'pwd': self.pwd,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'telephone': self.telephone,
            'role': self.role,
            'role_name': TcRole.query.filter_by(code=self.role).first().name_kr,
            'position': self.position,
            'department': self.department,
            'state': self.state,
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
            'dtLastConnected': self.dtLastConnected,
            'note': self.note,
            'failCount': self.failCount
        }
        return json_user

class TcRole(db.Model):
    __tablename__ = 'tc_role'
    __table_args__ = (
        db.Index('idx_tc_role_01', 'code', 'state'),
    )

    idx = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False)
    name_kr = db.Column(db.String(45), nullable=False)
    name_en = db.Column(db.String(45))
    name_zh = db.Column(db.String(45))
    name_kr_forAccount = db.Column(db.String(45))
    name_en_forAccount = db.Column(db.String(45))
    name_zh_forAccount = db.Column(db.String(45))
    state = db.Column(db.Enum('Registered', 'Deleted', 'Paused'), nullable=False)
    description = db.Column(db.Text)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    dtModified = db.Column(db.DateTime, nullable=False)
    isIcraft = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    permissions = db.Column(db.Integer)

class TdCompany(db.Model):
    __tablename__ = 'td_company'

    idx = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)
    name_kr = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    name_zh = db.Column(db.String(100))
    registrationNumber = db.Column(db.String(45), nullable=False)
    businessRegistrationUrl = db.Column(db.String(64))
    addr_kr = db.Column(db.Text, nullable=False)
    addr_en = db.Column(db.Text)
    addr_zh = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    delegator_kr = db.Column(db.String(40), nullable=False)
    delegator_en = db.Column(db.String(45))
    delegator_zh = db.Column(db.String(45))
    state = db.Column(Enum('Registered', 'Deleted', 'Paused'), nullable=False, server_default=db.FetchedValue())
    registrant = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtModified = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.Text)
    ci = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    description_kr = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text)
    description_zh = db.Column(db.Text)
    tntLogoImgUrl = db.Column(db.String(64))

    td_admin = db.relationship('TdAdmin', primaryjoin='TdCompany.modifier == TdAdmin.id', backref='tdadmin_td_companies')
    td_admin1 = db.relationship('TdAdmin', primaryjoin='TdCompany.registrant == TdAdmin.id', backref='tdadmin_td_companies_0')


    def to_json(self):
        json_company = {
            'idx': self.idx,
            'code': self.code,
            'name_kr': self.name_kr,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'registrationNumber': self.registrationNumber,
            'businessRegistrationUrl': self.businessRegistrationUrl,
            'addr_kr': self.addr_kr,
            'addr_en': self.addr_en,
            'addr_zh': self.addr_zh,
            'telephone': self.telephone,
            'fax': self.fax,
            'delegator_kr': self.delegator_kr,
            'delegator_en': self.delegator_en,
            'delegator_zh': self.delegator_zh,
            'state': self.state,
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
            'note': self.note,
            'ci': self.ci,
            'url': self.url,
            'description_kr': self.description_kr,
            'description_en': self.description_en,
            'description_zh': self.description_zh,
            'tntLogoImgUrl': self.tntLogoImgUrl
        }
        return json_company

class TdRetailer(db.Model):
    __tablename__ = 'td_retailer'

    idx = db.Column(db.Integer, primary_key=True)
    rtid = db.Column(db.String(10), nullable=False, index=True)
    name_kr = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(45))
    name_zh = db.Column(db.String(45))
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    state = db.Column(db.Enum('Registered', 'Deleted', 'Paused'), nullable=False, server_default=db.FetchedValue())
    note = db.Column(db.String(512))
    headerquarterYN = db.Column(db.Enum('Y', 'N'), nullable=False, server_default=db.FetchedValue())
    channel = db.Column(db.Integer, server_default=db.FetchedValue())
    managerName = db.Column(db.String(45))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    areaType = db.Column(db.String(6))
    latitude = db.Column(db.String(45))
    longitude = db.Column(db.String(45))
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)

    td_company = db.relationship('TdCompany', primaryjoin='TdRetailer.companyCode == TdCompany.code', backref='td_retailers')

    def to_json(self):
        json_retailer = {
            'idx': self.idx,
            'rtid': self.rtid,
            'name_kr': self.name_kr,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'companyCode': self.companyCode,
            'state': self.state,
            'note': self.note,
            'headerquarterYN': self.headerquarterYN,
            'channel': self.channel,
            'managerName': self.managerName,
            'address': self.address,
            'phone': self.phone,
            'areaType': self.areaType,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified
        }
        return json_retailer


class TdAreaLimit(db.Model):
    __tablename__ = 'td_area_limit'

    idx = db.Column(db.Integer, primary_key=True)
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    areaCode = db.Column(db.String(6), nullable=False, index=True)
    areaName = db.Column(db.String(45))
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifer = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)

    td_retailer = db.relationship('TdRetailer', primaryjoin='TdAreaLimit.rtid == TdRetailer.rtid', backref='td_area_limits')

    def to_json(self):
        json_arealimit = {
            'idx': self.idx,
            'rtid': self.rtid,
            'areaCode': self.areaCode,
            'areaName': self.areaName,          
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified
        }
        return json_arealimit


class TdAccount(db.Model):
    __tablename__ = 'td_account'

    idx = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(20), nullable=False, unique=True)
    pwd = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    name_kr = db.Column(db.String(40), nullable=False, index=True)
    name_en = db.Column(db.String(40))
    name_zh = db.Column(db.String(40))
    phone = db.Column(db.String(20), nullable=False, index=True)
    telephone = db.Column(db.String(20), nullable=False)
    fax = db.Column(db.String(20))
    companyCode = db.Column(db.ForeignKey('td_company.code'), nullable=False, index=True)
    role = db.Column(db.ForeignKey('tc_role.code'), nullable=False, index=True)
    position = db.Column(db.String(20))
    department = db.Column(db.String(45))
    state = db.Column(db.Enum('Registered', 'Deleted', 'Paused'), nullable=False)
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20), nullable=False)
    dtModified = db.Column(db.DateTime, nullable=False)
    dtLastConnected = db.Column(db.DateTime)
    note = db.Column(db.Text)
    failCount = db.Column(db.SmallInteger, server_default=db.FetchedValue())
    company_code = db.Column(db.String(10))
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), index=True)    

    td_company = db.relationship('TdCompany', primaryjoin='TdAccount.companyCode == TdCompany.code', backref='td_accounts')
    tc_role = db.relationship('TcRole', primaryjoin='TdAccount.role == TcRole.code', backref='td_accounts')
    td_retailer = db.relationship('TdRetailer', primaryjoin='TdAccount.rtid == TdRetailer.rtid', backref='td_accounts')

    def get_company_name(self, lang = 'ko'):
        u = TdCompany.query.filter_by(code=self.companyCode).first()
        if u:
            if lang == 'ko':
                return u.name_kr
            if lang == 'en':
                return u.name_en
            if lang == 'zh':
                return u.name_zh

    def get_retailer_name(self, lang = 'ko'):
        u = TdRetailer.query.filter_by(rtid=self.rtid).first()
        if u:
            if lang == 'ko':
                return u.name_kr
            if lang == 'en':
                return u.name_en
            if lang == 'zh':
                return u.name_zh

    def get_user_name(self, lang = 'ko'):        
        if lang == 'ko':
            return self.name_kr
        if lang == 'en':
            return self.name_en
        if lang == 'zh':
            return self.name_zh

    def to_json(self, lang = 'ko'):
        json_account = {
            'idx': self.idx,
            'id': self.id,
            'pwd': self.pwd,
            'email': self.email,
            'name_kr': self.name_kr,
            'naem_en': self.name_en,
            'naem_zh': self.name_zh,
            'phone': self.phone,
            'telephone': self.telephone,
            'fax': self.fax,
            'companyCode': self.companyCode,
            'companyName': self.get_company_name(lang),
            'role': self.role,
            'position': self.position,
            'department': self.department,
            'state': self.state,
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
            'dtLastConnected': self.dtLastConnected,
            'note': self.note,
            'failCount': self.failCount,
            'comapny_code': self.company_code,
            'rtid': self.rtid,
            'rtName': self.get_retailer_name(lang)

        }
        return json_account

    def to_json_simple(self, lang = 'ko'):
        json_account = {            
            'userId': self.id,
            'userName': self.get_user_name(lang),
            'companyCode': self.companyCode,
            'companyName': self.get_company_name(lang),
            'retailerId': self.rtid,
            'retailerName': self.get_retailer_name(lang),
            'role': self.role
        }
        return json_account

class TdHolotag(db.Model):
    __tablename__ = 'td_holotag'
    __table_args__ = (
        db.Index('idx_td_holotag_02', 'code', 'companyCode'),
    )

    idx = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    name_kr = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(45))
    name_zh = db.Column(db.String(45))
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    state = db.Column(db.Enum('Registered', 'Deleted', 'Paused'), nullable=False)
    attachType = db.Column(db.Enum('LABELBOX', 'POUCH', 'POUCH_PRINT'))
    certOverCnt = db.Column(db.Integer)
    certOverManyCnt = db.Column(db.Integer)
    registrant = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtModified = db.Column(db.DateTime, nullable=False)
    sourceImage = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)
    hVersion = db.Column(db.ForeignKey('td_tag_version.version'), nullable=False, index=True)    
    mappingCode = db.Column(db.String(10), index=True)
    sqrUrl = db.Column(db.String(32))
    sqrVer = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    tagStdQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    sBoxStdQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    mBoxStdQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    lBoxStdQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    palletStdQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())

    td_company = db.relationship('TdCompany', primaryjoin='TdHolotag.companyCode == TdCompany.code', backref='td_holotags')
    td_tag_version = db.relationship('TdTagVersion', primaryjoin='TdHolotag.hVersion == TdTagVersion.version', backref='td_holotags')
    td_admin = db.relationship('TdAdmin', primaryjoin='TdHolotag.modifier == TdAdmin.id', backref='tdadmin_td_holotags')
    td_admin1 = db.relationship('TdAdmin', primaryjoin='TdHolotag.registrant == TdAdmin.id', backref='tdadmin_td_holotags_0')

    def to_json(self):
        json_holotag = {            
            'idx': self.idx,
            'code': self.code,
            'name_kr': self.name_kr,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'companyCode': self.companyCode,
            'state': self.state,
            'attachType': self.attachType,
            'certOverCnt': self.certOverCnt,
            'certOverManyCnt': self.certOverManyCnt,            
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
            'sourceImage': self.sourceImage,
            'note': self.note,
            'hVersion': self.hVersion,
            'mappingCode': self.mappingCode,
            'sqrUrl': self.sqrUrl,
            'sqrVer': self.sqrVer,
            'tagStdQty': self.tagStdQty,
            'sBoxStdQty': self.sBoxStdQty,
            'mBoxStdQty': self.mBoxStdQty,
            'lBoxStdQty': self.lBoxStdQty,
            'palletStdQty': self.palletStdQty
        }
        return json_holotag


class TdLine(db.Model):
    __tablename__ = 'td_line'

    idx = db.Column(db.Integer, primary_key=True)
    lineCode = db.Column(db.String(10), nullable=False, unique=True)
    # lineName = db.Column(db.String(100), nullable=False)
    name_kr = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    note = db.Column(db.String(512))
    lineType = db.Column(db.String(6))
    state = db.Column(db.Enum('Registered', 'Deleted', 'Paused'))
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)

    td_company = db.relationship('TdCompany', primaryjoin='TdLine.companyCode == TdCompany.code', backref='td_lines')
    td_retailer = db.relationship('TdRetailer', primaryjoin='TdLine.rtid == TdRetailer.rtid', backref='td_lines')

    def to_json(self):
        json_line = {            
            'idx': self.idx,
            'lineCode': self.lineCode,
            # 'lineName': self.lineName,
            'name_kr': self.name_kr,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'companyCode': self.companyCode,
            'rtid': self.rtid,
            'note': self.note,
            'lineType': self.lineType,
            'state': self.state,
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
        }
        return json_line


class TdLogisticBox(db.Model):
    __tablename__ = 'td_logistic_box'

    idx = db.Column(db.BigInteger, primary_key=True)
    boxId = db.Column(db.String(45), nullable=False, unique=True)
    parentBoxId = db.Column(db.ForeignKey('td_logistic_box.boxId'), index=True)
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    lineCode = db.Column(db.ForeignKey('td_line.lineCode'), nullable=False, index=True)
    boxType = db.Column(db.Enum('S', 'M', 'L'), nullable=False)
    packQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    dispTagCode = db.Column(db.String(30))
    dispTagName = db.Column(db.String(80))
    dispProdDate = db.Column(db.String(10))
    dispLotNo = db.Column(db.String(30))    
    dispQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    dispRemark = db.Column(db.String(255))
    tagCode = db.Column(db.ForeignKey('td_holotag.code'), index=True)
    scanYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    dtScan = db.Column(db.DateTime)
    packYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    palletScanYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    dtPalletScan = db.Column(db.DateTime)
    palletPackYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    palletId = db.Column(db.ForeignKey('td_logistic_pallet.palletId'), index=True)
    lastLineCode = db.Column(db.String(10), index=True)
    lastRtid = db.Column(db.String(10), index=True)
    lastParentBoxId = db.Column(db.String(45), index=True)
    lastPalletId = db.Column(db.String(45), index=True)
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)

    td_line = db.relationship('TdLine', primaryjoin='TdLogisticBox.lineCode == TdLine.lineCode', backref='td_logistic_boxes')
    td_logistic_pallet = db.relationship('TdLogisticPallet', primaryjoin='TdLogisticBox.palletId == TdLogisticPallet.palletId', backref='td_logistic_boxes')
    # parent = db.relationship('TdLogisticBox', remote_side=[idx], primaryjoin='TdLogisticBox.parentBoxId == TdLogisticBox.boxId', backref='td_logistic_boxes')
    td_company = db.relationship('TdCompany', primaryjoin='TdLogisticBox.companyCode == TdCompany.code', backref='td_logistic_boxes')
    td_retailer = db.relationship('TdRetailer', primaryjoin='TdLogisticBox.rtid == TdRetailer.rtid', backref='td_logistic_boxes')
    td_holotag = db.relationship('TdHolotag', primaryjoin='TdLogisticBox.tagCode == TdHolotag.code', backref='td_logistic_boxes')

    def get_holotag_name(self, lang = 'ko'):
        u = TdHolotag.query.filter_by(code=self.tagCode, companyCode=self.companyCode).first()
        if u:
            if lang == 'ko':
                return u.name_kr
            if lang == 'en':
                return u.name_en
            if lang == 'zh':
                return u.name_zh

    def get_date_to_str(self, val):
        rtn = None
        if val is not None:
            rtn = val.strftime('%Y-%m-%d %H:%M:%S')
        return rtn

    def to_json(self):
        json_box = {            
            'idx': self.idx,
            'boxId': self.boxId,
            'parentBoxId': self.parentBoxId,
            'companyCode': self.companyCode,
            'rtid': self.rtid,
            'lineCode': self.lineCode,
            'boxType': self.boxType,
            'packQty': self.packQty,
            'dispTagCode': self.dispTagCode,
            'dispTagName': self.dispTagName,
            'dispProdDate': self.dispProdDate,
            'dispLotNo': self.dispLotNo,
            'dispQty': self.dispQty,
            'dispRemark': self.dispRemark,
            'tagCode': self.tagCode,
            # 'tagName': self.get_holotag_name(),
            'scanYn': self.scanYn,
            'dtScan': self.get_date_to_str(self.dtScan),
            'packYn': self.packYn,
            'palletScanYn': self.palletScanYn,
            'dtPalletScan': self.get_date_to_str(self.dtPalletScan),
            'palletPackYn': self.palletPackYn,
            'palletId': self.palletId,
            'lastLineCode': self.lastLineCode,
            'lastRtid': self.lastRtid,
            'lastParentBoxId': self.lastParentBoxId,
            'lastPalletId': self.lastPalletId,
            'registrant': self.registrant,
            'dtRegistered': self.get_date_to_str(self.dtRegistered),
            'modifier': self.modifier,
            'dtModified': self.get_date_to_str(self.dtModified)
        }
        return json_box   


class TdLogisticPallet(db.Model):
    __tablename__ = 'td_logistic_pallet'

    idx = db.Column(db.BigInteger, primary_key=True)
    palletId = db.Column(db.String(45), nullable=False, unique=True)
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    lineCode = db.Column(db.ForeignKey('td_line.lineCode'), nullable=False, index=True)
    dispProdDate = db.Column(db.String(10))
    dispLotNo = db.Column(db.String(30))
    dispRemark = db.Column(db.String(255))
    tagCode = db.Column(db.ForeignKey('td_holotag.code'), index=True)
    scanYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    dtScan = db.Column(db.DateTime)
    lastLineCode = db.Column(db.String(10), index=True)
    lastRtid = db.Column(db.String(10), index=True)
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)
    
    td_line = db.relationship('TdLine', primaryjoin='TdLogisticPallet.lineCode == TdLine.lineCode', backref='td_logistic_pallets')
    td_company = db.relationship('TdCompany', primaryjoin='TdLogisticPallet.companyCode == TdCompany.code', backref='td_logistic_pallets')
    td_retailer = db.relationship('TdRetailer', primaryjoin='TdLogisticPallet.rtid == TdRetailer.rtid', backref='td_logistic_pallets')
    td_holotag = db.relationship('TdHolotag', primaryjoin='TdLogisticPallet.tagCode == TdHolotag.code', backref='td_logistic_pallets')

    def get_date_to_str(self, val):
        rtn = None
        if val is not None:
            rtn = val.strftime('%Y-%m-%d %H:%M:%S')
        return rtn

    def to_json(self):
        json_pallet = {            
            'idx': self.idx,
            'palletId': self.palletId,         
            'companyCode': self.companyCode,
            'rtid': self.rtid,
            'lineCode': self.lineCode,
            'dispProdDate': self.dispProdDate,
            'dispLotNo': self.dispLotNo,            
            'dispRemark': self.dispRemark,
            'tagCode': self.tagCode,
            'scanYn': self.scanYn,
            'dtScan': self.get_date_to_str(self.dtScan),
            'lastLineCode': self.lastLineCode,
            'lastRtid': self.lastRtid,
            'registrant': self.registrant,
            'dtRegistered': self.get_date_to_str(self.dtRegistered),
            'modifier': self.modifier,
            'dtModified': self.get_date_to_str(self.dtModified)
        }
        return json_pallet

class TdLogisticTag(db.Model):
    __tablename__ = 'td_logistic_tag'

    idx = db.Column(db.BigInteger, primary_key=True)
    companyCode = db.Column(db.ForeignKey('td_company.code'), index=True)
    rtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    lineCode = db.Column(db.ForeignKey('td_line.lineCode'), nullable=False, index=True)
    tagId = db.Column(db.String(45), nullable=False, unique=True)
    tagCode = db.Column(db.ForeignKey('td_holotag.code'), nullable=False, index=True)
    scanYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    dtScan = db.Column(db.DateTime)
    packYn = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    scanId = db.Column(db.String(80), nullable=False, index=True)
    random = db.Column(db.String(16))
    boxId = db.Column(db.ForeignKey('td_logistic_box.boxId'), index=True)
    tagQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    lastLineCode = db.Column(db.String(10), index=True)
    lastRtid = db.Column(db.String(10), index=True)
    lastBoxId = db.Column(db.String(45), index=True)
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)
    
    td_logistic_box = db.relationship('TdLogisticBox', primaryjoin='TdLogisticTag.boxId == TdLogisticBox.boxId', backref='td_logistic_tags')
    td_line = db.relationship('TdLine', primaryjoin='TdLogisticTag.lineCode == TdLine.lineCode', backref='td_logistic_tags')
    td_company = db.relationship('TdCompany', primaryjoin='TdLogisticTag.companyCode == TdCompany.code', backref='td_logistic_tags')
    td_retailer = db.relationship('TdRetailer', primaryjoin='TdLogisticTag.rtid == TdRetailer.rtid', backref='td_logistic_tags')
    td_holotag = db.relationship('TdHolotag', primaryjoin='TdLogisticTag.tagCode == TdHolotag.code', backref='td_logistic_tags')

    def get_holotag_name(self, lang = 'ko'):
        u = TdHolotag.query.filter_by(companyCode=self.companyCode, code=self.tagCode).first()
        if u:
            if lang == 'ko':
                return u.name_kr
            if lang == 'en':
                return u.name_en
            if lang == 'zh':
                return u.name_zh

    def get_date_to_str(self, val):
        rtn = None
        if val is not None:
            rtn = val.strftime('%Y-%m-%d %H:%M:%S')
        return rtn

    def to_json(self):
        json_tag = {            
            'idx': self.idx,
            'companyCode': self.companyCode,
            'rtid': self.rtid,
            'lineCode': self.lineCode,
            'tagId': self.tagId,
            'tagCode': self.tagCode,
            # 'tagName': self.get_holotag_name(),
            'scanYn': self.scanYn,
            'dtScan': self.get_date_to_str(self.dtScan),
            'packYn': self.packYn,
            'scanId': self.scanId,
            'random': self.random,
            'boxId': self.boxId,
            'tagQty': self.tagQty,
            'lastLineCode': self.lastLineCode,
            'lastRtid': self.lastRtid,
            'lastBoxId': self.lastBoxId,
            'registrant': self.registrant,
            'dtRegistered': self.get_date_to_str(self.dtRegistered),
            'modifier': self.modifier,
            'dtModified': self.get_date_to_str(self.dtModified)
        }
        return json_tag

class ThLogisticInout(db.Model):
    __tablename__ = 'th_logistic_inout'
    __table_args__ = (
        db.Index('idx_th_logistic_inout_id', 'ioId', 'ioSeq'),
    )

    idx = db.Column(db.BigInteger, primary_key=True)
    companyCode = db.Column(db.ForeignKey('td_company.code'), nullable=False, index=True)
    ioType = db.Column(db.Enum('IN', 'OUT'), nullable=False, index=True)
    ioDate = db.Column(db.String(8), nullable=False, index=True)
    ioId = db.Column(db.String(45), nullable=False)
    ioSeq = db.Column(db.Integer, nullable=False)
    tagId = db.Column(db.ForeignKey('td_logistic_tag.tagId'), index=True)
    boxId = db.Column(db.ForeignKey('td_logistic_box.boxId'), index=True)
    palletId = db.Column(db.ForeignKey('td_logistic_pallet.palletId'), index=True)
    scanId = db.Column(db.String(45),index=True)
    random = db.Column(db.String(16))
    tagCode = db.Column(db.ForeignKey('td_holotag.code'), index=True)
    ioQty = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    ioRtid = db.Column(db.ForeignKey('td_retailer.rtid'), nullable=False, index=True)
    scanType = db.Column(db.Enum('T', 'S', 'M', 'L', 'P'), nullable=False)
    clientType = db.Column(db.Enum('W', 'B', 'L'), nullable=False)
    deviceID = db.Column(db.String(50))
    osType = db.Column(db.Enum('iOS', 'Android', 'Unknown', 'Web'))
    latitude = db.Column(db.String(45))
    longitude = db.Column(db.String(45))
    registrant = db.Column(db.String(20), nullable=False)
    dtRegistered = db.Column(db.DateTime, nullable=False, index=True)
    modifier = db.Column(db.String(20))
    dtModified = db.Column(db.DateTime)

    td_logistic_box = db.relationship('TdLogisticBox', primaryjoin='ThLogisticInout.boxId == TdLogisticBox.boxId', backref='th_logistic_inouts')
    td_company = db.relationship('TdCompany', primaryjoin='ThLogisticInout.companyCode == TdCompany.code', backref='th_logistic_inouts')
    td_retailer = db.relationship('TdRetailer', primaryjoin='ThLogisticInout.ioRtid == TdRetailer.rtid', backref='th_logistic_inouts')
    td_logistic_pallet = db.relationship('TdLogisticPallet', primaryjoin='ThLogisticInout.palletId == TdLogisticPallet.palletId', backref='th_logistic_inouts')
    td_logistic_tag = db.relationship('TdLogisticTag', primaryjoin='ThLogisticInout.tagId == TdLogisticTag.tagId', backref='th_logistic_inouts')
    td_holotag = db.relationship('TdHolotag', primaryjoin='ThLogisticInout.tagCode == TdHolotag.code', backref='th_logistic_inouts')

    

    def get_date_to_str(self, val):
        rtn = None
        if val is not None:
            rtn = val.strftime('%Y-%m-%d %H:%M:%S')
        return rtn

    def to_json(self):
        json_inout = {            
            'idx': self.idx,
            'companyCode': self.companyCode,
            'ioType': self.ioType,
            'ioDate': self.ioDate,
            'ioId': self.ioId,
            'ioSeq': self.ioSeq,
            'tagId': self.tagId,
            'boxId': self.boxId,
            'palletId': self.palletId,
            'scanId': self.scanId,
            'random': self.random,
            'tagCode': self.tagCode,
            'ioQty': self.ioQty,
            'ioRtid': self.ioRtid,
            'scanType': self.scanType,
            'deviceID': self.deviceID,
            'osType': self.osType,
            'latitude': self.latitude,
            'longitude': self.longitude,            
            'registrant': self.registrant,
            'dtRegistered': self.get_date_to_str(self.dtRegistered),
            'modifier': self.modifier,
            'dtModified': self.get_date_to_str(self.dtModified)
        }
        return json_inout

    def to_json_app(self, name):
        json_inout = {            
            'idx': self.idx,
            'companyCode': self.companyCode,
            'ioType': self.ioType,
            'ioDate': self.ioDate,
            'ioId': self.ioId,
            'ioSeq': self.ioSeq,
            'tagId': self.tagId,
            'boxId': self.boxId,
            'palletId': self.palletId,
            'scanId': self.scanId,
            'random': self.random,
            'tagCode': self.tagCode,
            'ioQty': self.ioQty,
            'ioRtid': self.ioRtid,
            'scanType': self.scanType,
            'deviceID': self.deviceID,
            'osType': self.osType,
            'latitude': self.latitude,
            'longitude': self.longitude,            
            'registrant': self.registrant,
            'dtRegistered': self.get_date_to_str(self.dtRegistered),
            'modifier': self.modifier,
            'dtModified': self.get_date_to_str(self.dtModified),            
            'tagName': name
        }
        return json_inout

class TdTagVersion(db.Model):
    __tablename__ = 'td_tag_version'

    idx = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(11), nullable=False, unique=True)
    type = db.Column(db.Enum('HOLOTAG_ONLY', 'HOLOTAG_BARCODE', 'HYBRIDTAG', 'RANDOMTAG', 'SQRTAG'), nullable=False)
    name_kr = db.Column(db.String(60), nullable=False)
    name_en = db.Column(db.String(60), nullable=False)
    name_zh = db.Column(db.String(60), nullable=False)
    state = db.Column(db.Enum('Enable', 'Disable', 'Deleted'), nullable=False, server_default=db.FetchedValue())
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    registrant = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtRegistered = db.Column(db.DateTime, nullable=False)
    modifier = db.Column(db.ForeignKey('td_admin.id'), nullable=False, index=True)
    dtModified = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.Text)

    td_admin = db.relationship('TdAdmin', primaryjoin='TdTagVersion.modifier == TdAdmin.id', backref='tdadmin_td_tag_versions')
    td_admin1 = db.relationship('TdAdmin', primaryjoin='TdTagVersion.registrant == TdAdmin.id', backref='tdadmin_td_tag_versions_0')

    def to_json(self):
        json_tagversion = {            
            'idx': self.idx,
            'version': self.version,
            'type': self.type,
            'name_kr': self.name_kr,
            'name_en': self.name_en,
            'name_zh': self.name_zh,
            'state': self.state,
            'width': self.width,
            'height': self.height,
            'description': self.description,                      
            'registrant': self.registrant,
            'dtRegistered': self.dtRegistered,
            'modifier': self.modifier,
            'dtModified': self.dtModified,
            'note': self.note
        }
        return json_tagversion