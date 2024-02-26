# -- coding: utf-8 -- 

import os
import simplejson

from flask import jsonify, request, flash, url_for, app, current_app, json
from werkzeug.utils import secure_filename, redirect

import config
import datetime
from app import db, get_locale
from app.models_bswms import *
from app.main.cipherutil import CipherAgent
from dateutil import parser
from sqlalchemy import func, literal, exc
from sqlalchemy.orm import aliased
from flask_babel import gettext
import pymysql
from app.main.awsutil import awsS3

from . import main

@main.route('/api/chkDb', methods=['GET'])
def chk_db():

    dbType = os.environ.get('FLASK_ENV')
    try:
        db.session.query("1").from_statement(db.text("SELECT 1")).first()
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000'),
                'db' : dbType
            }
        })
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 3100,
                'msg' : gettext('3100'),
                'db' : dbType,
                'msg2': str(e)
            }
        })

@main.route('/api/chkKeyCode', methods=['POST'])
def chk_key_code():
    json_data = json.loads(request.data, strict=False)    
    tableNm = json_data.get('tableNm')
    fieldNm = json_data.get('fieldNm')
    siteCd = json_data.get('siteCd')    
    code = json_data.get('code')    
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "select count(*) as cnt \
             from " + tableNm + " \
            where 1 = 1 "
    if tableNm != 'sys_site':
        sql += "and siteCd = '" + siteCd + "' "
    sql += "and " + fieldNm + " = '" + code + "' \
            and state = 'R';"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['cnt'] = tr[0]

        data[index] = dic

    return jsonify({'chk': data})

