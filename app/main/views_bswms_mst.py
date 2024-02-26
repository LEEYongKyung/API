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
from sqlalchemy import func, literal
from sqlalchemy.orm import aliased
from flask_babel import gettext
import pymysql
from app.main.awsutil import awsS3

from . import main

@main.route('/api/selMstCust', methods=['POST'])
def select_mst_cust():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    custType = json_data.get('custType')
    custLocType = json_data.get('custLocType')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    cp = MstCust.query.filter(MstCust.siteCd==siteCd, MstCust.custType.like('%' + custType + '%'), MstCust.custCd.like('%' + custCd + '%') | MstCust.custNm.like('%' + custNm + '%') | MstCust.custNmEn.like('%' + custNm + '%'), MstCust.state=='R').all()
    if custLocType is not None:
        cp = cp.query.filter(MstCust.custLocType==custLocType)

    return jsonify({
        'cust': [c.to_json() for c in cp]
    })

@main.route('/api/regMstCust', methods=['POST'])
def regist_mst_cust():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
    custLocType = json_data.get('custLocType')
    varId = json_data.get('varId')
    sellYn = json_data.get('sellYn')
    purcYn = json_data.get('purcYn')
    address1 = json_data.get('address1')
    address2 = json_data.get('address2')
    address3 = json_data.get('address3')
    city = json_data.get('city')
    province = json_data.get('province')
    country = json_data.get('country')
    zipCode = json_data.get('zipCode')
    contact = json_data.get('contact')
    phone = json_data.get('phone')
    fax = json_data.get('fax')
    corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    note4 = json_data.get('note4')
    note5 = json_data.get('note5')
    user = json_data.get('user')    

    chk = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()

    if chk is not None:
        chk.custNm = custNm
        chk.custNmEn = custNmEn
        chk.custAbb = custAbb
        chk.custType = custType
        chk.custLocType = custLocType
        chk.varId = varId
        chk.sellYn = sellYn
        chk.purcYn = purcYn
        chk.address1 = address1
        chk.address2 = address2
        chk.address3 = address3
        chk.city = city
        chk.province = province
        chk.country = country
        chk.zipCode = zipCode
        chk.contact = contact
        chk.phone = phone
        chk.fax = fax
        chk.corpNo = corpNo
        chk.note = note
        chk.note2 = note2
        chk.note3 = note3
        chk.note4 = note4
        chk.note5 = note5
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
            'cust': chk.to_json()
        })
    else:

        findKey = custLocType
        seq = 1
        sel = MstCust.query.filter(MstCust.siteCd == siteCd, MstCust.custCd.like(findKey + '%')).order_by(MstCust.custCd.desc()).first()
        if sel is not None:
            seq = int(sel.custCd[-5:]) + 1    
        custCd = findKey + (5 - len(str(seq))) * '0' + str(seq)

        data = MstCust(
                    siteCd=siteCd,
                    custCd=custCd,
                    custNm=custNm,
                    custNmEn=custNmEn,
                    custAbb=custAbb,
                    custType=custType,
                    custLocType=custLocType,
                    varId=varId,
                    sellYn=sellYn,
                    purcYn=purcYn,
                    address1=address1,
                    address2=address2,
                    address3=address3,
                    city=city,
                    province=province,
                    country=country,
                    zipCode=zipCode,
                    contact=contact,
                    phone=phone,
                    fax=fax,
                    corpNo=corpNo,
                    note=note,
                    note2=note2,
                    note3=note3,
                    note4=note4,
                    note5=note5,
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
            'cust': data.to_json()
        })

@main.route('/api/updMstCust', methods=['POST'])
def update_mst_cust():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
    custLocType = json_data.get('custLocType')
    varId = json_data.get('varId')
    sellYn = json_data.get('sellYn')
    purcYn = json_data.get('purcYn')
    address1 = json_data.get('address1')
    address2 = json_data.get('address2')
    address3 = json_data.get('address3')
    city = json_data.get('city')
    province = json_data.get('province')
    country = json_data.get('country')
    zipCode = json_data.get('zipCode')
    contact = json_data.get('contact')
    phone = json_data.get('phone')
    fax = json_data.get('fax')
    corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    note4 = json_data.get('note4')
    note5 = json_data.get('note5')
    state = json_data.get('state')
    user = json_data.get('user')    

    data = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.custNm = custNm or data.custNm
    data.custNmEn = custNmEn or data.custNmEn
    data.custAbb = custAbb or data.custAbb
    data.custType = custType or data.custType
    data.custLocType = custLocType or data.custLocType
    data.varId = varId or data.varId
    data.sellYn = sellYn or data.sellYn
    data.purcYn = purcYn or data.purcYn
    data.address1 = address1 or data.address1
    data.address2 = address2 or data.address2
    data.address3 = address3 or data.address3
    data.city = city or data.city
    data.province = province or data.province
    data.country = country or data.country
    data.zipCode = zipCode or data.zipCode
    data.contact = contact or data.contact
    data.phone = phone or data.phone
    data.fax = fax or data.fax
    data.corpNo = corpNo or data.corpNo    
    data.note = note or data.note
    data.note2 = note2 or data.note2
    data.note3 = note3 or data.note3
    data.note4 = note4 or data.note4
    data.note5 = note5 or data.note5
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
        'cust': data.to_json()
    })

