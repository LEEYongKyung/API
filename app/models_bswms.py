# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, Numeric, String
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import FetchedValue
from app import db

class MstCust(db.Model):
    __tablename__ = 'mst_cust'

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    custCd = db.Column(db.String(10), primary_key=True, nullable=False)
    custNm = db.Column(db.String(80))
    custNmEn = db.Column(db.String(80))
    custAbb = db.Column(db.String(5))
    custType = db.Column(db.String(30))
    custLocType = db.Column(db.String(10))
    varId = db.Column(db.String(20))
    sellYn = db.Column(db.String(1))
    purcYn = db.Column(db.String(1))
    address1 = db.Column(db.String(80))
    address2 = db.Column(db.String(80))
    address3 = db.Column(db.String(80))
    city = db.Column(db.String(80))
    province = db.Column(db.String(80))
    zipCode = db.Column(db.String(10))
    country = db.Column(db.String(80))
    contact = db.Column(db.String(40))
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    corpNo = db.Column(db.String(20))
    note = db.Column(db.String(200))
    note2 = db.Column(db.String(200))
    note3 = db.Column(db.String(200))
    note4 = db.Column(db.String(200))
    note5 = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='MstCust.siteCd == SysSite.siteCd', backref='mst_custs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'custCd': self.custCd,
            'custNm': self.custNm,
            'custNmEn': self.custNmEn,
            'custAbb': self.custAbb,
            'custType': self.custType,
            'custLocType': self.custLocType,
            'varId': self.varId,
            'sellYn': self.sellYn,
            'purcYn': self.purcYn,
            'address1': self.address1,
            'address2': self.address2,
            'address3': self.address3,
            'city': self.city,
            'province': self.province,
            'zipCode': self.zipCode,
            'country': self.country,
            'contact': self.contact,
            'phone': self.phone,
            'fax': self.fax,
            'corpNo': self.corpNo,
            'note': self.note,
            'note2': self.note2,
            'note3': self.note3,
            'note4': self.note4,
            'note5': self.note5,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class MstPart(db.Model):
    __tablename__ = 'mst_part'

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    partCd = db.Column(db.String(10), primary_key=True, nullable=False)
    partNm = db.Column(db.String(40))
    partKind = db.Column(db.String(10))
    partType1 = db.Column(db.String(10))
    partType2 = db.Column(db.String(10))
    partType3 = db.Column(db.String(10))
    partSpec = db.Column(db.String(80))
    partUnit = db.Column(db.String(10))
    currency = db.Column(db.String(10))
    manufacturer = db.Column(db.String(10))
    note = db.Column(db.String(200))
    note2 = db.Column(db.String(200))
    note3 = db.Column(db.String(200))
    note4 = db.Column(db.String(200))
    note5 = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='MstPart.siteCd == SysSite.siteCd', backref='mst_parts')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'partCd': self.partCd,
            'partNm': self.partNm,
            'partKind': self.partKind,
            'partType1': self.partType1,
            'partType2': self.partType2,
            'partType3': self.partType3,
            'partSpec': self.partSpec,
            'partUnit': self.partUnit,
            'currency': self.currency,
            'manufacturer': self.manufacturer,
            'note': self.note,
            'note2': self.note2,
            'note3': self.note3,
            'note4': self.note4,
            'note5': self.note5,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class MstPartPrice(db.Model):
    __tablename__ = 'mst_part_price'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.Index('FK_mst_part_TO_mst_part_price', 'siteCd', 'partCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    prcCd = db.Column(db.String(20), primary_key=True, nullable=False)
    partCd = db.Column(db.String(10), nullable=False)
    prcType = db.Column(db.String(10), nullable=False)
    prcAmt = db.Column(db.Numeric(14, 2))
    currency = db.Column(db.String(10))
    stDate = db.Column(db.String(8))
    edDate = db.Column(db.String(8))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(MstPartPrice.siteCd == MstPart.siteCd, MstPartPrice.partCd == MstPart.partCd)', backref='mst_part_prices')
    sys_site = db.relationship('SysSite', primaryjoin='MstPartPrice.siteCd == SysSite.siteCd', backref='mst_part_prices')

class MstProject(db.Model):
    __tablename__ = 'mst_project'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'custCd'], ['mst_cust.siteCd', 'mst_cust.custCd']),
        db.Index('FK_mst_cust_TO_mst_project', 'siteCd', 'custCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    prjCd = db.Column(db.String(20), primary_key=True, nullable=False)
    prjNm = db.Column(db.String(80))
    prjType = db.Column(db.String(10))
    prjDate = db.Column(db.String(8))
    prjUser = db.Column(db.String(40))
    docNo = db.Column(db.String(40))
    prjAmt = db.Column(db.Numeric(14, 2))
    currency = db.Column(db.String(10))
    custCd = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_cust = db.relationship('MstCust', primaryjoin='and_(MstProject.siteCd == MstCust.siteCd, MstProject.custCd == MstCust.custCd)', backref='mst_projects')
    sys_site = db.relationship('SysSite', primaryjoin='MstProject.siteCd == SysSite.siteCd', backref='mst_projects')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'prjCd': self.prjCd,
            'prjNm': self.prjNm,
            'prjType': self.prjType,
            'prjDate': None if self.prjDate is None else self.prjDate if self.prjDate == '0000-00-00' else self.prjDate[:4] + '-' + self.prjDate[4:6] + '-' + self.prjDate[6:],
            'prjUser': self.prjUser,
            'docNo': self.docNo,
            'prjAmt': self.prjAmt,
            'currency': self.currency,
            'custCd': self.custCd,
            'custNm': MstCust.query.filter_by(siteCd=self.siteCd,custCd=self.custCd).first().custNm,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class MstStdStock(db.Model):
    __tablename__ = 'mst_std_stock'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.Index('FK_mst_part_TO_mst_std_stock', 'siteCd', 'partCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    sstkCd = db.Column(db.String(30), primary_key=True, nullable=False)
    partCd = db.Column(db.String(10), nullable=False)
    inDate = db.Column(db.String(8))
    stkQty = db.Column(db.Numeric(14, 2))
    stkAmt = db.Column(db.Numeric(14, 2))
    stkType = db.Column(db.String(10), nullable=False)    
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(MstStdStock.siteCd == MstPart.siteCd, MstStdStock.partCd == MstPart.partCd)', backref='mst_std_stocks')
    sys_site = db.relationship('SysSite', primaryjoin='MstStdStock.siteCd == SysSite.siteCd', backref='mst_std_stocks')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'sstkCd': self.sstkCd,
            'partCd': self.partCd,
            'inDate': self.inDate,
            'stkQty': self.stkQty,
            'stkAmt': self.stkAmt,
            'inDate': self.inDate,
            'stkType': self.stkType,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class MstWh(db.Model):
    __tablename__ = 'mst_wh'

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    whCd = db.Column(db.String(10), primary_key=True, nullable=False)
    whNm = db.Column(db.String(80))
    whType = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='MstWh.siteCd == SysSite.siteCd', backref='mst_whs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'whCd': self.whCd,
            'whNm': self.whNm,
            'whType': self.whType,            
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class PosCm(db.Model):
    __tablename__ = 'pos_cm'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'posCd'], ['pos_pos.siteCd', 'pos_pos.posCd']),
        db.Index('FK_pos_pos_TO_pos_cm', 'siteCd', 'posCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    cmCd = db.Column(db.String(20), primary_key=True, nullable=False)
    cmState = db.Column(db.String(10))
    cmDate = db.Column(db.String(8))
    cmNo = db.Column(db.String(20))
    rebAmt = db.Column(db.Numeric(14, 2))
    remAmt = db.Column(db.Numeric(14, 2))
    excRate = db.Column(db.Numeric(14, 2))
    rebWonAmt = db.Column(db.Numeric(14, 2))
    costWonAmt = db.Column(db.Numeric(14, 2))
    posCd = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    pos_po = db.relationship('PosPo', primaryjoin='and_(PosCm.siteCd == PosPo.siteCd, PosCm.posCd == PosPo.posCd)', backref='pos_cms')
    sys_site = db.relationship('SysSite', primaryjoin='PosCm.siteCd == SysSite.siteCd', backref='pos_cms')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'cmCd': self.cmCd,
            'cmState': self.cmState,
            'cmDate': self.cmDate,
            'cmNo': self.cmNo,
            'rebAmt': self.rebAmt,
            'remAmt': self.remAmt,
            'excRate': self.excRate,
            'rebWonAmt': self.rebWonAmt,
            'costWonAmt': self.costWonAmt,
            'posCd': self.posCd,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class PosCmLog(db.Model):
    __tablename__ = 'pos_cm_log'

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    cmCd = db.Column(db.String(20), primary_key=True, nullable=False)
    logSeq = db.Column(db.Integer, primary_key=True, nullable=False)    
    cmState = db.Column(db.String(10))
    cmDate = db.Column(db.String(8))
    cmNo = db.Column(db.String(20))
    rebAmt = db.Column(db.Numeric(14, 2))
    remAmt = db.Column(db.Numeric(14, 2))
    excRate = db.Column(db.Numeric(14, 2))
    rebWonAmt = db.Column(db.Numeric(14, 2))
    costWonAmt = db.Column(db.Numeric(14, 2))
    posCd = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)