@main.route('/api/selSysUserControl', methods=['POST'])
def select_sys_user_control():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    flag = json_data.get('flag')
    code = json_data.get('code') or ''
    name = json_data.get('name') or ''

    if flag == 'Comm':        
        data = db.session.query(SysMinor.minorCd.label('code'), SysMinor.minorNm.label('name')
                            , SysMinor.pMajorCd, SysMinor.pMinorCd, SysMinor.ref1, SysMinor.ref2, SysMinor.ref3, SysMinor.dispOrder, SysMinor.note, SysMinor.majorCd) \
                        .filter(SysMajor.majorCd == SysMinor.majorCd, SysMajor.state == 'R', SysMinor.state == 'R') \
                        .filter(SysMinor.majorCd.like(json_data.get('majorCd') + '%')) \
                        .filter(SysMinor.minorCd.like('%' + code + '%') | SysMinor.minorNm.like('%' + name + '%'))                        
        if json_data.get('ref1') is not None:
            data = data.filter(SysMinor.ref1 == json_data.get('ref1'))
        if json_data.get('ref2') is not None:
            data = data.filter(SysMinor.ref2 == json_data.get('ref2'))
        if json_data.get('ref3') is not None:
            data = data.filter(SysMinor.ref3 == json_data.get('ref3'))
        data= data.order_by(SysMinor.dispOrder.asc())
        return jsonify({                
                'data': [{'chk': '0','code': d[0],'name': d[1],'pMajorCd': d[2],'pMinorCd': d[3],'ref1': d[4],'ref2': d[5],'ref3': d[6],'dispOrder': d[7],'note': d[8],'majorCd': d[9]} for d in data]
            })        

    elif flag == 'Site':
        data = db.session.query(SysSite.siteCd, SysSite.siteNm, SysSite.contact, SysSite.phone, SysSite.fax, SysSite.corpNo, SysSite.note) \
                        .filter(SysSite.siteCd.like('%' + code + '%') | SysSite.siteNm.like('%' + name + '%')) \
                        .filter(SysSite.state=='R') \
                        .order_by(SysSite.siteCd.asc())
        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'contact': d[2],'phone': d[3],'fax': d[4],'corpNo': d[5],'note': d[6]} for d in data]
            })        

    elif flag == 'User':
        data = db.session.query(SysUser.userCd, SysUser.userNm, SysUser.roleCd, SysUser.note) \
                        .filter(SysUser.siteCd == siteCd, SysUser.state == 'R')

        if json_data.get('roleCd') is not None:
            data = data.filter(SysUser.roleCd == json_data.get('roleCd'))
        
        data = data.filter(SysUser.userCd.like('%' + code + '%') | SysUser.userNm.like('%' + name + '%')).order_by(SysUser.userCd)

        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'roleCd': d[2],'note': d[3]} for d in data]
            })        

    elif flag == 'Role':
        data = db.session.query(SysRole.roleCd, SysRole.roleNm, SysRole.note) \
                        .filter(SysRole.siteCd == siteCd, SysRole.state == 'R') \
                        .filter(SysRole.roleCd.like('%' + code + '%') | SysRole.roleNm.like('%' + name + '%'))
        if json_data.get('roleType') is not None:
            data = data.filter(SysRole.roleType >= json_data.get('roleType'))
        data = data.order_by(SysRole.roleCd)

        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'note': d[2]} for d in data]
            }) 

    elif flag == 'Cust':
        alCustType = aliased(SysMinor)

        data = db.session.query(MstCust.custCd, MstCust.custNm, MstCust.custNmEn, MstCust.custAbb, MstCust.custType, MstCust.varId, MstCust.sellYn, MstCust.purcYn, \
                                MstCust.address1, MstCust.address2, MstCust.address3, MstCust.city, MstCust.province, MstCust.country, MstCust.contact, \
                                MstCust.phone, MstCust.fax, MstCust.corpNo, MstCust.note, MstCust.custLocType, alCustType.minorNm.label('custLocTypeNm'), MstCust.zipCode) \
                        .outerjoin(alCustType, alCustType.minorCd == MstCust.custLocType) \
                        .filter(alCustType.majorCd == 'C0009') \
                        .filter(MstCust.siteCd == siteCd, MstCust.state == 'R') \
                        .filter(MstCust.custCd.like('%' + code + '%') | MstCust.custNm.like('%' + name + '%') | MstCust.custNmEn.like('%' + name + '%') | MstCust.varId.like('%' + code + '%'))
        if json_data.get('custType') is not None:
            data = data.filter(MstCust.custType.like('%' + json_data.get('custType') + '%'))
        if json_data.get('custLocType') is not None:
            data = data.filter(MstCust.custLocType == json_data.get('custLocType'))
        if json_data.get('varId') is not None:
            data = data.filter(MstCust.varId == json_data.get('varId'))
        if json_data.get('sellYn') is not None:
            data = data.filter(MstCust.sellYn == json_data.get('sellYn'))
        if json_data.get('purcYn') is not None:
            data = data.filter(MstCust.purcYn == json_data.get('purcYn'))
        data = data.order_by(MstCust.custCd)

        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'nameEn': d[2],'custAbb': d[3],'custType': d[4],'varId': d[5],'sellYn': d[6],'purcYn': d[7],'address1': d[8],'address2': d[9],'address3': d[10],'city': d[11],'province': d[12],'country': d[13],'contact': d[14],'phone': d[15],'fax': d[16],'corpNo': d[17],'note': d[18],'custLocType': d[19],'custLocTypeNm': d[20],'zipCode': d[21]} for d in data]
            }) 

    elif flag == 'Part':
        alPartKind = aliased(SysMinor)
        alPartType1 = aliased(SysMinor)
        alPartType2 = aliased(SysMinor)
        alPartType3 = aliased(SysMinor)

        data = db.session.query(MstPart.partCd, MstPart.partNm, \
                                MstPart.partKind, alPartKind.minorNm.label('partKindNm'), \
                                MstPart.partType1, alPartType1.minorNm.label('partType1Nm'), \
                                MstPart.partType2, alPartType2.minorNm.label('partType2Nm'), \
                                MstPart.partType3, alPartType3.minorNm.label('partType3Nm'), \
                                MstPart.partSpec, MstPart.partUnit, MstPart.currency, MstPart.note) \
                        .filter(MstPart.siteCd == siteCd, MstPart.state == 'R') \
                        .filter(MstPart.partCd.like('%' + code + '%') | MstPart.partNm.like('%' + name + '%')) \
                        .outerjoin(alPartKind, MstPart.partKind == alPartKind.minorCd) \
                        .filter(alPartKind.majorCd == 'C0003') \
                        .outerjoin(alPartType1, MstPart.partType1 == alPartType1.minorCd) \
                        .filter(alPartType1.majorCd == 'C0004') \
                        .outerjoin(alPartType2, MstPart.partType2 == alPartType2.minorCd) \
                        .filter(alPartType2.majorCd == 'C0005') \
                        .outerjoin(alPartType3, MstPart.partType3 == alPartType3.minorCd) \
                        .filter(alPartType3.majorCd == 'C0006')
        if json_data.get('partKind') is not None:
            data = data.filter(MstPart.partKind == json_data.get('partKind'))
        if json_data.get('partType1') is not None:
            data = data.filter(MstPart.partType1 == json_data.get('partType1'))
        if json_data.get('partType2') is not None:
            data = data.filter(MstPart.partType2 == json_data.get('partType2'))
        if json_data.get('partType3') is not None:
            data = data.filter(MstPart.partType3 == json_data.get('partType3'))
        data = data.order_by(MstPart.partCd)

        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'partKind': d[2],'partKindNm': d[3],'partType1': d[4],'partType1Nm': d[5],'partType2': d[6], \
                        'partType2Nm': d[7],'partType3': d[8],'partType3Nm': d[9],'partSpec': d[10],'partUnit': d[11],'currency': d[12],'note': d[13]} for d in data]
            }) 

    elif flag == 'Warehouse':
        data = db.session.query(MstWh.whCd, MstWh.whNm, MstWh.whType, MstWh.note) \
                        .filter(MstWh.siteCd == siteCd, MstWh.state == 'R') \
                        .filter(MstWh.whCd.like('%' + code + '%') | MstWh.whNm.like('%' + name + '%'))
        if json_data.get('whType') is not None:
            data = data.filter(MstWh.whType == json_data.get('whType'))
        data = data.order_by(MstWh.whCd)

        return jsonify({
                'data': [{'chk': '0','code': d[0],'name': d[1],'MstWh': d[2],'note': d[3]} for d in data]
            })

    elif flag == 'Spa':
        conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

        curs = conn.cursor()

        sql = " SELECT '0' AS chk, \
                        concat(left(a.spaDate, 4), '-', SUBSTRING(a.spaDate, 5, 2), '-', RIGHT(a.spaDate, 2)) AS spaDate, \
                        a.spaCd, a.spaSeq, a.spa AS code, \
                        a.reseller, c.varId AS resellerVarId, c.custNmEn AS resellerNm, b.theatre, c.city AS region, \
                        b.dealState, b.partnerLevel, \
                        CASE WHEN IFNULL(b.dateEffective, '') = '' THEN NULL ELSE concat(left(b.dateEffective, 4), '-', SUBSTRING(b.dateEffective, 5, 2), '-', RIGHT(b.dateEffective, 2)) END AS dateEffective, \
                        CASE WHEN IFNULL(b.dateExpiration, '') = '' THEN NULL ELSE concat(left(b.dateExpiration, 4), '-', SUBSTRING(b.dateExpiration, 5, 2), '-', RIGHT(b.dateExpiration, 2)) END AS dateExpiration, \
                        CASE WHEN IFNULL(b.dateLastPublished, '') = '' THEN NULL ELSE concat(left(b.dateLastPublished, 4), '-', SUBSTRING(b.dateLastPublished, 5, 2), '-', RIGHT(b.dateLastPublished, 2)) END AS dateLastPublished, \
                        b.revision, b.shipAndDebitId, \
                        a.endUser, b.endCustomerId, b.endUserVatId, d.custNmEn AS endUserNm, d.address1 AS endUserAddress1, d.address2 AS endUserAddress2, \
                        d.address3 AS endUserAddress3, d.city AS endUserCity, d.province AS endUserProvince, d.zipCode AS endUserZipCode, d.country AS endUserCountry, \
                        b.jnprSalesRep, b.lastUpdatedBy, a.partCd, e.partNm, b.skuDescription, b.fulfillmentType, a.qty, a.listPrice, a.dc, \
                        b.suggestedDiscountRateReseller, b.suggestedDiscountRateEndUser, b.extendedListPrice, b.extendedDiscount, b.extendedNetTotal, \
                        b.productLine, b.productFamily, b.lineNumber, b.parentLineNumber, b.configNumber, b.configInstance, b.serviceDuration, b.reportType, b.distributorId, distributorName, \
                        case when ifnull(b.quantity, 0) = 0 then 0 else ifnull(b.extendedNetTotal, 0) / b.quantity end as netPos \
                FROM pos_spa a \
                LEFT OUTER JOIN pos_spa_ext b \
                ON a.siteCd = b.siteCd \
                AND a.spaCd = b.spaCd \
                AND a.spaSeq = b.spaSeq \
                AND b.state = 'R' \
                LEFT OUTER JOIN mst_cust c \
                ON a.siteCd = c.siteCd \
                AND a.reseller = c.custCd \
                LEFT OUTER JOIN mst_cust d \
                ON a.siteCd = d.siteCd \
                AND a.endUser = d.custCd \
                LEFT OUTER JOIN mst_part e \
                ON a.siteCd= e.siteCd \
                AND a.partCd = e.partCd \
                WHERE a.siteCd = '" + siteCd + "' \
                AND a.state = 'R' \
                AND a.spa = '" + code + "' "
        if json_data.get('partCd') is not None:
            sql += " AND a.partCd = '" + json_data.get('partCd') + "' "
        if json_data.get('partText') is not None:
            sql += " AND ( a.partCd LIKE CONCAT('%', '" + json_data.get('partText') + "', '%') OR e.partNm LIKE CONCAT('%', '" + json_data.get('partText') + "', '%') ) "       
        sql += " ORDER BY a.spaCd DESC, b.spaSeq ASC"

        curs.execute(sql)
        data = list(curs.fetchall())
        conn.close()

        for index, tr in enumerate(data):
            dic = dict()
            dic['chk'] = tr[0]
            dic['spaDate'] = tr[1]
            dic['spaCd'] = tr[2]
            dic['spaSeq'] = tr[3]
            dic['code'] = tr[4]
            dic['name'] = tr[4]
            dic['reseller'] = tr[5]
            dic['resellerVarId'] = tr[6]
            dic['resellerNm'] = tr[7]
            dic['theatre'] = tr[8]
            dic['region'] = tr[9]
            dic['dealState'] = tr[10]
            dic['partnerLevel'] = tr[11]
            dic['dateEffective'] = tr[12]
            dic['dateExpiration'] = tr[13]
            dic['dateLastPublished'] = tr[14]
            dic['revision'] = tr[15]
            dic['shipAndDebitId'] = tr[16]
            dic['endUser'] = tr[17]
            dic['endCustomerId'] = tr[18]
            dic['endUserVatId'] = tr[19]
            dic['endUserNm'] = tr[20]
            dic['endUserAddress1'] = tr[21]
            dic['endUserAddress2'] = tr[22]
            dic['endUserAddress3'] = tr[23]
            dic['endUserCity'] = tr[24]
            dic['endUserProvince'] = tr[25]
            dic['endUserZipCode'] = tr[26]
            dic['endUserCountry'] = tr[27]
            dic['jnprSalesRep'] = tr[28]
            dic['lastUpdatedBy'] = tr[29]
            dic['partCd'] = tr[30]
            dic['partNm'] = tr[31]
            dic['skuDescription'] = tr[32]
            dic['fulfillmentType'] = tr[33]
            dic['qty'] = tr[34]
            dic['listPrice'] = tr[35]
            dic['dc'] = tr[36]
            dic['suggestedDiscountRateReseller'] = tr[37]
            dic['suggestedDiscountRateEndUser'] = tr[38]
            dic['extendedListPrice'] = tr[39]
            dic['extendedDiscount'] = tr[40]
            dic['extendedNetTotal'] = tr[41]
            dic['productLine'] = tr[42]
            dic['productFamily'] = tr[43]
            dic['lineNumber'] = tr[44]
            dic['parentLineNumber'] = tr[45]
            dic['configNumber'] = tr[46]
            dic['configInstance'] = tr[47]
            dic['serviceDuration'] = tr[48]       
            dic['reportType'] = tr[49]
            dic['distributorId'] = tr[50]
            dic['distributorName'] = tr[51]
            dic['netPos'] = tr[52]

            data[index] = dic
        
        return simplejson.dumps({'posSpa': data})

    elif flag == 'Sn':
        conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

        curs = conn.cursor()

        sql = " SELECT '0' as chk, a.siteCd, a.lotNo, a.sn, a.partCd, c.partNm, a.whCd, a.loc, a.curQty, a.docQty, a.unit, a.stkType, a.posState, b.bl, b.poCd, b.poNo \
                FROM stk_lot a \
                LEFT OUTER JOIN ( \
                    SELECT x.siteCd, x.lotNo, x.bl, x.inCd, x.inSeq, x.poCd, y.poNo \
                    FROM stk_in x \
                    LEFT OUTER JOIN pur_order y \
                    ON x.siteCd = y.siteCd \
                    AND x.poCd = y.poCd \
                ) b \
                ON a.siteCd = b.siteCd \
                AND a.lotNo = b.lotNo \
                LEFT OUTER JOIN mst_part c \
                ON a.siteCd = c.siteCd \
                AND a.partCd = c.partCd \
                WHERE a.siteCd = '" + siteCd + "' \
                AND a.state = 'R' \
                AND a.sn <> 'N/A' \
                AND a.sn = '" + code + "' "        

        curs.execute(sql)
        data = list(curs.fetchall())
        conn.close()

        for index, tr in enumerate(data):
            dic = dict()
            dic['chk'] = tr[0]
            dic['siteCd'] = tr[1]
            dic['lotNo'] = tr[2]
            dic['code'] = tr[3]            
            dic['name'] = tr[3]
            dic['partCd'] = tr[4]
            dic['partNm'] = tr[5]
            dic['whCd'] = tr[6]
            dic['loc'] = tr[7]
            dic['curQty'] = tr[8]
            dic['docQty'] = tr[9]
            dic['unit'] = tr[10]
            dic['stkType'] = tr[11]
            dic['posState'] = tr[12]
            dic['bl'] = tr[13]
            dic['poCd'] = tr[14]
            dic['poNo'] = tr[15]

            data[index] = dic
        
        return simplejson.dumps({'lot': data})

    elif flag == 'Project':
        conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

        curs = conn.cursor()

        sql = " SELECT '0' as chk, a.siteCd, a.prjCd, a.prjNm, a.prjType, c.minorNm as prjTypeNm, \
                       concat(left(a.prjDate, 4), '-', SUBSTRING(a.prjDate, 5, 2), '-', RIGHT(a.prjDate, 2)) AS prjDate, \
                       a.prjUser, a.docNo, a.prjAmt, a.currency, a.custCd, b.custNm, a.note \
                FROM mst_project a \
                LEFT OUTER JOIN mst_cust b \
                ON a.siteCd = b.siteCd \
                AND a.custCd = b.custCd \
                LEFT OUTER JOIN sys_minor c \
                ON c.majorCd = 'C0010' \
                AND a.prjType = c.minorCd \
                WHERE a.siteCd = '" + siteCd + "' \
                AND a.state = 'R' \
                AND (a.prjCd like '%" + code + "%' or a.prjNm like '%" + name + "%') "
        if json_data.get('custCd') is not None:
            sql += " AND a.custCd = '" + json_data.get('custCd') + "' "
        if json_data.get('custText') is not None:
            sql += " AND (a.custCd like '%" + json_data.get('custText') + "' or b.custNm like '%" + json_data.get('custText') + "%' or b.custNmEn like '%" + json_data.get('custText') + "%') "
        sql += " order by a.prjCd "

        curs.execute(sql)
        data = list(curs.fetchall())
        conn.close()

        for index, tr in enumerate(data):
            dic = dict()
            dic['chk'] = tr[0]
            dic['siteCd'] = tr[1]
            dic['code'] = tr[2]
            dic['name'] = tr[3]            
            dic['prjType'] = tr[4]
            dic['prjTypeNm'] = tr[5]
            dic['prjDate'] = tr[6]
            dic['prjUser'] = tr[7]
            dic['docNo'] = tr[8]
            dic['prjAmt'] = tr[9]
            dic['currency'] = tr[10]
            dic['custCd'] = tr[11]
            dic['custNm'] = tr[12]
            dic['note'] = tr[13]

            data[index] = dic
        
        return simplejson.dumps({'project': data})