@main.route('/api/selMstPart', methods=['POST'])
def select_mst_part():
    json_data = json.loads(request.data, strict=False)
    print("json_data=",json_data )
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')    
    partNm = json_data.get('partNm')
    partKind = json_data.get('partKind')
    partType1 = json_data.get('partType1')
    partType2 = json_data.get('partType2')
    partType3 = json_data.get('partType3')

    cp = MstPart.query.filter(MstPart.siteCd.like('%' + siteCd + '%'), 
                            MstPart.partCd.like('%' + partCd + '%'),
                            MstPart.partNm.like('%' + partNm + '%'),
                            MstPart.partKind.like('%' + partKind + '%'),
                            MstPart.partType1.like('%' + partType1 + '%'), 
                            MstPart.partType2.like('%' + partType2 + '%'), 
                            MstPart.partType3.like('%' + partType3 + '%'),
                            MstPart.state=='R').all()

    return jsonify({
        'part': [c.to_json() for c in cp]
    })

@main.route('/api/regMstPart', methods=['POST'])
def regist_mst_part():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')
    partNm = json_data.get('partNm')
    partKind = json_data.get('partKind')
    partType1 = json_data.get('partType1')
    partType2 = json_data.get('partType2')
    partType3 = json_data.get('partType3')
    partUnit = json_data.get('partUnit')
    partSpec = json_data.get('partSpec')
    currency = json_data.get('currency')
    manufacturer = json_data.get('manufacturer')
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    note4 = json_data.get('note4')
    note5 = json_data.get('note5')
    user = json_data.get('user')

    chk = MstPart.query.filter_by(siteCd = siteCd, partCd = partCd).first()

    if chk is not None:
        chk.partNm = partNm
        chk.partKind = partKind
        chk.partType1 = partType1
        chk.partType2 = partType2
        chk.partType3 = partType3
        chk.partUnit = partUnit
        chk.partSpec = partSpec
        chk.currency = currency
        chk.manufacturer = manufacturer
        chk.note = note
        chk.note2 = note2
        chk.note3 = note3
        chk.note4 = note4
        chk.note5 = note5
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
            'part': chk.to_json()
        })
    else:
        findKey = partType1
        seq = 1
        sel = MstPart.query.filter(MstPart.siteCd == siteCd, MstPart.partCd.like(findKey + '%')).order_by(MstPart.partCd.desc()).first()
        if sel is not None:
            seq = int(sel.partCd[-5:]) + 1    
        partCd = findKey + (5 - len(str(seq))) * '0' + str(seq)

        part = MstPart(siteCd=siteCd,
                        partCd=partCd,
                        partNm=partNm,
                        partKind=partKind,
                        partType1=partType1,
                        partType2=partType2,
                        partType3=partType3,
                        partUnit=partUnit,
                        partSpec=partSpec,
                        currency=currency,
                        manufacturer=manufacturer,
                        note=note,
                        note2=note2,
                        note3=note3,
                        note4=note4,
                        note5=note5,
                        state='R',
                        regUser=user,
                        regDate=datetime.now(),
                        modUser=None,
                        modDate=None)
        
        db.session.add(part)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'part': part.to_json()
        })