class PosCmUse(db.Model):
    __tablename__ = 'pos_cm_use'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'cmCd'], ['pos_cm.siteCd', 'pos_cm.cmCd']),
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    cmCd = db.Column(db.String(20), primary_key=True, nullable=False)
    useSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    useDate = db.Column(db.String(8))
    preAmt = db.Column(db.Numeric(14, 2))
    useAmt = db.Column(db.Numeric(14, 2))
    remAmt = db.Column(db.Numeric(14, 2))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    pos_cm = db.relationship('PosCm', primaryjoin='and_(PosCmUse.siteCd == PosCm.siteCd, PosCmUse.cmCd == PosCm.cmCd)', backref='pos_cm_uses')
    sys_site = db.relationship('SysSite', primaryjoin='PosCmUse.siteCd == SysSite.siteCd', backref='pos_cm_uses')


class PosPo(db.Model):
    __tablename__ = 'pos_pos'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'lotNo'], ['stk_lot.siteCd', 'stk_lot.lotNo']),
        db.ForeignKeyConstraint(['siteCd', 'poCd'], ['pur_order.siteCd', 'pur_order.poCd']),
        db.ForeignKeyConstraint(['siteCd', 'spaCd', 'spaSeq'], ['pos_spa.siteCd', 'pos_spa.spaCd', 'pos_spa.spaSeq']),
        db.Index('FK_pur_order_TO_pos_pos', 'siteCd', 'poCd'),
        db.Index('FK_stk_lot_TO_pos_pos', 'siteCd', 'lotNo'),
        db.Index('FK_pos_spa_TO_pos_pos', 'siteCd', 'spaCd', 'spaSeq')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    posCd = db.Column(db.String(20), primary_key=True, nullable=False)
    posState = db.Column(db.String(10))
    spa = db.Column(db.String(20))
    posDate = db.Column(db.String(8))
    posQty = db.Column(db.Numeric(14, 2))
    dc = db.Column(db.Numeric(15, 3))
    reseller = db.Column(db.String(10))
    endUser = db.Column(db.String(10))
    netPos = db.Column(db.String(20))
    am = db.Column(db.String(30))
    partner = db.Column(db.String(80))
    jda = db.Column(db.String(10))
    vertical = db.Column(db.String(80))
    year = db.Column(db.String(4))
    quater = db.Column(db.String(4))
    week = db.Column(db.String(4))
    poCd = db.Column(db.String(20))
    lotNo = db.Column(db.String(20))
    spaCd = db.Column(db.String(20))
    spaSeq = db.Column(db.Integer)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_lot = db.relationship('StkLot', primaryjoin='and_(PosPo.siteCd == StkLot.siteCd, PosPo.lotNo == StkLot.lotNo)', backref='pos_poes')
    pur_order = db.relationship('PurOrder', primaryjoin='and_(PosPo.siteCd == PurOrder.siteCd, PosPo.poCd == PurOrder.poCd)', backref='pos_poes')
    pos_spa = db.relationship('PosSpa', primaryjoin='and_(PosPo.siteCd == PosSpa.siteCd, PosPo.spaCd == PosSpa.spaCd, PosPo.spaSeq == PosSpa.spaSeq)', backref='pos_poes')
    sys_site = db.relationship('SysSite', primaryjoin='PosPo.siteCd == SysSite.siteCd', backref='pos_poes')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'posCd': self.posCd,
            'posState': self.posState,
            'spa': self.spa,            
            'posDate': self.posDate,
            'posQty': self.posQty,
            'dc': self.dc,
            'reseller': self.reseller,
            'endUser': self.endUser,
            'netPos': self.netPos,
            'am': self.am,
            'partner': self.partner,
            'jda': self.jda,
            'vertical': self.vertical,
            'year': self.year,
            'quater': self.quater,
            'week': self.week,
            'poCd': self.poCd,
            'lotNo': self.lotNo,
            'spaCd': self.spaCd,
            'spaSeq': self.spaSeq,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class PosPosLog(db.Model):
    __tablename__ = 'pos_pos_log'

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    posCd = db.Column(db.String(20), primary_key=True, nullable=False)
    logSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    posState = db.Column(db.String(10))
    spa = db.Column(db.String(20))
    posDate = db.Column(db.String(8))
    posQty = db.Column(db.Numeric(14, 2))
    dc = db.Column(db.Numeric(15, 3))
    reseller = db.Column(db.String(10))
    endUser = db.Column(db.String(10))
    am = db.Column(db.String(80))
    netPos = db.Column(db.String(20))
    partner = db.Column(db.String(80))
    jda = db.Column(db.String(10))
    vertical = db.Column(db.String(80))
    year = db.Column(db.String(4))
    quater = db.Column(db.String(4))
    week = db.Column(db.String(4))
    poCd = db.Column(db.String(20))
    lotNo = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'posCd': self.posCd,
            'logSeq': self.logSeq,
            'posState': self.posState,
            'spa': self.spa,            
            'posDate': self.posDate,
            'posQty': self.posQty,
            'dc': self.dc,
            'reseller': self.reseller,
            'endUser': self.endUser,
            'netPos': self.netPos,
            'am': self.am,
            'partner': self.partner,
            'jda': self.jda,
            'vertical': self.vertical,
            'year': self.year,
            'quater': self.quater,
            'week': self.week,
            'poCd': self.poCd,
            'lotNo': self.lotNo,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class PosSpa(db.Model):
    __tablename__ = 'pos_spa'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.Index('FK_mst_part_TO_pos_spa', 'siteCd', 'partCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    spaCd = db.Column(db.String(20), primary_key=True, nullable=False)
    spaSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    spaDate = db.Column(db.String(8))
    spa = db.Column(db.String(20))
    reseller = db.Column(db.String(10))
    endUser = db.Column(db.String(10))
    partCd = db.Column(db.String(10))
    qty = db.Column(db.Numeric(14, 2))
    listPrice = db.Column(db.Numeric(14, 2))
    dc = db.Column(db.Numeric(15, 3))
    extListPrice = db.Column(db.Numeric(14, 2))
    extDiscount = db.Column(db.Numeric(14, 2))
    extNetTotal = db.Column(db.Numeric(14, 2))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(PosSpa.siteCd == MstPart.siteCd, PosSpa.partCd == MstPart.partCd)', backref='pos_spas')
    sys_site = db.relationship('SysSite', primaryjoin='PosSpa.siteCd == SysSite.siteCd', backref='pos_spas')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'spaCd': self.spaCd,
            'spaSeq': self.spaSeq,
            'spaDate': self.spaDate,            
            'spa': self.spa,
            'reseller': self.reseller,
            'endUser': self.endUser,
            'partCd': self.partCd,
            'qty': self.qty,
            'listPrice': self.listPrice,
            'dc': self.dc,
            'extListPrice': self.extListPrice,
            'extDiscount': self.extDiscount,
            'extNetTotal': self.extNetTotal,
            'note': self.note,           
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class PosSpaExt(db.Model):
    __tablename__ = 'pos_spa_ext'    

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    spaCd = db.Column(db.String(20), primary_key=True, nullable=False)
    spaSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    reportType = db.Column(db.String(20))
    distributorId = db.Column(db.String(20))
    distributorName = db.Column(db.String(40))
    resellerVarId = db.Column(db.String(20))
    resellerName = db.Column(db.String(40))
    theatre = db.Column(db.String(40))
    region = db.Column(db.String(80))
    dealState = db.Column(db.String(20))
    partnerLevel = db.Column(db.String(20))
    dateEffective = db.Column(db.String(8))
    dateExpiration = db.Column(db.String(8))
    dateLastPublished = db.Column(db.String(8))
    revision = db.Column(db.Integer)
    shipAndDebitId = db.Column(db.String(20))
    endCustomerId = db.Column(db.String(20))
    endUserVatId = db.Column(db.String(20))
    endUserName = db.Column(db.String(40))
    endCostomerAddress1 = db.Column(db.String(80))
    endCostomerAddress2 = db.Column(db.String(80))
    endCostomerAddress3 = db.Column(db.String(80))
    endUserCity = db.Column(db.String(80))
    endUserProvince = db.Column(db.String(80))
    endUserZipCode = db.Column(db.String(10))
    endUserCountry = db.Column(db.String(80))
    jnprSalesRep = db.Column(db.String(20))
    lastUpdatedBy = db.Column(db.String(20))
    sku = db.Column(db.String(40))
    skuDescription = db.Column(db.String(80))
    fulfillmentType = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(14, 2))
    listPrice = db.Column(db.Numeric(14, 2))
    discountRateDistributor = db.Column(db.Numeric(14, 2))
    suggestedDiscountRateReseller = db.Column(db.Numeric(14, 2))
    suggestedDiscountRateEndUser = db.Column(db.Numeric(14, 2))
    extendedListPrice = db.Column(db.Numeric(14, 2))
    extendedDiscount = db.Column(db.Numeric(14, 2))
    extendedNetTotal = db.Column(db.Numeric(14, 2))
    productLine = db.Column(db.String(20))
    productFamily = db.Column(db.String(20))
    lineNumber = db.Column(db.String(20))
    parentLineNumber = db.Column(db.String(20))
    configNumber = db.Column(db.String(20))
    configInstance = db.Column(db.String(20))
    serviceDuration = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='PosSpaExt.siteCd == SysSite.siteCd', backref='pos_spa_exts')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'spaCd': self.posCd,
            'spaSeq': self.spaSeq,
            'reportType': self.reportType,            
            'distributorId': self.distributorId,
            'distributorName': self.distributorName,
            'resellerVarId': self.resellerVarId,
            'resellerName': self.resellerName,
            'theatre': self.theatre,
            'region': self.region,
            'dealState': self.dealState,
            'dateEffective': self.dateEffective,
            'dateExpiration': self.dateExpiration,
            'dateLastPublished': self.dateLastPublished,
            'revision': self.revision,
            'shipAndDebitId': self.shipAndDebitId,
            'endCustomerId': self.endCustomerId,
            'endUserVatId': self.endUserVatId,
            'endUserName': self.endUserName,
            'endCostomerAddress1': self.endCostomerAddress1,
            'endCostomerAddress2': self.endCostomerAddress2,
            'endCostomerAddress3': self.endCostomerAddress3,
            'endUserCity': self.endUserCity,
            'endUserProvince': self.endUserProvince,
            'endUserZipCode': self.endUserZipCode,
            'endUserCountry': self.endUserCountry,
            'jnprSalesRep': self.jnprSalesRep,
            'lastUpdatedBy': self.lastUpdatedBy,
            'sku': self.sku,
            'skuDescription': self.skuDescription,
            'fulfillmentType': self.fulfillmentType,
            'quantity': self.quantity,
            'listPrice': self.listPrice,
            'discountRateDistributor': self.discountRateDistributor,
            'suggestedDiscountRateReseller': self.suggestedDiscountRateReseller,
            'suggestedDiscountRateEndUser': self.suggestedDiscountRateEndUser,
            'extendedListPrice': self.extendedListPrice,
            'extendedDiscount': self.extendedDiscount,
            'extendedNetTotal': self.extendedNetTotal,
            'productLine': self.productLine,
            'productFamily': self.productFamily,
            'lineNumber': self.lineNumber,
            'parentLineNumber': self.parentLineNumber,
            'configNumber': self.configNumber,
            'configInstance': self.configInstance,
            'serviceDuration': self.serviceDuration,           
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class PurOrder(db.Model):
    __tablename__ = 'pur_order'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'custCd'], ['mst_cust.siteCd', 'mst_cust.custCd']),
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.Index('FK_mst_part_TO_pur_order', 'siteCd', 'partCd'),
        db.Index('FK_mst_cust_TO_pur_order', 'siteCd', 'custCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    poCd = db.Column(db.String(20), primary_key=True, nullable=False)
    poNo = db.Column(db.String(30))
    poState = db.Column(db.String(10))
    poDate = db.Column(db.String(10))
    poType1 = db.Column(db.String(10))
    poType2 = db.Column(db.String(10))
    poType3 = db.Column(db.String(10))
    custCd = db.Column(db.String(10))
    partCd = db.Column(db.String(10))
    soNo = db.Column(db.String(30))
    poQty = db.Column(db.Numeric(14, 2))
    unitAmt = db.Column(db.Numeric(14, 2))
    listAmt = db.Column(db.Numeric(14, 2))
    taxAmt = db.Column(db.Numeric(14, 2))
    purcAmt = db.Column(db.Numeric(14, 2))
    currency = db.Column(db.String(10))
    posState = db.Column(db.String(10))
    svcStDate = db.Column(db.String(8))
    svcEdDate = db.Column(db.String(8))
    stkType = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_cust = db.relationship('MstCust', primaryjoin='and_(PurOrder.siteCd == MstCust.siteCd, PurOrder.custCd == MstCust.custCd)', backref='pur_orders')
    mst_part = db.relationship('MstPart', primaryjoin='and_(PurOrder.siteCd == MstPart.siteCd, PurOrder.partCd == MstPart.partCd)', backref='pur_orders')
    sys_site = db.relationship('SysSite', primaryjoin='PurOrder.siteCd == SysSite.siteCd', backref='pur_orders')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'poCd': self.poCd,
            'poNo': self.poNo,
            'poState': self.poState,
            'poDate': self.poState,
            'poType1': self.poType1,
            'poType2': self.poType2,
            'poType3': self.poType3,
            'custCd': self.custCd,
            'partCd': self.partCd,
            'soNo': self.soNo,
            'poQty': self.poQty,
            'unitAmt': self.unitAmt,
            'listAmt': self.listAmt,
            'purcAmt': self.purcAmt,
            'currency': self.currency,
            'posState': self.posState,
            'svcStDate': self.svcStDate,
            'svcEdDate': self.poStsvcEdDateate,
            'stkType': self.stkType,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SalDemo(db.Model):
    __tablename__ = 'sal_demo'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.Index('FK_mst_part_TO_sal_demo', 'siteCd', 'partCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    demoCd = db.Column(db.String(20), primary_key=True, nullable=False)
    demoState = db.Column(db.String(10))
    partCd = db.Column(db.String(10))
    inDate = db.Column(db.String(8))
    sn = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(SalDemo.siteCd == MstPart.siteCd, SalDemo.partCd == MstPart.partCd)', backref='sal_demos')
    sys_site = db.relationship('SysSite', primaryjoin='SalDemo.siteCd == SysSite.siteCd', backref='sal_demos')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'demoCd': self.demoCd,
            'demoState': self.demoState,
            'partCd': self.partCd,
            'note': self.note,
            'inDate': self.inDate,
            'sn': self.sn,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            # 'modUser': self.modUser,
            # 'modDate': None if self.modDate is None else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SalDemoRent(db.Model):
    __tablename__ = 'sal_demo_rent'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'demoCd'], ['sal_demo.siteCd', 'sal_demo.demoCd']),
        db.ForeignKeyConstraint(['siteCd', 'rentCust'], ['mst_cust.siteCd', 'mst_cust.custCd']),
        db.Index('FK_mst_cust_TO_sal_demo_rent', 'siteCd', 'rentCust')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    demoCd = db.Column(db.String(20), primary_key=True, nullable=False)
    demoSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    demoState = db.Column(db.String(10))
    rentUser = db.Column(db.String(30))
    rentDate = db.Column(db.String(8))
    rentCust = db.Column(db.String(10))
    rentManager = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(80))
    estRetDate = db.Column(db.String(8))
    rcvDate = db.Column(db.String(8))
    rcvUser = db.Column(db.String(20))
    rcvYN = db.Column(db.String(1), server_default=db.FetchedValue())
    state = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)


    sal_demo = db.relationship('SalDemo', primaryjoin='and_(SalDemoRent.siteCd == SalDemo.siteCd, SalDemoRent.demoCd == SalDemo.demoCd)', backref='sal_demo_rents')
    mst_cust = db.relationship('MstCust', primaryjoin='and_(SalDemoRent.siteCd == MstCust.siteCd, SalDemoRent.rentCust == MstCust.custCd)', backref='sal_demo_rents')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'demoCd': self.demoCd,
            'demoSeq': self.demoSeq,
            'demoState': self.demoState,
            'rentDate': self.rentDate,
            'rentUser': self.rentUser,
            'rentCust': self.rentCust,
            'rentManager': self.rentManager,
            'phone': self.phone,
            'address': self.address,
            'estRetDate': self.estRetDate,
            'rcvDate': self.rcvDate,
            'rcvUser': self.rcvUser,
            'rcvYN': self.rcvYN,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SalReserveDemo(db.Model):
    __tablename__ = 'sal_reserve_demo'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'demoCd'], ['sal_demo.siteCd', 'sal_demo.demoCd']),
        db.Index('FK_sal_demo_TO_sal_reserve_demo', 'siteCd', 'demoCd')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    rdCd = db.Column(db.String(20), primary_key=True, nullable=False)
    rdSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    resvDate = db.Column(db.String(8))
    resvUser = db.Column(db.String(20))
    demoCd = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sal_demo = db.relationship('SalDemo', primaryjoin='and_(SalReserveDemo.siteCd == SalDemo.siteCd, SalReserveDemo.demoCd == SalDemo.demoCd)', backref='sal_reserve_demos')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'rdCd': self.rdCd,
            'rdSeq': self.rdSeq,
            'resvDate': self.resvDate,
            'resvUser': self.resvUser,
            'demoCd': self.demoCd,            
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkIn(db.Model):
    __tablename__ = 'stk_in'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'lotNo'], ['stk_lot.siteCd', 'stk_lot.lotNo']),
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.ForeignKeyConstraint(['siteCd', 'poCd'], ['pur_order.siteCd', 'pur_order.poCd']),
        db.ForeignKeyConstraint(['siteCd', 'whCd'], ['mst_wh.siteCd', 'mst_wh.whCd']),
        db.Index('FK_stk_lot_TO_stk_in', 'siteCd', 'lotNo'),
        db.Index('FK_mst_part_TO_stk_in', 'siteCd', 'partCd'),
        db.Index('FK_mst_wh_TO_stk_in', 'siteCd', 'whCd'),
        db.Index('FK_pur_order_TO_stk_in', 'siteCd', 'poCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    inCd = db.Column(db.String(20), primary_key=True, nullable=False)
    inSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    inNo = db.Column(db.String(20))
    inDate = db.Column(db.String(8))
    lotNo = db.Column(db.String(20))
    sn = db.Column(db.String(30))
    inKind = db.Column(db.String(10))
    purcYn = db.Column(db.String(1))
    inType = db.Column(db.String(10))
    poCd = db.Column(db.String(20))
    partCd = db.Column(db.String(10))
    inQty = db.Column(db.Numeric(14, 2))
    inUnit = db.Column(db.String(10))
    inAmt = db.Column(db.Numeric(14, 2))
    currency = db.Column(db.String(10))
    cmLoc = db.Column(db.String(30))
    whCd = db.Column(db.String(10))
    loc = db.Column(db.String(20))
    bl = db.Column(db.String(20))
    invoice = db.Column(db.String(20))
    inWarr = db.Column(db.String(10))
    partRank = db.Column(db.String(10))
    svcStDate = db.Column(db.String(8))
    svcEdDate = db.Column(db.String(8))
    stkType = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_lot = db.relationship('StkLot', primaryjoin='and_(StkIn.siteCd == StkLot.siteCd, StkIn.lotNo == StkLot.lotNo)', backref='stk_ins')
    mst_part = db.relationship('MstPart', primaryjoin='and_(StkIn.siteCd == MstPart.siteCd, StkIn.partCd == MstPart.partCd)', backref='stk_ins')
    pur_order = db.relationship('PurOrder', primaryjoin='and_(StkIn.siteCd == PurOrder.siteCd, StkIn.poCd == PurOrder.poCd)', backref='stk_ins')
    mst_wh = db.relationship('MstWh', primaryjoin='and_(StkIn.siteCd == MstWh.siteCd, StkIn.whCd == MstWh.whCd)', backref='stk_ins')
    sys_site = db.relationship('SysSite', primaryjoin='StkIn.siteCd == SysSite.siteCd', backref='stk_ins')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'inCd': self.inCd,
            'inSeq': self.inSeq,          
            'inNo': self.inNo,
            'inDate': self.inDate,
            'lotNo': self.lotNo,
            'sn': self.sn,
            'inKind': self.inKind,
            'purcYn': self.purcYn,
            'inType': self.inType,
            'poCd': self.poCd,
            'partCd': self.partCd,
            'inQty': self.inQty,
            'inUnit': self.inUnit,
            'inAmt': self.inAmt,
            'currency': self.currency,
            'cmLoc': self.cmLoc,
            'whCd': self.whCd,
            'loc': self.loc,
            'bl': self.bl,
            'invoice': self.invoice,
            'inWarr': self.inWarr,
            'partRank': self.partRank,
            'svcStDate': self.svcStDate,
            'svcEdDate': self.svcEdDate,
            'stkType': self.stkType,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class StkLot(db.Model):
    __tablename__ = 'stk_lot'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.ForeignKeyConstraint(['siteCd', 'whCd'], ['mst_wh.siteCd', 'mst_wh.whCd']),
        db.Index('FK_mst_part_TO_stk_lot', 'siteCd', 'partCd'),
        db.Index('FK_mst_wh_TO_stk_lot', 'siteCd', 'whCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    lotNo = db.Column(db.String(20), primary_key=True, nullable=False)
    sn = db.Column(db.String(30))
    partCd = db.Column(db.String(10))
    whCd = db.Column(db.String(10))
    loc = db.Column(db.String(20))
    curQty = db.Column(db.Numeric(14, 2))
    docQty = db.Column(db.Numeric(14, 2))
    unit = db.Column(db.String(10))
    stkType = db.Column(db.String(10))
    posState = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(StkLot.siteCd == MstPart.siteCd, StkLot.partCd == MstPart.partCd)', backref='stk_lots')
    mst_wh = db.relationship('MstWh', primaryjoin='and_(StkLot.siteCd == MstWh.siteCd, StkLot.whCd == MstWh.whCd)', backref='stk_lots')
    sys_site = db.relationship('SysSite', primaryjoin='StkLot.siteCd == SysSite.siteCd', backref='stk_lots')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,            
            'lotNo': self.lotNo,
            'sn': self.sn,
            'partCd': self.partCd,
            'whCd': self.whCd,
            'loc': self.loc,
            'curQty': self.curQty,
            'docQty': self.docQty,
            'unit': self.unit,
            'stkType': self.stkType,
            'posState': self.posState,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkOutEtc(db.Model):
    __tablename__ = 'stk_out_etc'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'outCd', 'outSeq'], ['stk_out.siteCd', 'stk_out.outCd', 'stk_out.outSeq']),
        db.Index('FK_stk_out_TO_stk_out_etc', 'siteCd', 'outCd', 'outSeq')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    outEtcCd = db.Column(db.String(20), primary_key=True, nullable=False)
    outEtcSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    outEtcNo = db.Column(db.String(20))
    outEtcDate = db.Column(db.String(8))
    poCd = db.Column(db.String(20))
    outCd = db.Column(db.String(20))
    outSeq = db.Column(db.Integer)
    remark = db.Column(db.String(200))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_out = db.relationship('StkOut', primaryjoin='and_(StkOutEtc.siteCd == StkOut.siteCd, StkOutEtc.outCd == StkOut.outCd, StkOutEtc.outSeq == StkOut.outSeq)', backref='stk_out_etcs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,            
            'outEtcCd': self.outEtcCd,
            'outEtcSeq': self.outEtcSeq,
            'outEtcNo': self.outEtcNo,
            'outEtcDate': self.outEtcDate,
            'poCd': self.poCd,
            'outCd': self.outCd,
            'outSeq': self.outSeq,
            'remark': self.remark,
            'note': self.note,         
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkOutReq(db.Model):
    __tablename__ = 'stk_out_req'

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    reqCd = db.Column(db.String(20), primary_key=True, nullable=False)
    reqState = db.Column(db.String(10))
    reqDate = db.Column(db.String(8))
    reqUser = db.Column(db.String(20))
    sender = db.Column(db.String(50))
    senderPhone = db.Column(db.String(20))
    senderFax = db.Column(db.String(20))
    shipCustCd = db.Column(db.String(20))
    shipContact = db.Column(db.String(40))
    shipPhone = db.Column(db.String(20))
    shipAddress = db.Column(db.String(300))
    receiver = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='StkOutReq.siteCd == SysSite.siteCd', backref='stk_out_reqs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,            
            'reqCd': self.reqCd,
            'reqState': self.reqState,
            'reqDate': self.reqDate,
            'reqUser': self.reqUser,
            'sender': self.sender,
            'senderPhone': self.senderPhone,
            'senderFax': self.senderFax,
            'shipCustCd': self.shipCustCd,
            'shipContact': self.shipContact,
            'shipPhone': self.shipPhone,
            'shipAddress': self.shipAddress,
            'receiver': self.receiver,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkOutReqDtl(db.Model):
    __tablename__ = 'stk_out_req_dtl'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'partCd'], ['mst_part.siteCd', 'mst_part.partCd']),
        db.ForeignKeyConstraint(['siteCd', 'reqCd'], ['stk_out_req.siteCd', 'stk_out_req.reqCd']),
        db.Index('FK_mst_part_TO_stk_out_req_dtl', 'siteCd', 'partCd')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    reqCd = db.Column(db.String(20), primary_key=True, nullable=False)
    reqSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    partCd = db.Column(db.String(10))
    qty = db.Column(db.Numeric(14, 2))
    unit = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_part = db.relationship('MstPart', primaryjoin='and_(StkOutReqDtl.siteCd == MstPart.siteCd, StkOutReqDtl.partCd == MstPart.partCd)', backref='stk_out_req_dtls')
    stk_out_req = db.relationship('StkOutReq', primaryjoin='and_(StkOutReqDtl.siteCd == StkOutReq.siteCd, StkOutReqDtl.reqCd == StkOutReq.reqCd)', backref='stk_out_req_dtls')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,            
            'reqCd': self.reqCd,
            'reqSeq': self.reqSeq,
            'partCd': self.partCd,
            'qty': self.qty,
            'unit': self.unit,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkOutReqSn(db.Model):
    __tablename__ = 'stk_out_req_sn'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'lotNo'], ['stk_lot.siteCd', 'stk_lot.lotNo']),
        db.ForeignKeyConstraint(['siteCd', 'poCd'], ['pur_order.siteCd', 'pur_order.poCd']),
        db.ForeignKeyConstraint(['siteCd', 'reqCd'], ['stk_out_req.siteCd', 'stk_out_req.reqCd']),
        db.Index('FK_stk_lot_TO_stk_out_req_sn', 'siteCd', 'lotNo'),
        db.Index('FK_pur_order_TO_stk_out_req_sn', 'siteCd', 'poCd')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    reqCd = db.Column(db.String(20), primary_key=True, nullable=False)
    snSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    poCd = db.Column(db.String(20))
    poNo = db.Column(db.String(30))
    partCd = db.Column(db.String(10))
    lotNo = db.Column(db.String(20))
    sn = db.Column(db.String(30))
    qty = db.Column(db.Numeric(14, 2))
    unit = db.Column(db.String(10))
    loc = db.Column(db.String(20))
    awb = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_lot = db.relationship('StkLot', primaryjoin='and_(StkOutReqSn.siteCd == StkLot.siteCd, StkOutReqSn.lotNo == StkLot.lotNo)', backref='stk_out_req_sns')
    pur_order = db.relationship('PurOrder', primaryjoin='and_(StkOutReqSn.siteCd == PurOrder.siteCd, StkOutReqSn.poCd == PurOrder.poCd)', backref='stk_out_req_sns')
    stk_out_req = db.relationship('StkOutReq', primaryjoin='and_(StkOutReqSn.siteCd == StkOutReq.siteCd, StkOutReqSn.reqCd == StkOutReq.reqCd)', backref='stk_out_req_sns')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,            
            'reqCd': self.reqCd,
            'snSeq': self.snSeq,
            'poCd': self.poCd,
            'poNo': self.poNo,
            'partCd': self.partCd,
            'lotNo': self.lotNo,
            'sn': self.sn,
            'qty': self.qty,
            'unit': self.unit,
            'loc': self.loc,
            'awb': self.awb,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class StkReserveOut(db.Model):
    __tablename__ = 'stk_reserve_out'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'lotNo'], ['stk_lot.siteCd', 'stk_lot.lotNo']),
        db.Index('FK_stk_lot_TO_stk_reserve_out', 'siteCd', 'lotNo')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    roCd = db.Column(db.String(20), primary_key=True, nullable=False)
    roSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    resvDate = db.Column(db.String(8))
    resvUser = db.Column(db.String(20))
    lotNo = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_lot = db.relationship('StkLot', primaryjoin='and_(StkReserveOut.siteCd == StkLot.siteCd, StkReserveOut.lotNo == StkLot.lotNo)', backref='stk_reserve_outs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'roCd': self.roCd,
            'roSeq': self.roSeq,
            'resvDate': self.resvDate,
            'resvUser': self.resvUser,
            'lotNo': self.lotNo,            
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class StkOut(db.Model):
    __tablename__ = 'stk_out'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'custCd'], ['mst_cust.siteCd', 'mst_cust.custCd']),
        db.ForeignKeyConstraint(['siteCd', 'lotNo'], ['stk_lot.siteCd', 'stk_lot.lotNo']),
        db.ForeignKeyConstraint(['siteCd', 'poCd'], ['pur_order.siteCd', 'pur_order.poCd']),
        db.Index('FK_pur_order_TO_stk_out', 'siteCd', 'poCd'),
        db.Index('FK_mst_cust_TO_stk_out', 'siteCd', 'custCd'),
        db.Index('FK_stk_lot_TO_stk_out', 'siteCd', 'lotNo')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    outCd = db.Column(db.String(20), primary_key=True, nullable=False)
    outSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    outNo = db.Column(db.String(20))
    outDate = db.Column(db.String(8))
    lotNo = db.Column(db.String(20))
    sn = db.Column(db.String(30))
    outKind = db.Column(db.String(10))
    sellYn = db.Column(db.String(1))
    outType = db.Column(db.String(10))
    requester = db.Column(db.String(20))
    sender = db.Column(db.String(20))
    outQty = db.Column(db.Numeric(14, 2))
    outUnit = db.Column(db.String(10))
    whCd = db.Column(db.String(10))
    poCd = db.Column(db.String(20))
    custCd = db.Column(db.String(10))
    arrAddr = db.Column(db.String(150))
    recipient = db.Column(db.String(20))
    recipientTel = db.Column(db.String(20))
    transporter = db.Column(db.String(20))
    transporterTel = db.Column(db.String(20))
    receiptYn = db.Column(db.String(1))
    note = db.Column(db.String(200))
    note2 = db.Column(db.String(200))
    note3 = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_cust = db.relationship('MstCust', primaryjoin='and_(StkOut.siteCd == MstCust.siteCd, StkOut.custCd == MstCust.custCd)', backref='stk_outs')
    stk_lot = db.relationship('StkLot', primaryjoin='and_(StkOut.siteCd == StkLot.siteCd, StkOut.lotNo == StkLot.lotNo)', backref='stk_outs')
    pur_order = db.relationship('PurOrder', primaryjoin='and_(StkOut.siteCd == PurOrder.siteCd, StkOut.poCd == PurOrder.poCd)', backref='stk_outs')
    sys_site = db.relationship('SysSite', primaryjoin='StkOut.siteCd == SysSite.siteCd', backref='stk_outs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'outCd': self.outCd,
            'outSeq': self.outSeq,
            'outNo': self.outNo,
            'outDate': self.outDate,
            'lotNo': self.lotNo,
            'sn': self.sn,
            'outKind': self.outKind,
            'sellYn': self.sellYn,
            'outType': self.outType,
            'requester': self.requester,
            'sender': self.sender,
            'outQty': self.outQty,
            'outUnit': self.outUnit,
            'whCd': self.whCd,
            'poCd': self.poCd,
            'custCd': self.custCd,
            'arrAddr': self.arrAddr,
            'recipient': self.recipient,
            'recipientTel': self.recipientTel,
            'transporter': self.transporter,
            'transporterTel': self.transporterTel,
            'receiptYn': self.receiptYn,           
            'note': self.note,
            'note2': self.note2,
            'note3': self.note3,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class StkSell(db.Model):
    __tablename__ = 'stk_sell'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'prjCd'], ['mst_project.siteCd', 'mst_project.prjCd']),
        db.ForeignKeyConstraint(['siteCd', 'custCd'], ['mst_cust.siteCd', 'mst_cust.custCd']),
        db.ForeignKeyConstraint(['siteCd', 'outCd', 'outSeq'], ['stk_out.siteCd', 'stk_out.outCd', 'stk_out.outSeq']),
        db.ForeignKeyConstraint(['siteCd', 'poCd'], ['pur_order.siteCd', 'pur_order.poCd']),
        db.Index('FK_mst_project_TO_stk_sell', 'siteCd', 'prjCd'),
        db.Index('FK_mst_cust_TO_stk_sell', 'siteCd', 'custCd'),
        db.Index('FK_pur_order_TO_stk_sell', 'siteCd', 'poCd'),
        db.Index('FK_stk_out_TO_stk_sell', 'siteCd', 'outCd', 'outSeq')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    sellCd = db.Column(db.String(20), primary_key=True, nullable=False)
    sellSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    sellNo = db.Column(db.String(20))
    sellDate = db.Column(db.String(8))
    sellState = db.Column(db.String(10))
    psvType = db.Column(db.String(10))
    serviceYn = db.Column(db.String(1))
    poCd = db.Column(db.String(20))
    custCd = db.Column(db.String(10))
    prjCd = db.Column(db.String(20))
    project = db.Column(db.String(150))
    manager = db.Column(db.String(20))
    unitAmt = db.Column(db.Numeric(14, 2))
    taxAmt = db.Column(db.Numeric(14, 2))
    sellAmt = db.Column(db.Numeric(14, 2))
    currency = db.Column(db.String(10))
    tempServiceAmt = db.Column(db.Numeric(14, 2))
    tempExcRate = db.Column(db.Numeric(14, 2))
    tempWonAmt = db.Column(db.Numeric(14, 2))
    outCd = db.Column(db.String(20))
    outSeq = db.Column(db.Integer)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    mst_project = db.relationship('MstProject', primaryjoin='and_(StkSell.siteCd == MstProject.siteCd, StkSell.prjCd == MstProject.prjCd)', backref='stk_sells')
    mst_cust = db.relationship('MstCust', primaryjoin='and_(StkSell.siteCd == MstCust.siteCd, StkSell.custCd == MstCust.custCd)', backref='stk_sells')
    stk_out = db.relationship('StkOut', primaryjoin='and_(StkSell.siteCd == StkOut.siteCd, StkSell.outCd == StkOut.outCd, StkSell.outSeq == StkOut.outSeq)', backref='stk_sells')
    pur_order = db.relationship('PurOrder', primaryjoin='and_(StkSell.siteCd == PurOrder.siteCd, StkSell.poCd == PurOrder.poCd)', backref='stk_sells')
    sys_site = db.relationship('SysSite', primaryjoin='StkSell.siteCd == SysSite.siteCd', backref='stk_sells')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'sellCd': self.sellCd,
            'sellSeq': self.sellSeq,
            'sellNo': self.sellNo,
            'sellDate': self.sellDate,
            'sellState': self.sellState,
            'psvType': self.psvType,
            'serviceYn': self.serviceYn,
            'poCd': self.poCd,
            'custCd': self.custCd,
            'prjCd': self.prjCd,
            'project': self.project,
            'manager': self.manager,
            'unitAmt': self.unitAmt,
            'taxAmt': self.taxAmt,
            'sellAmt': self.sellAmt,
            'currency': self.currency,
            'tempServiceAmt': self.tempServiceAmt,
            'tempExcRate': self.tempExcRate,
            'tempWonAmt': self.tempWonAmt,
            'outCd': self.outCd,
            'outSeq': self.outSeq,             
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class StkSellMapping(db.Model):
    __tablename__ = 'stk_sell_mapping'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'sellCd', 'sellSeq'], ['stk_sell.siteCd', 'stk_sell.sellCd', 'stk_sell.sellSeq']),
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    sellCd = db.Column(db.String(20), primary_key=True, nullable=False)
    sellSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    seq = db.Column(db.Integer, primary_key=True, nullable=False)
    svcSellCd = db.Column(db.String(20))
    svcSellSeq = db.Column(db.Integer)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    stk_sell = db.relationship('StkSell', primaryjoin='and_(StkSellMapping.siteCd == StkSell.siteCd, StkSellMapping.sellCd == StkSell.sellCd, StkSellMapping.sellSeq == StkSell.sellSeq)', backref='stk_sell_mappings')
    sys_site = db.relationship('SysSite', primaryjoin='StkSellMapping.siteCd == SysSite.siteCd', backref='stk_sell_mappings')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'sellCd': self.sellCd,
            'sellSeq': self.sellSeq,
            'seq': self.seq,
            'svcSellCd': self.svcSellCd,
            'svcSellSeq': self.svcSellSeq,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SysAuth(db.Model):
    __tablename__ = 'sys_auth'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'roleCd'], ['sys_role.siteCd', 'sys_role.roleCd']),
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    roleCd = db.Column(db.String(10), primary_key=True, nullable=False)
    menuCd = db.Column(db.ForeignKey('sys_menu.menuCd'), primary_key=True, nullable=False, index=True)    
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_menu = db.relationship('SysMenu', primaryjoin='SysAuth.menuCd == SysMenu.menuCd', backref='sys_auths')
    sys_role = db.relationship('SysRole', primaryjoin='and_(SysAuth.siteCd == SysRole.siteCd, SysAuth.roleCd == SysRole.roleCd)', backref='sys_auths')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'roleCd': self.roleCd,
            'menuCd': self.menuCd,            
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysAuthObj(db.Model):
    __tablename__ = 'sys_auth_obj'
    __table_args__ = (
        db.ForeignKeyConstraint(['menuCd', 'objSeq'], ['sys_menu_obj.menuCd', 'sys_menu_obj.objSeq']),
        db.ForeignKeyConstraint(['siteCd', 'roleCd', 'menuCd'], ['sys_auth.siteCd', 'sys_auth.roleCd', 'sys_auth.menuCd']),
        db.Index('FK_sys_menu_obj_TO_sys_auth_obj', 'menuCd', 'objSeq')
    )

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    roleCd = db.Column(db.String(10), primary_key=True, nullable=False)
    menuCd = db.Column(db.String(10), primary_key=True, nullable=False)
    objSeq = db.Column(db.Integer, primary_key=True, nullable=False)   
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_menu_obj = db.relationship('SysMenuObj', primaryjoin='and_(SysAuthObj.menuCd == SysMenuObj.menuCd, SysAuthObj.objSeq == SysMenuObj.objSeq)', backref='sys_auth_objs')
    sys_auth = db.relationship('SysAuth', primaryjoin='and_(SysAuthObj.siteCd == SysAuth.siteCd, SysAuthObj.roleCd == SysAuth.roleCd, SysAuthObj.menuCd == SysAuth.menuCd)', backref='sys_auth_objs')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'roleCd': self.roleCd,
            'menuCd': self.menuCd,
            'objSeq': self.objSeq,        
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysConn(db.Model):
    __tablename__ = 'sys_conn'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'userCd'], ['sys_user.siteCd', 'sys_user.userCd']),
        db.Index('FK_sys_user_TO_sys_conn', 'siteCd', 'userCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    connCd = db.Column(db.String(20), primary_key=True, nullable=False)
    userCd = db.Column(db.String(20))
    connState = db.Column(db.String(10))
    hostName = db.Column(db.String(80))
    ipAddr = db.Column(db.String(20))
    macAddr = db.Column(db.String(20))
    loginTime = db.Column(db.DateTime)
    logoutTime = db.Column(db.DateTime)
    checkTime = db.Column(db.DateTime)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_user = db.relationship('SysUser', primaryjoin='and_(SysConn.siteCd == SysUser.siteCd, SysConn.userCd == SysUser.userCd)', backref='sys_conns')
    sys_site = db.relationship('SysSite', primaryjoin='SysConn.siteCd == SysSite.siteCd', backref='sys_conns')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'connCd': self.connCd,
            'userCd': self.userCd,
            'connState': self.connState,
            'hostName': self.hostName,
            'ipAddr': self.ipAddr,
            'macAddr': self.macAddr,
            'loginTime': None if self.loginTime is None else self.loginTime if self.loginTime == '0000-00-00 00:00:00' else self.loginTime.strftime('%Y-%m-%d %H:%M:%S'),
            'logoutTime': None if self.logoutTime is None else self.logoutTime if self.logoutTime == '0000-00-00 00:00:00' else self.logoutTime.strftime('%Y-%m-%d %H:%M:%S'),
            'checkTime': None if self.checkTime is None else self.checkTime if self.checkTime == '0000-00-00 00:00:00' else self.checkTime.strftime('%Y-%m-%d %H:%M:%S'),
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysMajor(db.Model):
    __tablename__ = 'sys_major'

    majorCd = db.Column(db.String(10), primary_key=True)
    majorNm = db.Column(db.String(40))
    systemYn = db.Column(db.String(1))
    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), index=True)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='SysMajor.siteCd == SysSite.siteCd', backref='sys_majors')

    def to_json(self):
        json = {
            'majorCd': self.majorCd,
            'majorNm': self.majorNm,
            'systemYn': self.systemYn,
            'siteCd': self.siteCd,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SysMenu(db.Model):
    __tablename__ = 'sys_menu'

    menuCd = db.Column(db.String(10), primary_key=True)
    pMenuCd = db.Column(db.String(10))
    menuNm = db.Column(db.String(40))
    dispOrder = db.Column(db.Integer)
    menuLv = db.Column(db.Integer)
    systemType = db.Column(db.String(10))
    menuType = db.Column(db.String(10))
    assemblyNm = db.Column(db.String(40))
    namespaceNm = db.Column(db.String(40))
    formNm = db.Column(db.String(40))    
    imgIdx = db.Column(db.Integer)
    roleType = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    def to_json(self):
        json = {
            'menuCd': self.menuCd,
            'pMenuCd': self.pMenuCd,
            'menuNm': self.menuNm,
            'dispOrder': self.dispOrder,
            'menuLv': self.menuLv,
            'systemType': self.systemType,
            'menuType': self.menuType,
            'assemblyNm': self.assemblyNm,
            'namespaceNm': self.namespaceNm,
            'formNm': self.formNm,
            'imgIdx': self.imgIdx,
            'roleType': self.roleType,       
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysMenuObj(db.Model):
    __tablename__ = 'sys_menu_obj'

    menuCd = db.Column(db.ForeignKey('sys_menu.menuCd'), primary_key=True, nullable=False)
    objSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    objNm = db.Column(db.String(30))
    objText = db.Column(db.String(80))
    dispOrder = db.Column(db.Integer)
    imgIdx = db.Column(db.Integer)
    objPos = db.Column(db.Integer)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False, server_default=db.FetchedValue())
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_menu = db.relationship('SysMenu', primaryjoin='SysMenuObj.menuCd == SysMenu.menuCd', backref='sys_menu_objs')

    def to_json(self):
        json = {
            'menuCd': self.menuCd,
            'objSeq': self.objSeq,
            'objNm': self.objNm,
            'objText': self.objText,
            'dispOrder': self.dispOrder,
            'imgIdx': self.imgIdx,
            'objPos': self.objPos,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SysMinor(db.Model):
    __tablename__ = 'sys_minor'

    majorCd = db.Column(db.ForeignKey('sys_major.majorCd'), primary_key=True, nullable=False)
    minorCd = db.Column(db.String(10), primary_key=True, nullable=False)
    pMajorCd = db.Column(db.String(10))
    pMinorCd = db.Column(db.String(10))
    minorNm = db.Column(db.String(40))
    ref1 = db.Column(db.String(50))
    ref2 = db.Column(db.String(50))
    ref3 = db.Column(db.String(50))
    dispOrder = db.Column(db.Integer)
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_major = db.relationship('SysMajor', primaryjoin='SysMinor.majorCd == SysMajor.majorCd', backref='sys_minors')

    def to_json(self):
        json = {
            'majorCd': self.majorCd,
            'minorCd': self.minorCd,
            'pMajorCd': self.pMajorCd,
            'pMinorCd': self.pMinorCd,
            'minorNm': self.minorNm,
            'ref1': self.ref1,
            'ref2': self.ref2,
            'ref3': self.ref3,
            'dispOrder': self.dispOrder,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SysRole(db.Model):
    __tablename__ = 'sys_role'

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    roleCd = db.Column(db.String(10), primary_key=True, nullable=False)
    roleNm = db.Column(db.String(40))
    roleType = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_site = db.relationship('SysSite', primaryjoin='SysRole.siteCd == SysSite.siteCd', backref='sys_roles')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'siteNm': self.sys_site.siteNm,
            'roleCd': self.roleCd,
            'roleNm': self.roleNm,
            'roleType': self.roleType,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json


class SysSite(db.Model):
    __tablename__ = 'sys_site'

    siteCd = db.Column(db.String(5), primary_key=True)
    siteNm = db.Column(db.String(40))
    contact = db.Column(db.String(40))
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    corpNo = db.Column(db.String(20))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'siteNm': self.siteNm,
            'contact': self.contact,
            'phone': self.phone,
            'fax': self.fax,
            'corpNo': self.corpNo,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysTranMsg(db.Model):
    __tablename__ = 'sys_tran_msg'

    siteCd = db.Column(db.String(5), primary_key=True, nullable=False)
    msgDate = db.Column(db.String(8), primary_key=True, nullable=False)
    msgSeq = db.Column(db.Integer, primary_key=True, nullable=False)
    fConnCd = db.Column(db.String(20))
    tConnCd = db.Column(db.String(20))
    protocol = db.Column(db.String(100))
    message = db.Column(db.String(1000))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'msgDate': self.msgDate,
            'msgSeq': self.msgSeq,
            'fConnCd': self.fConnCd,
            'tConnCd': self.tConnCd,
            'protocol': self.protocol,
            'message': self.message,            
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class SysUser(db.Model):
    __tablename__ = 'sys_user'
    __table_args__ = (
        db.ForeignKeyConstraint(['siteCd', 'roleCd'], ['sys_role.siteCd', 'sys_role.roleCd']),
        db.Index('FK_sys_role_TO_sys_user', 'siteCd', 'roleCd')
    )

    siteCd = db.Column(db.ForeignKey('sys_site.siteCd'), primary_key=True, nullable=False)
    userCd = db.Column(db.String(20), primary_key=True, nullable=False)
    userNm = db.Column(db.String(40))
    pwd = db.Column(db.String(120))
    roleCd = db.Column(db.String(10))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    sys_role = db.relationship('SysRole', primaryjoin='and_(SysUser.siteCd == SysRole.siteCd, SysUser.roleCd == SysRole.roleCd)', backref='sys_users')
    sys_site = db.relationship('SysSite', primaryjoin='SysUser.siteCd == SysSite.siteCd', backref='sys_users')

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'siteNm': self.sys_site.siteNm,
            'userCd': self.userCd,
            'userNm': self.userNm,
            'pwd': self.pwd,
            'roleCd': self.roleCd,
            'roleNm': self.sys_role.roleNm,
            'roleType': self.sys_role.roleType,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json  

    def to_json_simple(self):
        json = {
            'siteCd': self.siteCd,
            'siteNm': self.sys_site.siteNm,
            'userCd': self.userCd,
            'userNm': self.userNm,
            'pwd': self.pwd,         
            'roleCd': self.roleCd,
            'roleNm': self.sys_role.roleNm,
            'note': self.note,
            'state': self.state,
            'roleType': self.sys_role.roleType
        }
        return json  

class TstSite(db.Model):
    __tablename__ = 'tst_site'

    siteCd = db.Column(db.String(5), primary_key=True)
    siteNm = db.Column(db.String(40))
    note = db.Column(db.String(200))
    state = db.Column(db.String(1), nullable=False)
    regUser = db.Column(db.String(20), nullable=False)
    regDate = db.Column(db.DateTime, nullable=False)
    modUser = db.Column(db.String(20))
    modDate = db.Column(db.DateTime)

    def to_json(self):
        json = {
            'siteCd': self.siteCd,
            'siteNm': self.siteNm,
            'note': self.note,
            'state': self.state,
            'regUser': self.regUser,
            'regDate': None if self.regDate is None else self.regDate if self.regDate == '0000-00-00 00:00:00' else self.regDate.strftime('%Y-%m-%d %H:%M:%S'),
            'modUser': self.modUser,
            'modDate': None if self.modDate is None else self.modDate if self.modDate == '0000-00-00 00:00:00' else self.modDate.strftime('%Y-%m-%d %H:%M:%S')
        }
        return json

class TmpRawDatum(db.Model):
    __tablename__ = 'tmp_raw_data'

    IDX = Column(Integer, primary_key=True)
    A = Column(String(50))
    B = Column(String(50))
    C = Column(String(50))
    D = Column(String(50))
    E = Column(String(50))
    F = Column(String(50))
    G = Column(String(50))
    H = Column(String(50))
    I = Column(String(50))
    J = Column(String(50))
    K = Column(String(50))
    L = Column(String(100))
    M = Column(String(100))
    N = Column(String(50))
    O = Column(String(50))
    P = Column(String(50))
    Q = Column(String(50))
    R = Column(String(50))
    S = Column(String(50))
    T = Column(String(50))
    U = Column(String(50))
    V = Column(String(50))
    W = Column(String(50))
    X = Column(String(50))
    Y = Column(String(50))
    Z = Column(String(50))
    AA = Column(String(50))
    AB = Column(String(100))
    AC = Column(String(50))
    AD = Column(String(200))
    AE = Column(String(200))
    AF = Column(String(200))
    AG = Column(String(50))
    AH = Column(String(50))
    AI = Column(String(50))
    AJ = Column(String(50))
    AK = Column(String(50))
    AL = Column(String(50))
    AM = Column(String(50))
    AN = Column(String(50))
    AO = Column(String(50))
    AP = Column(String(50))
    AQ = Column(String(50))
    AR = Column(String(50))
    AS = Column(String(50))
    AT = Column(String(50))
    AU = Column(String(200))
    AV = Column(String(50))
    AW = Column(String(50))
    AX = Column(String(50))
    AY = Column(String(50))
    AZ = Column(String(50))
    BA = Column(String(50))
    BB = Column(String(50))
    BC = Column(String(50))
    BD = Column(String(50))
    BE = Column(String(50))
    BF = Column(String(50))
    BG = Column(String(50))
    BH = Column(String(100))
    BI = Column(String(100))
    BJ = Column(String(50))
    BK = Column(String(50))
    BL = Column(String(50))
    BM = Column(String(50))
    BN = Column(String(50))
    BO = Column(String(50))
    BP = Column(String(50))
    BQ = Column(String(50))
    BR = Column(String(50))
    BS = Column(String(50))
    BT = Column(String(50))
    BU = Column(String(50))
    BV = Column(String(50))
    BW = Column(String(50))
    BX = Column(String(50))
    BY = Column(String(50))
    BZ = Column(String(50))
    CA = Column(String(50))
    CB = Column(String(50))
    CC = Column(String(50))
    CD = Column(String(50))
    CE = Column(String(50))
    CF = Column(String(50))
    CG = Column(String(50))
    CH = Column(String(50))
    CI = Column(String(50))
    CJ = Column(String(50))
    CK = Column(String(50))
    CL = Column(String(50))
    CM = Column(String(50))
    CN = Column(String(50))
    CO = Column(String(50))
    CP = Column(String(50))
    CQ = Column(String(100))
    CR = Column(String(100))
    CS = Column(String(50))
    CT = Column(String(50))
    CU = Column(String(50))
    CV = Column(String(50))
    CW = Column(String(50))
    CX = Column(String(50))
    CY = Column(String(50))
    CZ = Column(String(50))
    DA = Column(String(50))
    DB = Column(String(50))
    DC = Column(String(50))
    DD = Column(String(50))
    DE = Column(String(50))
    DF = Column(String(50))
    DG = Column(String(50))
    DH = Column(String(50))
    partCd = Column(String(20))
    partNm = Column(String(80))
    poCd = Column(String(20))
    inCd = Column(String(20))
    inSeq = Column(Integer)
    lotNo = Column(String(20))
    lotNoMulti = Column(String())
    outCd = Column(String(20))
    outSeq = Column(Integer)
    sellCd = Column(String(20))
    sellSeq = Column(Integer)
    posCd = Column(String(20))    
    cmCd = Column(String(20))
    orgPosCd = Column(String(20))    
    orgCmCd = Column(String(20))    

    def to_json(self):
        json = {
            'IDX': self.IDX,
            '0A': self.A,
            '0B': self.B,
            '0C': self.C,
            '0D': self.D,
            '0E': self.E,
            '0F': self.F,
            '0G': self.G,
            '0H': self.H,
            '0I': self.I,
            '0J': self.J,
            '0K': self.K,
            '0L': self.L,
            '0M': self.M,
            '0N': self.N,
            '0O': self.O,
            '0P': self.P,
            '0Q': self.Q,
            '0R': self.R,
            '0S': self.S,
            '0T': self.T,
            '0U': self.U,
            '0V': self.V,
            '0W': self.W,
            '0X': self.X,
            '0Y': self.AY,
            '0Z': self.Z,
            'AA': self.AA,
            'AB': self.AB,
            'AC': self.AC,
            'AD': self.AD,
            'AE': self.AE,
            'AF': self.AF,
            'AG': self.AG,
            'AH': self.AH,
            'AI': self.AI,
            'AJ': self.AJ,
            'AK': self.AK,
            'AL': self.AL,
            'AM': self.AM,
            'AN': self.AN,
            'AO': self.AO,
            'AP': self.AP,
            'AQ': self.AQ,
            'AR': self.AR,
            'AS': self.AS,
            'AT': self.AT,
            'AU': self.AU,
            'AV': self.AV,
            'AW': self.AW,
            'AX': self.AX,
            'AY': self.AY,
            'AZ': self.AZ,
            'BA': self.BA,
            'BB': self.BB,
            'BC': self.BC,
            'BD': self.BD,
            'BE': self.BE,
            'BF': self.BF,
            'BG': self.BG,
            'BH': self.BH,
            'BI': self.BI,
            'BJ': self.BJ,
            'BK': self.BK,
            'BL': self.BL,
            'BM': self.BM,
            'BN': self.BN,
            'BO': self.BO,
            'BP': self.BP,
            'BQ': self.BQ,
            'BR': self.BR,
            'BS': self.BS,
            'BT': self.BT,
            'BU': self.BU,
            'BV': self.BV,
            'BW': self.BW,
            'BX': self.BX,
            'BY': self.BY,
            'BZ': self.BZ,
            'CA': self.CA,
            'CB': self.CB,
            'CC': self.CC,
            'CD': self.CD,
            'CE': self.CE,
            'CF': self.CF,
            'CG': self.CG,
            'CH': self.CH,
            'CI': self.CI,
            'CJ': self.CJ,
            'CK': self.CK,
            'CL': self.CL,
            'CM': self.CM,
            'CN': self.CN,
            'CO': self.CO,
            'CP': self.CP,
            'CQ': self.CQ,
            'CR': self.CR,
            'CS': self.CS,
            'CT': self.CT,
            'CU': self.CU,
            'CV': self.CV,
            'CW': self.CW,
            'CX': self.CX,
            'CY': self.CY,
            'CZ': self.CZ,
            'DA': self.DA,
            'DB': self.DB,
            'DC': self.DC,
            'DD': self.DD,
            'DE': self.DE,
            'DF': self.DF,
            'DG': self.DG,
            'DH': self.DH,
            'partCd': self.partCd,
            'partNm': self.partNm,
            'poCd': self.poCd,
            'inCd': self.inCd,
            'inSeq': self.inSeq,
            'lotNo': self.lotNo,
            'lotNoMulti': self.lotNoMulti,
            'outCd': self.outCd,
            'outSeq': self.outSeq,
            'sellCd': self.sellCd,
            'sellSeq': self.sellSeq,
            'posCd': self.posCd,            
            'cmCd': self.cmCd,
            'orgPosCd': self.orgPosCd,
            'orgCmCd': self.orgCmCd
        }
        return json  

class TmpRawDatumA(db.Model):
    __tablename__ = 'tmp_raw_data_a'

    IDX = Column(Integer, primary_key=True)
    A = Column(String(50))
    B = Column(String(50))
    C = Column(String(100))
    D = Column(String(50))
    E = Column(String(50))
    F = Column(String(50))
    G = Column(String(50))
    H = Column(String(50))
    I = Column(String(50))
    J = Column(String(50))
    K = Column(String(50))
    L = Column(String(50))
    M = Column(String(50))
    N = Column(String(100))
    O = Column(String(200))
    P = Column(String(50))
    Q = Column(String(50))
    R = Column(String(200))    
    partCd = Column(String(20))
    partNm = Column(String(80))
    poCd = Column(String(20))
    inCd = Column(String(20))
    inSeq = Column(Integer)
    lotNo = Column(String(20))
    lotNoMulti = Column(String())
    outCd = Column(String(20))
    outSeq = Column(Integer)
    sellCd = Column(String(20))
    sellSeq = Column(Integer)
    posCd = Column(String(20))
    posSeq = Column(Integer)
    cmCd = Column(String(20))
    cmSeq = Column(Integer)

    def to_json(self):
        json = {
            'IDX': self.IDX,
            '0A': self.A,
            '0B': self.B,
            '0C': self.C,
            '0D': self.D,
            '0E': self.E,
            '0F': self.F,
            '0G': self.G,
            '0H': self.H,
            '0I': self.I,
            '0J': self.J,
            '0K': self.K,
            '0L': self.L,
            '0M': self.M,
            '0N': self.N,
            '0O': self.O,
            '0P': self.P,
            '0Q': self.Q,
            '0R': self.R,
            'partCd': self.partCd,
            'partNm': self.partNm,
            'poCd': self.poCd,
            'inCd': self.inCd,
            'inSeq': self.inSeq,
            'lotNo': self.lotNo,
            'lotNoMulti': self.lotNoMulti,
            'outCd': self.outCd,
            'outSeq': self.outSeq,
            'sellCd': self.sellCd,
            'sellSeq': self.sellSeq,
            'posCd': self.posCd,
            'cmCd': self.cmCd
        }
        return json  