@main.route('/api/selSysSite', methods=['POST'])
def select_sys_site():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    siteNm = json_data.get('siteNm')
    cp = SysSite.query.filter(SysSite.siteCd.like('%' + siteCd + '%'), SysSite.siteNm.like('%' + siteNm + '%'), SysSite.state=='R').all()
    return jsonify({
        'site': [c.to_json() for c in cp]
    })

@main.route('/api/regSysSite', methods=['POST'])
def regist_sys_site():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    siteNm = json_data.get('siteNm')
    contact = json_data.get('contact')
    phone = json_data.get('phone')
    fax = json_data.get('fax')
    corpNo = json_data.get('corpNo')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysSite.query.filter_by(siteCd = siteCd).first()
    if chk is not None:
        chk.siteNm = siteNm
        chk.contact = contact
        chk.phone = phone
        chk.fax = fax
        chk.corpNo = corpNo
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'site': chk.to_json()
        })
    else:
        site = SysSite(siteCd=siteCd,
                        siteNm=siteNm,
                        contact=contact,
                        phone=phone,
                        fax=fax,
                        corpNo=corpNo,
                        note=note,
                        state='R',
                        regUser=user,
                        regDate=datetime.now(),
                        modUser=None,
                        modDate=None)
    
        db.session.add(site)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'site': site.to_json()
        })

@main.route('/api/updSysSite', methods=['POST'])
def update_sys_site():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    siteNm = json_data.get('siteNm')
    contact = json_data.get('contact')
    phone = json_data.get('phone')
    fax = json_data.get('fax')
    corpNo = json_data.get('corpNo')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    site = SysSite.query.filter_by(siteCd = siteCd).first()
    if site is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    if state == 'D':
        site.state = state
    else:
        site.siteNm = siteNm
        site.contact = contact
        site.phone = phone
        site.fax = fax
        site.corpNo = corpNo
        site.note = note    
    site.modUser = user
    site.modDate = datetime.now()    

    db.session.add(site)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'site': site.to_json()
    })

@main.route('/api/selSysMenu', methods=['POST'])
def select_sys_menu():    
    json_data = json.loads(request.data, strict=False)
    systemType = json_data.get('systemType')
    pMenuCd = json_data.get('pMenuCd')

    data = SysMenu.query.filter(SysMenu.systemType==systemType, SysMenu.state=='R')
    if pMenuCd is not None:
        pMenuCd = None if pMenuCd == '' else pMenuCd
        data = data.filter(SysMenu.pMenuCd==pMenuCd)
    data = data.order_by(SysMenu.menuLv.asc(), SysMenu.dispOrder.asc())

    return jsonify({
        'menu': [d.to_json() for d in data]
    })

@main.route('/api/regSysMenu', methods=['POST'])
def regist_sys_menu():    
    json_data = json.loads(request.data, strict=False)    
    menuCd = json_data.get('menuCd')
    pMenuCd = json_data.get('pMenuCd')
    menuNm = json_data.get('menuNm')
    dispOrder = json_data.get('dispOrder')
    systemType = json_data.get('systemType')
    roleType = json_data.get('roleType')
    menuType = json_data.get('menuType')
    menuLv = json_data.get('menuLv')
    assemblyNm = json_data.get('assemblyNm')
    namespaceNm = json_data.get('namespaceNm')
    formNm = json_data.get('formNm')
    imgIdx = json_data.get('imgIdx')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysMenu.query.filter_by(menuCd = menuCd).first()
    if chk is not None:
        chk.pMenuCd = pMenuCd
        chk.menuNm = menuNm        
        chk.dispOrder = dispOrder
        chk.systemType = systemType
        chk.roleType = roleType
        chk.menuType = menuType
        chk.menuLv = menuLv
        chk.assemblyNm = assemblyNm
        chk.namespaceNm = namespaceNm
        chk.formNm = formNm
        chk.imgIdx = imgIdx
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'menu': chk.to_json()
        })
    else:
        menu = SysMenu(
                    menuCd=menuCd,
                    pMenuCd=pMenuCd,
                    menuNm=menuNm,                    
                    dispOrder=dispOrder,
                    systemType=systemType,
                    roleType=roleType,
                    menuType=menuType,
                    menuLv=menuLv,
                    assemblyNm=assemblyNm,
                    namespaceNm=namespaceNm,
                    formNm=formNm,                  
                    imgIdx=imgIdx,                  
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(menu)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'menu': menu.to_json()
        })