@main.route('/api/updMstPart', methods=['POST'])
def update_mst_part():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')
    partNm = json_data.get('partNm')
    partKind = json_data.get('partKind')
    partType1 = json_data.get('partType1')
    partType2 = json_data.get('partType2')
    partType3 = json_data.get('partType3')
    partUnit = json_data.get('partUnit')
    partSpec = json_data.get('partSpec')
    currency = json_data.get('currency')
    manufacturer = json_data.get('manufacturer')
    state = json_data.get('state')
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    note4 = json_data.get('note4')
    note5 = json_data.get('note5')
    user = json_data.get('user')
    
    part = MstPart.query.filter_by(siteCd = siteCd, partCd = partCd).first()
    if part is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    if state == 'D':
        part.state = state
    else:
        part.partNm = partNm
        part.partKind = partKind
        part.partType1 = partType1
        part.partType2 = partType2
        part.partType3 = partType3
        part.partUnit = partUnit
        part.partSpec = partSpec
        part.currency = currency
        part.manufacturer = manufacturer
        part.note = note
        part.note2 = note2
        part.note3 = note3
        part.note4 = note4
        part.note5 = note5
    part.modUser = user
    part.modDate = datetime.now()

    db.session.add(part)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'part': part.to_json()
    })

@main.route('/api/selMstWh', methods=['POST'])
def select_mst_wh():
    json_data = json.loads(request.data, strict=False)
    print("json_data=",json_data )
    siteCd = json_data.get('siteCd')
    whCd = json_data.get('whCd')    
    whNm = json_data.get('whNm')
    whType = json_data.get('whType')

    cp = MstWh.query.filter(MstWh.siteCd.like('%' + siteCd + '%'), 
                            MstWh.whCd.like('%' + whCd + '%') | MstWh.whNm.like('%' + whNm + '%'),
                            MstWh.whType.like('%' + whType + '%'),
                            MstWh.state=='R').all()    

    return jsonify({
        'wh': [c.to_json() for c in cp]
    })

@main.route('/api/regMstWh', methods=['POST'])
def regist_mst_wh():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    whCd = json_data.get('whCd')    
    whNm = json_data.get('whNm')
    whType = json_data.get('whType')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = MstWh.query.filter_by(siteCd = siteCd, whCd = whCd).first()

    if chk is not None:
        chk.whNm = whNm
        chk.whType = whType
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
            'wh': chk.to_json()
        })

    else:
        wh = MstWh(siteCd=siteCd,
                    whCd=whCd,
                    whNm=whNm,
                    whType=whType,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(wh)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'wh': wh.to_json()
        })

@main.route('/api/updMstWh', methods=['POST'])
def update_mst_wh():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    whCd = json_data.get('whCd')    
    whNm = json_data.get('whNm')
    whType = json_data.get('whType')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    wh = MstWh.query.filter_by(siteCd = siteCd, whCd = whCd).first()
    
    if wh is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    if state == 'D':
        wh.state = state
    else:
        wh.whNm = whNm
        wh.whType = whType
        wh.note = note        
    wh.modUser = user
    wh.modDate = datetime.now()

    db.session.add(wh)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'wh': wh.to_json()
    })