@main.route('/api/updSysMenu', methods=['POST'])
def update_sys_menu():    
    json_data = json.loads(request.data, strict=False)
    menuCd = json_data.get('menuCd')
    pMenuCd = json_data.get('pMenuCd')
    menuNm = json_data.get('menuNm')
    dispOrder = json_data.get('dispOrder')
    systemType = json_data.get('systemType')
    roleType = json_data.get('roleType')
    menuType = json_data.get('menuType')
    menuLv = json_data.get('menuLv')
    assemblyNm = json_data.get('assemblyNm')
    namespaceNm = json_data.get('namespaceNm')
    formNm = json_data.get('formNm')
    imgIdx = json_data.get('imgIdx')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    menu = SysMenu.query.filter_by(menuCd = menuCd).first()
    if menu is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    menu.pMenuCd = pMenuCd or menu.pMenuCd
    menu.menuNm = menuNm or menu.menuNm    
    menu.dispOrder = dispOrder or menu.dispOrder
    menu.systemType = systemType or menu.systemType
    menu.roleType = roleType or menu.roleType
    menu.menuType = menuType or menu.menuType
    menu.menuLv = menuLv or menu.menuLv
    menu.assemblyNm = assemblyNm or menu.assemblyNm
    menu.namespaceNm = namespaceNm or menu.namespaceNm
    menu.formNm = formNm or menu.formNm
    menu.imgIdx = imgIdx or menu.imgIdx    
    menu.note = note or menu.note
    menu.state = state or menu.state
    menu.modUser = user or menu.modUser
    menu.modDate = datetime.now()

    db.session.add(menu)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'menu': menu.to_json()
    })

@main.route('/api/selSysMenuObj', methods=['POST'])
def select_sys_menu_obj():    
    json_data = json.loads(request.data, strict=False)
    menuCd = json_data.get('menuCd')    

    data = SysMenuObj.query.filter(SysMenuObj.menuCd==menuCd, SysMenuObj.state=='R').order_by(SysMenuObj.objSeq.asc())

    return jsonify({
        'obj': [d.to_json() for d in data]
    })

@main.route('/api/regSysMenuObj', methods=['POST'])
def regist_sys_menu_obj():    
    json_data = json.loads(request.data, strict=False)
    menuCd = json_data.get('menuCd')
    objSeq = json_data.get('objSeq')
    objNm = json_data.get('objNm')
    objText = json_data.get('objText')
    dispOrder = json_data.get('dispOrder')
    imgIdx = json_data.get('imgIdx')
    objPos = json_data.get('objPos')    
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysMenuObj.query.filter_by(menuCd = menuCd, objSeq = objSeq).first()
    if chk is not None:
        chk.objNm = objNm
        chk.objText = objText
        chk.dispOrder = dispOrder
        chk.imgIdx = imgIdx
        chk.objPos = objPos
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'obj': chk.to_json()
        })
    else:
        menuObj = SysMenuObj(
                    menuCd=menuCd,
                    objSeq=objSeq,
                    objNm=objNm,
                    objText=objText,
                    dispOrder=dispOrder,
                    imgIdx=imgIdx,
                    objPos=objPos,                      
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(menuObj)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'obj': menuObj.to_json()
        })

@main.route('/api/updSysMenuObj', methods=['POST'])
def update_sys_menu_obj():    
    json_data = json.loads(request.data, strict=False)
    menuCd = json_data.get('menuCd')
    objSeq = json_data.get('objSeq')
    objNm = json_data.get('objNm')
    objText = json_data.get('objText')
    dispOrder = json_data.get('dispOrder')
    imgIdx = json_data.get('imgIdx')
    objPos = json_data.get('objPos')    
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    menuObj = SysMenuObj.query.filter_by(menuCd = menuCd, objSeq = objSeq).first()
    if menuObj is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    menuObj.objNm = objNm or menuObj.objNm
    menuObj.objText = objText or menuObj.objText
    menuObj.dispOrder = dispOrder or menuObj.dispOrder
    menuObj.imgIdx = imgIdx or menuObj.imgIdx
    menuObj.objPos = objPos or menuObj.objPos  
    menuObj.note = note or menuObj.note
    menuObj.state = state or menuObj.state
    menuObj.modUser = user or menuObj.modUser
    menuObj.modDate = datetime.now()

    db.session.add(menuObj)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'obj': menuObj.to_json()
    })

@main.route('/api/selSysRole', methods=['POST'])
def select_sys_role():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd') 
    roleNm = json_data.get('roleNm') 
    roleType = json_data.get('roleType')
    
    if roleType is None:
        cp = SysRole.query.filter(SysRole.siteCd.like('%' + siteCd + '%'), SysRole.roleNm.like('%' + roleNm + '%'), SysRole.state=='R').all()
    else:
        cp = SysRole.query.filter(SysRole.siteCd.like('%' + siteCd + '%'), SysRole.roleNm.like('%' + roleNm + '%'), SysRole.roleType >= roleType, SysRole.state=='R').all()

    # cp = SysRole.query.filter(SysRole.state=='R').all()
    return jsonify({
        'role': [c.to_json() for c in cp]
    })


@main.route('/api/regSysRole', methods=['POST'])
def regist_sys_role():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    roleCd = json_data.get('roleCd')
    roleNm = json_data.get('roleNm')
    roleType = json_data.get('roleType')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysRole.query.filter_by(siteCd = siteCd, roleCd = roleCd).first()
    if chk is not None:
        chk.roleNm = roleNm
        chk.roleType = roleType
        chk.note = note        
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'role': chk.to_json()
        })
    else:
        role = SysRole(siteCd=siteCd,
                        roleCd=roleCd,
                        roleNm=roleNm,
                        roleType=roleType,
                        note=note,
                        state='R',
                        regUser=user,
                        regDate=datetime.now(),
                        modUser=None,
                        modDate=None)
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'role': role.to_json()
        })

@main.route('/api/updSysRole', methods=['POST'])
def update_sys_role():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    roleCd = json_data.get('roleCd')
    roleNm = json_data.get('roleNm')
    roleType = json_data.get('roleType')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    role = SysRole.query.filter_by(siteCd = siteCd, roleCd = roleCd).first()
    
    if state == 'D':
        role.state = state
    else:
        role.roleNm = roleNm
        role.roleType = roleType
        role.note = note    
    role.modUser = user
    role.modDate = datetime.now()

    db.session.add(role)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'role': role.to_json()
    })

@main.route('/api/selSysAuth', methods=['POST'])
def select_sys_auth():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    roleCd = json_data.get('roleCd')
    systemType = json_data.get('systemType')    
    conn = pymysql.connect(host=db.engine.url.host,

                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "select case when x.menuCd is null then '0' else '1' end as chk, \
                  x.roleCd, a.menuCd, a.pMenuCd, a.menuNm, a.dispOrder, a.systemType, a.menuType, a.menuLv, a.assemblyNm, a.namespaceNm, a.formNm, \
                  a.imgIdx, x.note, x.state, x.regUser, x.regDate, x.modUser, x.modDate\
            from sys_menu a \
            left outer join ( \
                select b.menuCd, b.roleCd, b.note, b.state, b.regUser, b.regDate, b.modUser, b.modDate \
                from sys_auth b \
                inner join sys_role c \
                on b.siteCd = c.siteCd \
                and b.roleCd = c.roleCd \
                where b.siteCd = '" + siteCd + "' \
                and b.roleCd = '" + roleCd + "' \
                and b.state = 'R' \
                and c.state = 'R' \
            ) x \
            on a.menuCd = x.menuCd \
            where a.systemType = '" + systemType + "' \
            and a.state = 'R' \
            order by a.menuLv, a.dispOrder;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['roleCd'] = tr[1]
        dic['menuCd'] = tr[2]
        dic['pMenuCd'] = tr[3]
        dic['menuNm'] = tr[4]
        dic['dispOrder'] = tr[5]
        dic['systemType'] = tr[6]
        dic['menuType'] = tr[7]
        dic['menuLv'] = tr[8]
        dic['assemblyNm'] = tr[9]   
        dic['namespaceNm'] = tr[10]
        dic['formNm'] = tr[11]
        dic['imgIdx'] = tr[12]
        dic['note'] = tr[13]
        dic['state'] = tr[14]
        dic['regUser'] = tr[15]
        dic['regDate'] = tr[16]
        dic['modUser'] = tr[17]
        dic['modDate'] = tr[18]

        data[index] = dic

    return jsonify({'menu': data})

@main.route('/api/selSysAuthMenu', methods=['POST'])
def select_sys_auth_menu():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    roleCd = json_data.get('roleCd')
    roleType = json_data.get('roleType')
    systemType = json_data.get('systemType')    

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " select t.* \
            from ( \
                select case when x.menuCd is null then '0' else '1' end as chk, \
                    x.roleCd, a.menuCd, a.pMenuCd, a.menuNm, a.dispOrder, a.menuLv, a.menuType, x.note, 0 as objPos \
                from sys_menu a \
                left outer join ( \
                    select b.menuCd, b.roleCd, b.note \
                    from sys_auth b \
                    inner join sys_role c \
                    on b.siteCd = c.siteCd \
                    and b.roleCd = c.roleCd \
                    where b.siteCd = '" + siteCd + "' \
                    and b.roleCd = '" + roleCd + "' \
                    and b.state = 'R' \
                    and c.state = 'R' \
                ) x \
                on a.menuCd = x.menuCd \
                where a.systemType = '" + systemType + "' \
                and a.roleType >= '" + roleType + "' \
                and a.state = 'R' \
                \
                union all \
                \
                select case when x.menuCd is null then '0' else '1' end as chk, \
                    x.roleCd, concat(a.menuCd, '.', a.objSeq) as menuCd, a.menuCd as pMenuCd, concat(z.objNm, ' (', z.objText, ')') as menuNm, a.dispOrder, 99 as menuLv, 'C' as menuType, a.note, z.objPos \
                from sys_menu_obj a \
                left outer join ( \
                    select b.* \
                    from sys_auth_obj b \
                    inner join sys_role c \
                    on b.siteCd = c.siteCd \
                    and b.roleCd = c.roleCd \
                    where b.siteCd = '" + siteCd + "' \
                    and b.roleCd = '" + roleCd + "' \
                    and b.state = 'R' \
                    and c.state = 'R' \
                ) x \
                on a.menuCd = x.menuCd \
                and a.objSeq = x.objSeq \
                inner join sys_menu y \
                on a.menuCd = y.menuCd \
                and y.systemType = '" + systemType + "' \
                inner join sys_menu_obj z \
                on a.menuCd = z.menuCd \
                and a.objSeq = z.objSeq \
                where y.roleType >= '" + roleType + "' \
                and y.state = 'R' \
                and z.state = 'R' \
                and a.state = 'R' \
            ) t \
            order by menuLv, objPos, dispOrder;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['roleCd'] = tr[1]
        dic['menuCd'] = tr[2]
        dic['pMenuCd'] = tr[3]
        dic['menuNm'] = tr[4]
        dic['dispOrder'] = tr[5]        
        dic['menuLv'] = tr[6]
        dic['menuType'] = tr[7]
        dic['note'] = tr[8]       

        data[index] = dic

    return jsonify({'menu': data})

@main.route('/api/regSysAuthMenu', methods=['POST'])
def regist_sys_auth():    
    json_data = json.loads(request.data, strict=False)
    menuType = json_data.get('menuType')
    siteCd = json_data.get('siteCd')
    roleCd = json_data.get('roleCd')
    menuCd = json_data.get('menuCd')
    objSeq = json_data.get('objSeq')
    chkVal = json_data.get('chk')
    user = json_data.get('user')

    if menuType == 'C':
        chk = SysAuthObj.query.filter_by(siteCd = siteCd, roleCd = roleCd, menuCd = menuCd, objSeq = objSeq).first()
        if chk is not None:
            chk.state = 'R' if chkVal == '1' else 'D'
            chk.user = user
            chk.modDate = datetime.now()

            db.session.add(chk)
            db.session.commit()

            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                },
                'menu': chk.to_json()
            })
        
        else:
            if chkVal == '1':
                obj = SysAuthObj(
                    siteCd=siteCd,
                    roleCd=roleCd,
                    menuCd=menuCd,
                    objSeq=objSeq,                    
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)

                db.session.add(obj)
                db.session.commit()

                return jsonify({
                    'result': {
                        'code': 1000,
                        'msg' : gettext('1000')
                    },
                    'menu': obj.to_json()
                })
            else:
                return jsonify({
                    'result': {
                        'code': 1000,
                        'msg' : gettext('1000')
                    },
                    'menu': []
                })
    else:
        chk = SysAuth.query.filter_by(siteCd = siteCd, roleCd = roleCd, menuCd = menuCd).first()
        if chk is not None:
            chk.state = 'R' if chkVal == '1' else 'D'
            chk.user = user
            chk.modDate = datetime.now()

            db.session.add(chk)
            db.session.commit()

            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                },
                'menu': chk.to_json()
            })
        
        else:
            if chkVal == '1':
                obj = SysAuth(
                    siteCd=siteCd,
                    roleCd=roleCd,
                    menuCd=menuCd,                    
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)

                db.session.add(obj)
                db.session.commit()

                return jsonify({
                    'result': {
                        'code': 1000,
                        'msg' : gettext('1000')
                    },
                    'menu': obj.to_json()
                }) 
            else:
                return jsonify({
                    'result': {
                        'code': 1000,
                        'msg' : gettext('1000')
                    },
                    'menu': []
                })        

@main.route('/api/selSysUser', methods=['POST'])
def select_sys_user():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    userCd = json_data.get('userCd')
    userNm = json_data.get('userNm')
    roleType = json_data.get('roleType')
    if roleType is None:
        cp = SysUser.query.filter(SysUser.siteCd==siteCd, SysUser.userCd.like('%' + userCd + '%') | SysUser.userNm.like('%' + userNm + '%'), SysUser.state=='R').all()
    else:
        cp = SysUser.query.filter(SysUser.siteCd==siteCd, SysUser.userCd.like('%' + userCd + '%') | SysUser.userNm.like('%' + userNm + '%'), SysUser.state=='R')
        cp = cp.filter(SysUser.siteCd==SysRole.siteCd, SysUser.roleCd==SysRole.roleCd, SysRole.roleType>=roleType).all()
    return jsonify({
        'user': [c.to_json() for c in cp]
    })

@main.route('/api/regSysUser', methods=['POST'])
def regist_sys_user():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    userCd = json_data.get('userCd')
    userNm = json_data.get('userNm')
    pwd = json_data.get('pwd')
    roleCd = json_data.get('roleCd')
    note = json_data.get('note')
    user = json_data.get('user')
    
    password_encoding = None if pwd is None else CipherAgent().encryptAndEncodingBase64(pwd)

    chk = SysUser.query.filter_by(siteCd = siteCd, userCd = userCd).first()

    if chk is not None:
        chk.userNm = userNm
        chk.pwd = password_encoding
        chk.roleCd = roleCd
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'user': chk.to_json()
        })
    else:
        data = SysUser(
                    siteCd=siteCd,
                    userCd=userCd,
                    userNm=userNm,
                    pwd=password_encoding,
                    roleCd=roleCd,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(data)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'user': data.to_json()
        })

@main.route('/api/updSysUser', methods=['POST'])
def update_sys_user():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    userCd = json_data.get('userCd')
    userNm = json_data.get('userNm')
    pwd = json_data.get('pwd')
    roleCd = json_data.get('roleCd')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')    
    
    password_encoding = None if pwd is None else CipherAgent().encryptAndEncodingBase64(pwd)

    data = SysUser.query.filter_by(siteCd = siteCd, userCd = userCd).first()
    if user is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.userNm = userNm or data.userNm
    data.pwd = password_encoding or data.pwd
    data.roleCd = roleCd or data.roleCd
    data.note = note or data.note
    data.state = state or data.state
    data.modUser = user or data.modUser
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'user': data.to_json()
    })