@main.route('/api/selMstStdStock', methods=['POST'])
def select_mst_std_stock():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')    
    tDate= json_data.get('tDate')
    partCd= json_data.get('partCd')
    partText = json_data.get('partText')
    stkType = json_data.get('stkType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT '0' AS chk, a.siteCd,  \
                   a.sstkCd, \
                   CONCAT(LEFT(a.inDate, 4), '-', SUBSTRING(a.inDate, 5, 2), '-', RIGHT(a.inDate, 2)) AS inDate, \
                   a.partCd, \
                   b.partNm, \
                   IFNULL(a.stkQty, 0) AS stkQty, \
                   IFNULL(a.stkAmt, 0) AS stkAmt, \
                   a.stkType, \
                   a.note, \
                   a.regDate, \
                   a.regUser, \
                   a.modDate, \
                   a.modUser \
            FROM mst_std_stock a \
            LEFT OUTER JOIN mst_part b \
            ON a.siteCd = b.siteCd \
            AND a.partCd = b.partCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.inDate BETWEEN '" + fDate + "' AND '" + tDate + "' \
            AND a.state = 'R'"

    if partCd is not None:
        sql += " AND a.partCd = '" + partCd + "'"
    if partText is not None:
        sql += " AND ( a.partCd LIKE CONCAT('%', '" + partText + "', '%') OR b.partNm LIKE CONCAT('%', '" + partText + "', '%') )"    
    if stkType is not None:
        sql += " AND a.stkType = '" + stkType + "'"
    sql += " ORDER BY a.partCd, a.inDate;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['sstkCd'] = tr[2]
        dic['inDate'] = tr[3]
        dic['partCd'] = tr[4]
        dic['partNm'] = tr[5]
        dic['stkQty'] = tr[6]
        dic['stkAmt'] = tr[7]
        dic['stkType'] = tr[8]
        dic['note'] = tr[9]
        dic['regDate'] = None if tr[10] is None else tr[10] if tr[10] == '0000-00-00 00:00:00' else tr[10].strftime('%Y-%m-%d %H:%M:%S')
        dic['regUser'] = tr[11]
        dic['modDate'] = None if tr[12] is None else tr[12] if tr[12] == '0000-00-00 00:00:00' else tr[12].strftime('%Y-%m-%d %H:%M:%S')
        dic['modUser'] = tr[13]

        data[index] = dic

    # return jsonify({'order': data})    
    return simplejson.dumps({'stdStock': data})

@main.route('/api/regMstStdStock', methods=['POST'])
def regist_mst_std_stock():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sstkCd = json_data.get('sstkCd')    
    inDate = json_data.get('inDate')
    partCd = json_data.get('partCd')
    stkQty = json_data.get('stkQty')
    stkAmt = json_data.get('stkAmt')
    stkType = json_data.get('stkType')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = MstStdStock.query.filter_by(siteCd = siteCd, sstkCd = sstkCd).first()

    if chk is not None:
        chk.inDate = inDate
        chk.partCd = partCd
        chk.stkQty = stkQty
        chk.stkAmt = stkAmt
        chk.stkType = stkType        
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
            'wh': chk.to_json()
        })

    else:
        findKey = 'STD' + datetime.now().strftime('%y%m%d')
        seq = 1
        sel = MstStdStock.query.filter(MstStdStock.siteCd == siteCd, MstStdStock.sstkCd.like(findKey + '%')).order_by(MstStdStock.sstkCd.desc()).first()
        if sel is not None:
            seq = int(sel.sstkCd[-5:]) + 1    
        sstkCd = findKey + (5 - len(str(seq))) * '0' + str(seq)

        stdStock = MstStdStock(siteCd=siteCd,
                    sstkCd=sstkCd,
                    inDate=inDate,
                    partCd=partCd,
                    stkQty=stkQty,
                    stkAmt=stkAmt,
                    stkType=stkType,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(stdStock)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'stdStock': stdStock.to_json()
        })

@main.route('/api/updMstStdStock', methods=['POST'])
def update_mst_std_stock():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sstkCd = json_data.get('sstkCd')    
    inDate = json_data.get('inDate')
    partCd = json_data.get('partCd')
    stkQty = json_data.get('stkQty')
    stkAmt = json_data.get('stkAmt')
    stkType = json_data.get('stkType')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    stdStock = MstStdStock.query.filter_by(siteCd = siteCd, sstkCd = sstkCd).first()
    
    if stdStock is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    if state == 'D':
        stdStock.state = state
    else:
        stdStock.inDate = inDate
        stdStock.partCd = partCd
        stdStock.stkQty = stkQty
        stdStock.stkAmt = stkAmt
        stdStock.stkType = stkType        
        stdStock.note = note        
    stdStock.modUser = user
    stdStock.modDate = datetime.now()

    db.session.add(stdStock)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'wstdStockh': stdStock.to_json()
    })

# @main.route('/api/selMstProject', methods=['POST'])
# def select_mst_project():
#     json_data = json.loads(request.data, strict=False)
#     print("json_data=",json_data )
#     siteCd = json_data.get('siteCd')
#     prjCd = json_data.get('prjCd')
#     prjNm = json_data.get('prjNm')
#     custCd = json_data.get('custCd')

#     cp = MstProject.query.filter(MstProject.siteCd.like('%' + siteCd + '%'), 
#                             MstProject.prjCd.like('%' + prjCd + '%') | MstProject.prjNm.like('%' + prjNm + '%'),
#                             MstProject.custCd.like('%' + custCd + '%'),
#                             MstProject.state=='R').all()   

#     return jsonify({
#         'project': [c.to_json() for c in cp]
#     })