@main.route('/api/selSysMajor', methods=['POST'])
def select_sys_major():
    json_data = json.loads(request.data, strict=False)    
    searchText = '' if json_data.get('searchText') is None else json_data.get('searchText')

    data = SysMajor.query.filter(SysMajor.majorCd.like('%' + searchText + '%') | SysMajor.majorNm.like('%' + searchText + '%'), SysMajor.state == 'R').all()
    return jsonify({
        'major': [c.to_json() for c in data]
    })

@main.route('/api/regSysMajor', methods=['POST'])
def regist_sys_major():    
    json_data = json.loads(request.data, strict=False)    
    majorCd = json_data.get('majorCd')    
    majorNm = json_data.get('majorNm')
    systemYn = json_data.get('systemYn')
    siteCd = json_data.get('siteCd')    
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysMajor.query.filter_by(majorCd = majorCd).first()
    if chk is not None:
        chk.majorNm = majorNm
        chk.systemYn = systemYn        
        chk.siteCd = siteCd        
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'major': chk.to_json()
        })
    else:
        data = SysMajor(
                    majorCd=majorCd,
                    majorNm=majorNm,
                    systemYn=systemYn,
                    siteCd=siteCd,                  
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(data)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'major': data.to_json()
        })

@main.route('/api/updSysMajor', methods=['POST'])
def update_sys_major():    
    json_data = json.loads(request.data, strict=False)
    majorCd = json_data.get('majorCd')    
    majorNm = json_data.get('majorNm')
    systemYn = json_data.get('systemYn')
    siteCd = json_data.get('siteCd')    
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = SysMajor.query.filter_by(majorCd = majorCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.majorNm = majorNm or data.majorNm
    data.systemYn = systemYn or data.systemYn    
    data.siteCd = siteCd or data.siteCd    
    data.note = note or data.note
    data.state = state or data.state
    data.modUser = user or data.modUser
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'data': data.to_json()
    })

@main.route('/api/selSysMinor', methods=['POST'])
def select_sys_minor():    
    json_data = json.loads(request.data, strict=False)
    majorCd = json_data.get('majorCd')    

    data = SysMinor.query.filter(SysMinor.majorCd==majorCd, SysMinor.state=='R').order_by(SysMinor.dispOrder.asc())

    return jsonify({
        'minor': [d.to_json() for d in data]
    })

@main.route('/api/regSysMinor', methods=['POST'])
def regist_sys_minor():    
    json_data = json.loads(request.data, strict=False)    
    majorCd = json_data.get('majorCd')
    minorCd = json_data.get('minorCd')
    minorNm = json_data.get('minorNm')
    ref1 = json_data.get('ref1')
    ref2 = json_data.get('ref2')
    ref3 = json_data.get('ref3')
    dispOrder = json_data.get('dispOrder')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = SysMinor.query.filter_by(majorCd = majorCd, minorCd = minorCd).first()
    if chk is not None:
        chk.minorNm = minorNm
        chk.ref1 = ref1
        chk.ref2 = ref2
        chk.ref3 = ref3
        chk.dispOrder = dispOrder        
        chk.note = note
        chk.state = 'R'
        chk.modUser = user
        chk.modDate = datetime.now()

        db.session.add(chk)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'minor': chk.to_json()
        })
    else:
        data = SysMinor(
                    majorCd=majorCd,
                    minorCd=minorCd,
                    minorNm=minorNm,
                    ref1=ref1,
                    ref2=ref2,
                    ref3=ref3,
                    dispOrder=dispOrder,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(data)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'minor': data.to_json()
        })

@main.route('/api/updSysMinor', methods=['POST'])
def update_sys_minor():    
    json_data = json.loads(request.data, strict=False)
    majorCd = json_data.get('majorCd')
    minorCd = json_data.get('minorCd')
    minorNm = json_data.get('minorNm')
    ref1 = json_data.get('ref1')
    ref2 = json_data.get('ref2')
    ref3 = json_data.get('ref3')
    dispOrder = json_data.get('dispOrder')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = SysMinor.query.filter_by(majorCd = majorCd, minorCd = minorCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.minorNm = minorNm or data.minorNm
    data.ref1 = ref1 or data.ref1    
    data.ref2 = ref2 or data.ref2
    data.ref3 = ref3 or data.ref3
    data.dispOrder = dispOrder or data.dispOrder    
    data.note = note or data.note
    data.state = state or data.state
    data.modUser = user or data.modUser
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'minor': data.to_json()
    })

@main.route('/api/login', methods=['POST'])
def login():
    lang = get_locale()
    json_data = request.get_json()
    siteCd = json_data.get('siteCd')
    userCd = json_data.get('userCd')
    pwd = json_data.get('pwd')

    cp = SysUser.query.filter_by(siteCd=siteCd,userCd=userCd,state='R').first()    

    if cp is None:
        return jsonify({
            'result': {
                'code': 8501,
                'msg' : gettext('8501')
            }
        })

    password_encoding = CipherAgent().encryptAndEncodingBase64(pwd)    

    if cp.pwd == password_encoding:        

        authMenu = db.session.query(SysMenu.menuCd, SysMenu.pMenuCd, SysMenu.menuNm, SysMenu.menuType, SysMenu.systemType, SysMenu.dispOrder, SysMenu.menuLv \
                                    , SysMenu.assemblyNm, SysMenu.namespaceNm, SysMenu.formNm, SysMenu.imgIdx, SysMenu.note) \
            .filter(SysSite.siteCd==SysRole.siteCd, SysSite.state=='R') \
            .filter(SysAuth.siteCd==SysRole.siteCd, SysAuth.roleCd==SysRole.roleCd, SysAuth.state=='R') \
            .filter(SysAuth.menuCd==SysMenu.menuCd, SysMenu.state=='R', SysMenu.roleType>=SysRole.roleType) \
            .filter(SysAuth.siteCd==siteCd, SysAuth.roleCd==cp.roleCd, SysAuth.state=='R') \
            .order_by(SysMenu.menuLv.asc(), SysMenu.dispOrder.asc())        

        authMenuObj = db.session.query(SysMenu.formNm, SysMenuObj.menuCd, SysMenuObj.objSeq, SysMenuObj.objNm, SysMenuObj.objText, SysMenuObj.dispOrder \
                                    , SysMenuObj.imgIdx, SysMenuObj.objPos, SysMenuObj.note) \
            .filter(SysSite.siteCd==SysAuthObj.siteCd, SysSite.state=='R') \
            .filter(SysAuthObj.menuCd==SysMenuObj.menuCd, SysAuthObj.objSeq==SysMenuObj.objSeq) \
            .filter(SysMenu.menuCd==SysMenuObj.menuCd, SysMenu.state=='R') \
            .filter(SysAuthObj.siteCd==SysRole.siteCd, SysAuthObj.roleCd==SysRole.roleCd, SysRole.state=='R', SysMenu.roleType>=SysRole.roleType) \
            .filter(SysAuthObj.siteCd==siteCd, SysAuthObj.roleCd==cp.roleCd, SysAuthObj.state=='R', SysMenuObj.state=='R') \
            .order_by(SysMenuObj.menuCd.asc(), SysMenuObj.dispOrder.asc(), SysMenuObj.objSeq.asc())

        chkConnInfo = SysConn.query.filter(SysConn.siteCd == siteCd, SysConn.userCd == userCd, SysConn.connState != 'LOC', SysConn.state == 'R').order_by(SysConn.connCd.desc()).first()

        chkOption = db.session.query(SysMinor.ref1) \
            .filter(SysMajor.majorCd==SysMinor.majorCd, SysMajor.state=='R') \
            .filter(SysMinor.majorCd=='S0000', SysMinor.minorCd=='001', SysMinor.state=='R').first()
        
        chkOptionVal = 'N'

        if chkOption is not None:
            chkOptionVal = chkOption[0]
        
        if chkConnInfo is not None and chkOptionVal == 'Y':
            return jsonify({
                'result': {
                    'code': 8607,
                    'msg' : '이미 다른곳에서 접속중인 클라이언트가 존재합니다.\n * ' + chkConnInfo.hostName + ' (' +chkConnInfo.ipAddr + ')\n\n 기존 연결을 종료하고 접속 하시겠습니까?'
                },
                'conn': chkConnInfo.to_json()
                ,
                'user': cp.to_json_simple()            
                ,
                'authMenu': [{'menuCd': c[0],'pMenuCd': c[1],'menuNm': c[2],'menuType': c[3],'systemType': c[4],'dispOrder': c[5],'menuLv': c[6],'assemblyNm': c[7],'namespaceNm': c[8],'formNm': c[9],'imgIdx': c[10],'note': c[11]} for c in authMenu]
                ,
                'authMenuObj': [{'formNm': c[0],'menuCd': c[1],'objSeq': c[2],'objNm': c[3],'objText': c[4],'dispOrder': c[5],'imgIdx': c[6],'objPos': c[7],'note': c[8]} for c in authMenuObj]
                })
        else:
            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                },
                'user': cp.to_json_simple()            
                ,
                'authMenu': [{'menuCd': c[0],'pMenuCd': c[1],'menuNm': c[2],'menuType': c[3],'systemType': c[4],'dispOrder': c[5],'menuLv': c[6],'assemblyNm': c[7],'namespaceNm': c[8],'formNm': c[9],'imgIdx': c[10],'note': c[11]} for c in authMenu]
                ,
                'authMenuObj': [{'formNm': c[0],'menuCd': c[1],'objSeq': c[2],'objNm': c[3],'objText': c[4],'dispOrder': c[5],'imgIdx': c[6],'objPos': c[7],'note': c[8]} for c in authMenuObj]
            })
    else:
        return jsonify({
            'result': {
                'code': 8502,
                'msg' : gettext('8502')
            }
        })