@main.route('/api/selMstProject', methods=['POST'])
def select_mst_project():
    json_data = json.loads(request.data, strict=False)
    print("json_data=",json_data )
    siteCd = json_data.get('siteCd')
    prjCd = json_data.get('prjCd')
    prjNm = json_data.get('prjNm')
    custCd = json_data.get('custCd')
    custText = json_data.get('custText')
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT a.siteCd, a.prjCd, a.prjNm, a.prjType, \
            CONCAT(LEFT(a.prjDate, 4), '-', SUBSTRING(a.prjDate, 5, 2), '-', RIGHT(a.prjDate, 2)) as prjDate, \
            a.prjUser, a.docNo, a.prjAmt, a.currency, \
            a.custCd, b.custNm as custNm, \
            a.note, a.regUser, a.regDate, a.modUser, a.modDate \
            FROM mst_project a \
            LEFT OUTER JOIN mst_cust b \
            ON a.siteCd = b.siteCd \
            AND a.custCd = b.custCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.state = 'R' "            
    if prjCd is not None and prjCd != '':
        sql += " AND a.prjCd LIKE CONCAT('%', '" + prjCd + "', '%')"
    if prjNm is not None and prjNm != '':
        sql += " AND a.prjNm LIKE CONCAT('%', '" + prjCd + "', '%')"
    if custCd is not None and custCd != '':
        sql += " AND a.custCd = '" + custCd + "'"
    if custText is not None and custText != '':
        sql += " AND (a.custCd like '%" + custText + "%' or b.custNm like '%" + custText + "%')" 
    sql += " order by a.prjCd"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()        
        dic['siteCd'] = tr[0]
        dic['prjCd'] = tr[1]
        dic['prjNm'] = tr[2]
        dic['prjType'] = tr[3]
        dic['prjDate'] = tr[4]
        dic['prjUser'] = tr[5]
        dic['docNo'] = tr[6]
        dic['prjAmt'] = tr[7]
        dic['currency'] = tr[8]
        dic['custCd'] = tr[9]
        dic['custNm'] = tr[10]
        dic['note'] = tr[11]   
        dic['regUser'] = tr[12]
        dic['regDate'] = None if tr[13] is None else tr[13] if tr[13] == '0000-00-00 00:00:00' else tr[13].strftime('%Y-%m-%d %H:%M:%S')
        dic['modUser'] = tr[14]
        dic['modDate'] = None if tr[15] is None else tr[15] if tr[15] == '0000-00-00 00:00:00' else tr[15].strftime('%Y-%m-%d %H:%M:%S')    

        data[index] = dic
    
    return simplejson.dumps({'project': data})

@main.route('/api/regMstProject', methods=['POST'])
def regist_mst_project():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    prjCd = json_data.get('prjCd')    
    prjNm = json_data.get('prjNm')
    prjType = json_data.get('prjType')
    prjDate = json_data.get('prjDate')
    prjUser = json_data.get('prjUser')
    docNo = json_data.get('docNo')
    prjAmt = json_data.get('prjAmt')
    currency = json_data.get('currency')
    custCd = json_data.get('custCd')
    note = json_data.get('note')
    user = json_data.get('user')

    chk = MstProject.query.filter_by(siteCd = siteCd, prjCd = prjCd).first()

    if chk is not None:
        chk.prjNm = prjNm
        chk.prjType = prjType
        chk.prjDate = prjDate
        chk.prjUser = prjUser
        chk.docNo = docNo
        chk.prjAmt = prjAmt
        chk.currency = currency
        chk.custCd = custCd
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
            'project': chk.to_json()
        })

    else:
        project = MstProject(siteCd=siteCd,
                    prjCd=prjCd,
                    prjNm=prjNm,
                    prjType=prjType,
                    prjDate=prjDate,
                    prjUser=prjUser,
                    docNo=docNo,
                    prjAmt=prjAmt,
                    currency=currency,
                    custCd=custCd,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'project': project.to_json()
        })

@main.route('/api/updMstProject', methods=['POST'])
def update_mst_project():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    prjCd = json_data.get('prjCd')    
    prjNm = json_data.get('prjNm')
    prjType = json_data.get('prjType')
    prjDate = json_data.get('prjDate')
    prjUser = json_data.get('prjUser')
    docNo = json_data.get('docNo')
    prjAmt = json_data.get('prjAmt')
    currency = json_data.get('currency')
    custCd = json_data.get('custCd')
    note = json_data.get('note')
    user = json_data.get('user')
    state = json_data.get('state')

    project = MstProject.query.filter_by(siteCd = siteCd, prjCd = prjCd).first()
    
    if project is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    if state == 'D':
        project.state = state
    else:
        project.prjNm = prjNm
        project.prjType = prjType      
        project.prjDate = prjDate
        project.prjUser = prjUser
        project.docNo = docNo
        project.prjAmt = prjAmt
        project.currency = currency
        project.custCd = custCd        
        project.note = note        
    project.modUser = user
    project.modDate = datetime.now()

    db.session.add(project)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'project': project.to_json()
    })