@main.route('/api/getUserInfo', methods=['POST'])
def get_user_info():
    lang = get_locale()
    json_data = request.get_json()
    siteCd = json_data.get('siteCd')
    userCd = json_data.get('userCd')    

    cp = SysUser.query.filter_by(siteCd=siteCd,userCd=userCd,state='R').first()    

    if cp is None:
        return jsonify({
            'result': {
                'code': 8501,
                'msg' : gettext('8501')
            }
        })

    authMenu = db.session.query(SysMenu.menuCd, SysMenu.pMenuCd, SysMenu.menuNm, SysMenu.menuType, SysMenu.systemType, SysMenu.dispOrder, SysMenu.menuLv \
                                , SysMenu.assemblyNm, SysMenu.namespaceNm, SysMenu.formNm, SysMenu.imgIdx, SysMenu.note) \
        .filter(SysSite.siteCd==SysRole.siteCd, SysSite.state=='R') \
        .filter(SysAuth.siteCd==SysRole.siteCd, SysAuth.roleCd==SysRole.roleCd, SysAuth.state=='R') \
        .filter(SysAuth.menuCd==SysMenu.menuCd, SysMenu.state=='R') \
        .filter(SysAuth.siteCd==siteCd, SysAuth.roleCd==cp.roleCd, SysAuth.state=='R') \
        .order_by(SysMenu.menuLv.asc(), SysMenu.dispOrder.asc())        

    authMenuObj = db.session.query(SysMenu.formNm, SysMenuObj.menuCd, SysMenuObj.objSeq, SysMenuObj.objNm, SysMenuObj.objText, SysMenuObj.dispOrder \
                                , SysMenuObj.imgIdx, SysMenuObj.objPos, SysMenuObj.note) \
        .filter(SysSite.siteCd==SysAuthObj.siteCd, SysSite.state=='R') \
        .filter(SysAuthObj.menuCd==SysMenuObj.menuCd, SysAuthObj.objSeq==SysMenuObj.objSeq) \
        .filter(SysMenu.menuCd==SysMenuObj.menuCd) \
        .filter(SysAuthObj.siteCd==siteCd, SysAuthObj.roleCd==cp.roleCd, SysAuthObj.state=='R', SysMenuObj.state=='R') \
        .order_by(SysMenuObj.menuCd.asc(), SysMenuObj.dispOrder.asc(), SysMenuObj.objSeq.asc())        

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'user': cp.to_json_simple()
        ,
        'authMenu': [{'menuCd': c[0],'pMenuCd': c[1],'menuNm': c[2],'menuType': c[3],'systemType': c[4],'dispOrder': c[5],'menuLv': c[6],'assemblyNm': c[7],'namespaceNm': c[8],'formNm': c[9],'imgIdx': c[10],'note': c[11]} for c in authMenu]
        ,
        'authMenuObj': [{'formNm': c[0],'menuCd': c[1],'objSeq': c[2],'objNm': c[3],'objText': c[4],'dispOrder': c[5],'imgIdx': c[6],'objPos': c[7],'note': c[8]} for c in authMenuObj]
    })

@main.route('/api/selSysConn', methods=['POST'])
def select_sys_conn():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')    
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    connState = json_data.get('connState')    
    userText = json_data.get('userText')
    hostName = json_data.get('hostName')
    ipAddr = json_data.get('ipAddr')
    macAddr = json_data.get('macAddr')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " select a.connCd, a.userCd, b.userNm, \
                   a.connState, fn_get_codename('S0010', a.connState) AS connStateNm, \
                   a.hostName, a.ipAddr, a.macAddr, a.loginTime, a.logoutTime \
            from sys_conn a \
            left outer join sys_user b \
            on a.siteCd = b.siteCd \
            and a.userCd = b.userCd \
            where a.siteCd = '" + siteCd + "' \
            and a.state = 'R' \
            and a.loginTime between '" + fDate + "' and '" + tDate + "'"    
    if userText is not None:
        sql += " AND ( a.userCd LIKE CONCAT('%', '" + userText + "', '%') OR b.userNm LIKE CONCAT('%', '" + userText + "', '%') ) "
    if connState is not None:
        sql += " AND a.connState = '" + connState + "' "
    if hostName is not None:
        sql += " AND a.hostName LIKE CONCAT('%', '" + hostName + "', '%') "
    if ipAddr is not None:
        sql += " AND a.ipAddr LIKE CONCAT('%', '" + ipAddr + "', '%') "
    if macAddr is not None:
        sql += " AND a.macAddr LIKE CONCAT('%', '" + macAddr + "', '%') "    
    sql += " order by a.connCd desc; "

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['connCd'] = tr[0]
        dic['userCd'] = tr[1]
        dic['userNm'] = tr[2]
        dic['connState'] = tr[3]
        dic['connStateNm'] = tr[4]
        dic['hostName'] = tr[5]
        dic['ipAddr'] = tr[6]
        dic['macAddr'] = tr[7]
        dic['loginTime'] = None if tr[8] is None else tr[8] if tr[8] == '0000-00-00 00:00:00' else tr[8].strftime('%Y-%m-%d %H:%M:%S')
        dic['logoutTime'] = None if tr[9] is None else tr[9] if tr[9] == '0000-00-00 00:00:00' else tr[9].strftime('%Y-%m-%d %H:%M:%S')
        data[index] = dic

    return jsonify({'conn': data})

@main.route('/api/insSysConn', methods=['POST'])
def insert_sys_conn():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')    
    hostName = json_data.get('hostName')
    ipAddr = json_data.get('ipAddr')
    macAddr = json_data.get('macAddr')
    user = json_data.get('user')
    preConnCd = json_data.get('preConnCd')

    if preConnCd != None and preConnCd != '':
        pre_connInfo = SysConn.query.filter_by(siteCd = siteCd, connCd = preConnCd).first()
        
        if pre_connInfo is not None:
            pre_connInfo.connState = 'LOC'
            pre_connInfo.checkTime = datetime.now()
            pre_connInfo.logoutTime = datetime.now()
            pre_connInfo.modDate = datetime.now()
            pre_connInfo.modUser = user

            db.session.add(pre_connInfo)  

    findKey_connCd = siteCd + datetime.now().strftime('%y%m%d')
    seq_connCd = 1
    sel_connCd = SysConn.query.filter(SysConn.siteCd == siteCd, SysConn.connCd.like(findKey_connCd + '%')).order_by(SysConn.connCd.desc()).first()
    if sel_connCd is not None:
        seq_connCd = int(sel_connCd.connCd[-6:]) + 1
    connCd = findKey_connCd + (6 - len(str(seq_connCd))) * '0' + str(seq_connCd)

    connInfo = SysConn(
        siteCd=siteCd,
        connCd=connCd,
        userCd=user,
        connState='LIC',
        hostName=hostName,
        ipAddr=ipAddr,
        macAddr=macAddr,
        loginTime=datetime.now(),
        logoutTime=None,
        checkTime=datetime.now(),
        note=None,
        state='R',
        regUser=user,
        regDate=datetime.now(),
        modUser=None,
        modDate=None)

    db.session.add(connInfo)        
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'conn': connInfo.to_json()
    })

@main.route('/api/updSysConn', methods=['POST'])
def update_sys_conn():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    connCd = json_data.get('connCd')
    connState = json_data.get('connState')
    user = json_data.get('user')

    data = SysConn.query.filter_by(siteCd = siteCd, connCd = connCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.connState = connState
    if connState == 'LOC':
        data.logoutTime = datetime.now()
    else:
        data.logoutTime = None
    data.checkTime = datetime.now()    
    data.modUser = user
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'conn': data.to_json()
    })

@main.route('/api/testListDataSave', methods=['POST'])
def test_list_data_save():
    lang = get_locale()
    json_data = request.get_json()

    input_data = json_data.get('data')

    try:
        for i, d in enumerate(input_data):

            chk = TstSite.query.filter_by(siteCd = d.get('siteCd')).first()

            if d.get('crud') == 'C':
                
                if chk is not None:
                    if chk.state == 'R':
                        db.session.rollback()
                        return jsonify({
                            'result': {
                                'code': 8503,
                                # 'msg' : 'It is already registered data.'
                                'msg' : '회원사코드 ({0}) 는 이미 등록 되어 있습니다.'.format(chk.siteCd)
                            }            
                        })

                    chk.siteNm = d.get('siteNm')
                    chk.note = d.get('note')
                    chk.modUser = d.get('user')
                    chk.modDate = datetime.now()
                    db.session.add(chk)
                else:
                    site = TstSite(siteCd = d.get('siteCd'),
                            siteNm = d.get('siteNm'),
                            note = d.get('note'),
                            state = 'R',
                            regUser = d.get('user'),
                            regDate = datetime.now(),
                            modUser = None,
                            modDate = None)
                    db.session.add(site)
            
            elif d.get('crud') == 'U':
                if chk is not None:
                    chk.siteNm = d.get('siteNm')
                    chk.note = d.get('note')
                    chk.modUser = d.get('user')
                    chk.modDate = datetime.now()
                    db.session.add(chk)

            elif d.get('crud') == 'D':
                if chk is not None:
                    chk.state = 'D'
                    chk.modUser = d.get('user')
                    chk.modDate = datetime.now()
                    db.session.add(chk)
        
    except exc.SQLAlchemyError as e:        
        db.session.rollback()
        return jsonify({
            'result': {
                'code': 9998,                
                'msg' : 'SQLAlchemy Error. ({0})'.format(e)
            }            
        })
    except BaseException as e:
        return jsonify({
            'result': {
                'code': 9999,                
                'msg' : '{0}'.format(e)
            }            
        })

    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })


@main.route('/api/insTmpRawData', methods=['POST'])
def insert_tmp_raw_data():    
    json_data = json.loads(request.data, strict=False)        

    data = TmpRawDatum(
        A=json_data.get('A'),
        B=json_data.get('B'),
        C=json_data.get('C'),
        D=json_data.get('D'),
        E=json_data.get('E'),
        F=json_data.get('F'),
        G=json_data.get('G'),
        H=json_data.get('H'),
        I=json_data.get('I'),
        J=json_data.get('J'),
        K=json_data.get('K'),
        L=json_data.get('L'),
        M=json_data.get('M'),
        N=json_data.get('N'),
        O=json_data.get('O'),
        P=json_data.get('P'),
        Q=json_data.get('Q'),
        R=json_data.get('R'),
        S=json_data.get('S'),
        T=json_data.get('T'),
        U=json_data.get('U'),
        V=json_data.get('V'),
        W=json_data.get('W'),
        X=json_data.get('X'),
        Y=json_data.get('Y'),
        Z=json_data.get('Z'),
        AA=json_data.get('AA'),
        AB=json_data.get('AB'),
        AC=json_data.get('AC'),
        AD=json_data.get('AD'),
        AE=json_data.get('AE'),
        AF=json_data.get('AF'),
        AG=json_data.get('AG'),
        AH=json_data.get('AH'),
        AI=json_data.get('AI'),
        AJ=json_data.get('AJ'),
        AK=json_data.get('AK'),
        AL=json_data.get('AL'),
        AM=json_data.get('AM'),
        AN=json_data.get('AN'),
        AO=json_data.get('AO'),
        AP=json_data.get('AP'),
        AQ=json_data.get('AQ'),
        AR=json_data.get('AR'),
        AS=json_data.get('AS'),
        AT=json_data.get('AT'),
        AU=json_data.get('AU'),
        AV=json_data.get('AV'),
        AW=json_data.get('AW'),
        AX=json_data.get('AX'),
        AY=json_data.get('AY'),
        AZ=json_data.get('AZ'),
        BA=json_data.get('BA'),
        BB=json_data.get('BB'),
        BC=json_data.get('BC'),
        BD=json_data.get('BD'),
        BE=json_data.get('BE'),
        BF=json_data.get('BF'),
        BG=json_data.get('BG'),
        BH=json_data.get('BH'),
        BI=json_data.get('BI'),
        BJ=json_data.get('BJ'),
        BK=json_data.get('BK'),
        BL=json_data.get('BL'),
        BM=json_data.get('BM'),
        BN=json_data.get('BN'),
        BO=json_data.get('BO'),
        BP=json_data.get('BP'),
        BQ=json_data.get('BQ'),
        BR=json_data.get('BR'),
        BS=json_data.get('BS'),
        BT=json_data.get('BT'),
        BU=json_data.get('BU'),
        BV=json_data.get('BV'),
        BW=json_data.get('BW'),
        BX=json_data.get('BX'),
        BY=json_data.get('BY'),
        BZ=json_data.get('BZ'),
        CA=json_data.get('CA'),
        CB=json_data.get('CB'),
        CC=json_data.get('CC'),
        CD=json_data.get('CD'),
        CE=json_data.get('CE'),
        CF=json_data.get('CF'),
        CG=json_data.get('CG'),
        CH=json_data.get('CH'),
        CI=json_data.get('CI'),
        CJ=json_data.get('CJ'),
        CK=json_data.get('CK'),
        CL=json_data.get('CL'),
        CM=json_data.get('CM'),
        CN=json_data.get('CN'),
        CO=json_data.get('CO'),
        CP=json_data.get('CP'),
        CQ=json_data.get('CQ'),
        CR=json_data.get('CR'),
        CS=json_data.get('CS'),
        CT=json_data.get('CT'),
        CU=json_data.get('CU'),
        CV=json_data.get('CV'),
        CW=json_data.get('CW'),
        CX=json_data.get('CX'),
        CY=json_data.get('CY'),
        CZ=json_data.get('CZ'),
        DA=json_data.get('DA'),
        DB=json_data.get('DB'),
        DC=json_data.get('DC'),
        DD=json_data.get('DD'),
        DE=json_data.get('DE'),
        DF=json_data.get('DF'),
        DG=json_data.get('DG'),
        DH=json_data.get('DH')
    )

    db.session.add(data)        
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }        
    })

@main.route('/api/selTmpRawData', methods=['POST'])
def select_tmp_raw_data():    
    json_data = json.loads(request.data, strict=False)
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    
    data = TmpRawDatum.query.filter(TmpRawDatum.Q >= fDate, TmpRawDatum.Q <= tDate).order_by(TmpRawDatum.IDX.asc()).all()

    return jsonify({
        'data': [d.to_json() for d in data]
    })

@main.route('/api/insTmpRawDataA', methods=['POST'])
def insert_tmp_raw_data_a():    
    json_data = json.loads(request.data, strict=False)        

    data = TmpRawDatumA(
        A=json_data.get('A'),
        B=json_data.get('B'),
        C=json_data.get('C'),
        D=json_data.get('D'),
        E=json_data.get('E'),
        F=json_data.get('F'),
        G=json_data.get('G'),
        H=json_data.get('H'),
        I=json_data.get('I'),
        J=json_data.get('J'),
        K=json_data.get('K'),
        L=json_data.get('L'),
        M=json_data.get('M'),
        N=json_data.get('N'),
        O=json_data.get('O'),
        P=json_data.get('P'),
        Q=json_data.get('Q'),
        R=json_data.get('R'),       
    )

    db.session.add(data)        
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }        
    })