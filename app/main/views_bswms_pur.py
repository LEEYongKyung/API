# -- coding: utf-8 --

import os
import simplejson

from flask import jsonify, request, flash, url_for, app, current_app, json
from werkzeug.utils import secure_filename, redirect

import config
import datetime
from app import db, get_locale
from app.models_bswms import *
# from app.main.cipherutil import CipherAgent
from dateutil import parser
from sqlalchemy import func, literal
from sqlalchemy.orm import aliased
from flask_babel import gettext
import pymysql
from app.main.handlerutil import jsonhandler
# from app.main.awsutil import awsS3

from . import main


@main.route('/api/selPurOrder', methods=['POST'])
def select_pur_order():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    poNo = json_data.get('poNo')
    poState = json_data.get('poState')
    stkType = json_data.get('stkType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT '0' as chk, \
                    a.siteCd, \
                    a.poCd, \
                    a.poNo, \
                    /*CONCAT(LEFT(a.poDate, 4), '-', SUBSTRING(a.poDate, 5, 2), '-', RIGHT(a.poDate, 2)) AS poDate,*/ \
                    STR_TO_DATE(a.poDate, '%Y%m%d') AS poDate, \
                    a.poState, fn_get_codename('P0002', a.poState) AS poStateNm, \
                    a.poType1, fn_get_codename('P0003', a.poType1) AS poType1Nm, \
                    a.poType2, fn_get_codename('P0004', a.poType2) AS poType2Nm, \
                    a.poType3, fn_get_codename('P0005', a.poType3) AS poType3Nm, \
                    b.partType3 AS partCategory, fn_get_codename('C0006', b.partType3) AS partCategoryNm, \
                    a.partCd, b.partNm, \
                    a.custCd, c.custNm, \
                    a.soNo, \
                    a.poQty, \
                    IFNULL(a.unitAmt, 0) * IFNULL(a.poQty, 0) AS totAmt, \
                    IFNULL(a.listAmt, 0) AS listAmt, \
                    IFNULL(a.unitAmt, 0) AS unitAmt, \
                    IFNULL(a.purcAmt, 0) AS purcAmt, \
                    IFNULL(a.taxAmt, 0) AS taxAmt, \
                    IFNULL(a.purcAmt, 0) + IFNULL(a.taxAmt, 0) AS subPurcAmt, \
                    (IFNULL(a.purcAmt, 0) + IFNULL(a.taxAmt, 0)) * IFNULL(a.poQty, 0) AS totPurcAmt, \
                    a.currency, fn_get_codename('S0006', a.currency) AS currencyNm, \
                    a.posState, fn_get_codename('P0001', a.posState) AS posStateNm, \
                    a.note, \
                    IFNULL((select sum(inQty) from stk_in x where x.siteCd = a.siteCd and x.poCd = a.poCd and x.state = 'R'), 0.00) as inQtySum, \
                    a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm \
            FROM pur_order a \
            LEFT OUTER JOIN mst_part b \
            ON a.siteCd = b.siteCd \
            AND a.partCd = b.partCd \
            LEFT OUTER JOIN mst_cust c \
            ON a.siteCd = c.siteCd \
            AND a.custCd = c.custCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.poDate BETWEEN '" + fDate + "' AND '" + tDate + "' \
            AND a.state = 'R'"

    if poNo is not None:
        sql += " AND a.poNo LIKE CONCAT('%', '" + poNo + "', '%')"
    if partCd is not None:
        sql += " AND a.partCd = '" + partCd + "'"
    if partText is not None:
        sql += " AND ( a.partCd LIKE CONCAT('%', '" + partText + \
            "', '%') OR b.partNm LIKE CONCAT('%', '" + partText + "', '%') )"
    if poState is not None:
        sql += " AND a.poState = '" + poState + "'"
    if stkType is not None:
        sql += " AND a.stkType = '" + stkType + "'"
    sql += " ORDER BY a.poCd desc;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poDate'] = tr[4]
        dic['poState'] = tr[5]
        dic['poStateNm'] = tr[6]
        dic['poType1'] = tr[7]
        dic['poType1Nm'] = tr[8]
        dic['poType2'] = tr[9]
        dic['poType2Nm'] = tr[10]
        dic['poType3'] = tr[11]
        dic['poType3Nm'] = tr[12]
        dic['partCategory'] = tr[13]
        dic['partCategoryNm'] = tr[14]
        dic['partCd'] = tr[15]
        dic['partNm'] = tr[16]
        dic['custCd'] = tr[17]
        dic['custNm'] = tr[18]
        dic['soNo'] = tr[19]
        dic['poQty'] = tr[20]
        dic['totAmt'] = tr[21]
        dic['listAmt'] = tr[22]
        dic['unitAmt'] = tr[23]
        dic['purcAmt'] = tr[24]
        dic['taxAmt'] = tr[25]
        dic['subPurcAmt'] = tr[26]
        dic['totPurcAmt'] = tr[27]
        dic['currency'] = tr[28]
        dic['currencyNm'] = tr[29]
        dic['posState'] = tr[30]
        dic['posStateNm'] = tr[31]
        dic['note'] = tr[32]
        dic['inQtySum'] = tr[33]
        dic['stkType'] = tr[34]
        dic['stkTypeNm'] = tr[35]

        data[index] = dic

    # return jsonify({'order': data})
    return simplejson.dumps({'order': data}, default=jsonhandler.date_handler)


@main.route('/api/insPurOrder', methods=['POST'])
def insert_pur_order():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    poNo = json_data.get('poNo')
    poDate = json_data.get('poDate')
    poType1 = json_data.get('poType1')
    poType2 = json_data.get('poType2')
    poType3 = json_data.get('poType3')
    partCd = json_data.get('partCd')
    custCd = json_data.get('custCd')
    soNo = json_data.get('soNo')
    poQty = json_data.get('poQty')
    unitAmt = json_data.get('unitAmt')
    listAmt = json_data.get('listAmt')
    taxAmt = json_data.get('taxAmt')
    purcAmt = json_data.get('purcAmt')
    currency = json_data.get('currency')
    posState = json_data.get('posState')
    stkType = json_data.get('stkType')
    note = json_data.get('note')
    user = json_data.get('user')

    findKey = 'ORD' + poDate[-6:]  # datetime.now().strftime('%y%m%d')
    seq = 1
    sel = PurOrder.query.filter(PurOrder.siteCd == siteCd, PurOrder.poCd.like(
        findKey + '%')).order_by(PurOrder.poCd.desc()).first()
    if sel is not None:
        seq = int(sel.poCd[-6:]) + 1
    poCd = findKey + (6 - len(str(seq))) * '0' + str(seq)

    order = PurOrder(siteCd=siteCd,
                     poCd=poCd,
                     poNo=poNo,
                     poState='N',
                     poDate=poDate,
                     poType1=poType1,
                     poType2=poType2,
                     poType3=poType3,
                     custCd=custCd,
                     partCd=partCd,
                     soNo=soNo,
                     poQty=poQty,
                     unitAmt=unitAmt,
                     listAmt=listAmt,
                     taxAmt=taxAmt,
                     purcAmt=purcAmt,
                     currency=currency,
                     posState=posState,
                     stkType=stkType,
                     note=note,
                     state='R',
                     regUser=user,
                     regDate=datetime.now(),
                     modUser=None,
                     modDate=None)

    db.session.add(order)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        }
    })


@main.route('/api/updPurOrder', methods=['POST'])
def update_pur_order():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    poCd = json_data.get('poCd')
    poNo = json_data.get('poNo')
    poDate = json_data.get('poDate')
    poType1 = json_data.get('poType1')
    poType2 = json_data.get('poType2')
    poType3 = json_data.get('poType3')
    partCd = json_data.get('partCd')
    custCd = json_data.get('custCd')
    soNo = json_data.get('soNo')
    poQty = json_data.get('poQty')
    unitAmt = json_data.get('unitAmt')
    listAmt = json_data.get('listAmt')
    taxAmt = json_data.get('taxAmt')
    purcAmt = json_data.get('purcAmt')
    currency = json_data.get('currency')
    posState = json_data.get('posState')
    stkType = json_data.get('stkType')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    data = PurOrder.query.filter_by(siteCd=siteCd, poCd=poCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        data.poNo = poNo or data.poNo
        data.poDate = poDate or data.poDate
        data.poType1 = poType1 or data.poType1
        data.poType2 = poType2 or data.poType2
        data.poType3 = poType3 or data.poType3
        data.partCd = partCd or data.partCd
        data.custCd = custCd or data.custCd
        data.soNo = soNo or data.soNo
        data.poQty = poQty or data.poQty
        data.unitAmt = unitAmt or data.unitAmt
        data.listAmt = listAmt or data.listAmt
        data.taxAmt = taxAmt or data.taxAmt
        data.purcAmt = purcAmt or data.purcAmt
        data.currency = currency or data.currency
        data.posState = posState or data.posState
        data.stkType = stkType or data.stkType
        data.note = note or data.note
    data.modUser = user or data.modUser
    data.modDate = datetime.now()
    data.state = state or data.state

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        }
    })


@main.route('/api/selPurOrderIn', methods=['POST'])
def select_pur_order_in():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    poCdMulti = json_data.get('poCdMulti')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT (CASE WHEN inCd IS NULL THEN '1' ELSE '0' END) chk, \
                   t.* \
            FROM ( \
                SELECT r1.* \
                    , (CASE @vPartition WHEN r1.poCd THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) rnum \
                    , CAST((CASE @vPartition WHEN r1.poCd THEN @sumqty:=@sumqty+inQty ELSE @sumqty:=IFNULL(inQty, 1) END) AS DECIMAL(14,2)) sqty \
                    , (CASE WHEN r1.inCd IS NULL THEN 1 ELSE (SELECT COUNT(*) FROM stk_in x WHERE x.siteCd = r1.sitecd AND x.poCd = r1.poCd AND x.state = 'R') END) as cnt \
                    , (@vPartition:=r1.poCd) vPartition \
                FROM ( \
                    SELECT a.siteCd, a.poCd, a.poNo, \
                            a.poType1, fn_get_codename('P0003', a.poType1) AS poType1Nm, \
                            a.poType2, fn_get_codename('P0004', a.poType2) AS poType2Nm, \
                            a.poType3, fn_get_codename('P0005', a.poType3) AS poType3Nm, \
                            a.partCd, c.partNm, a.poQty, \
                            a.poState, fn_get_codename('P0002', a.poState) AS poStateNm, \
                            a.poDate, b.inCd, b.inSeq, b.inNo, b.inDate, b.lotNo, b.sn, \
                            IFNULL(b.inKind, 'G') AS inKind, fn_get_codename('W0001', IFNULL(b.inKind, 'G')) AS inKindNm, \
                            b.purcYn, \
                            /*IFNULL(b.inType, 'A'), fn_get_codename('W0002', IFNULL(b.inType, 'A')) AS inTypeNm,*/ \
                            b.inType, fn_get_codename('W0002', b.inType) AS inTypeNm, \
                            IFNULL(b.inQty, 1) AS inQty, \
                            c.partUnit AS inUnit, fn_get_codename('S0005', c.partUnit) AS inUnitNm, \
                            b.inAmt, \
                            a.currency, fn_get_codename('S0006', a.currency) AS currencyNm, \
                            b.cmLoc, \
                            IFNULL(b.whCd, 'WH0001') AS whCd, d.whNm, \
                            b.loc, fn_get_codename('C0008', b.loc) AS locNm, \
                            b.bl, b.invoice, \
                            /*IFNULL(b.inWarr, 'A'), fn_get_codename('W0003', IFNULL(b.inWarr, 'A')) AS inWarrNm,*/ \
                            b.inWarr, fn_get_codename('W0003', b.inWarr) AS inWarrNm, \
                            /*IFNULL(b.partRank, 'A') AS partRank, fn_get_codename('W0004', IFNULL(b.partRank, 'A')) AS partRankNm,*/ \
                            b.partRank AS partRank, fn_get_codename('W0004', b.partRank) AS partRankNm, \
                            a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm, \
                            b.note, \
                            IFNULL(a.unitAmt, 0) AS unitAmt, \
                            IFNULL(a.purcAmt, 0) AS purcAmt, \
                            IFNULL(a.taxAmt, 0) AS taxAmt \
                    FROM pur_order a \
                    LEFT OUTER JOIN stk_in b \
                    ON a.siteCd = b.siteCd \
                    AND a.poCd = b.poCd \
                    AND b.state = 'R' \
                    LEFT OUTER JOIN mst_part c \
                    ON a.siteCd = c.siteCd \
                    AND a.partCd = c.partCd \
                    LEFT OUTER JOIN mst_wh d \
                    ON b.siteCd = d.siteCd \
                    AND b.whCd = d.whCd \
                    WHERE a.siteCd = '" + siteCd + "' \
                    AND a.poCd IN ('', " + poCdMulti + ") \
                    AND a.state = 'R' \
                ) r1 \
                ,(SELECT @vPartition:='', @rownum:=0, @sumqty:=0 FROM DUAL) r2 \
                ORDER BY r1.poCd \
            ) t \
            ORDER BY poCd, inCd, inSeq;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poType1'] = tr[4]
        dic['poType1Nm'] = tr[5]
        dic['poType2'] = tr[6]
        dic['poType2Nm'] = tr[7]
        dic['poType3'] = tr[8]
        dic['poType3Nm'] = tr[9]
        dic['partCd'] = tr[10]
        dic['partNm'] = tr[11]
        dic['poQty'] = tr[12]
        dic['poState'] = tr[13]
        dic['poStateNm'] = tr[14]
        dic['poDate'] = tr[15]
        dic['inCd'] = tr[16]
        dic['inSeq'] = tr[17]
        dic['inNo'] = tr[18]
        dic['inDate'] = tr[19]
        dic['lotNo'] = tr[20]
        dic['sn'] = tr[21]
        dic['inKind'] = tr[22]
        dic['inKindNm'] = tr[23]
        dic['purcYn'] = tr[24]
        dic['inType'] = tr[25]
        dic['inTypeNm'] = tr[26]
        dic['inQty'] = tr[27]
        dic['inUnit'] = tr[28]
        dic['inUnitNm'] = tr[29]
        dic['inAmt'] = tr[30]
        dic['currency'] = tr[31]
        dic['currencyNm'] = tr[32]
        dic['cmLoc'] = tr[33]
        dic['whCd'] = tr[34]
        dic['whNm'] = tr[35]
        dic['loc'] = tr[36]
        dic['locNm'] = tr[37]
        dic['bl'] = tr[38]
        dic['invoice'] = tr[39]
        dic['inWarr'] = tr[40]
        dic['inWarrNm'] = tr[41]
        dic['partRank'] = tr[42]
        dic['partRankNm'] = tr[43]
        dic['stkType'] = tr[44]
        dic['stkTypeNm'] = tr[45]
        dic['note'] = tr[46]
        dic['unitAmt'] = tr[47]
        dic['purcAmt'] = tr[48]
        dic['taxAmt'] = tr[49]
        dic['rnum'] = tr[50]
        dic['sqty'] = tr[51]
        dic['cnt'] = tr[52]

        data[index] = dic

    # return jsonify({'order': data})
    return simplejson.dumps({'order': data})


@main.route('/api/insPurOrderIn', methods=['POST'])
def insert_pur_order_in():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    inCd = json_data.get('inCd')
    inDate = json_data.get('inDate')
    inNo = json_data.get('inNo')
    sn = json_data.get('sn')
    inKind = json_data.get('inKind')
    purcYn = json_data.get('purcYn')
    inType = json_data.get('inType')
    poCd = json_data.get('poCd')
    partCd = json_data.get('partCd')
    inQty = json_data.get('inQty')
    inUnit = json_data.get('inUnit')
    inAmt = json_data.get('inAmt')
    currency = json_data.get('currency')
    cmLoc = json_data.get('cmLoc')
    whCd = json_data.get('whCd')
    loc = json_data.get('loc')
    bl = json_data.get('bl')
    invoice = json_data.get('invoice')
    inWarr = json_data.get('inWarr')
    partRank = json_data.get('partRank')
    stkType = json_data.get('stkType')
    note = json_data.get('note')
    user = json_data.get('user')

    order = PurOrder.query.filter_by(
        siteCd=siteCd, poCd=poCd, state='R').first()
    if order is None:
        return jsonify({
            'result': {
                'code': 8601,
                'msg': '발주정보가 존재하지 않습니다.'
            }
        })

    if (order.poState == 'C'):
        return jsonify({
            'result': {
                'code': 8602,
                'msg': '해당발주는 이미 입고완료 상태 입니다.'
            }
        })

    # check stk_lot
    findKey = 'LOT' + inDate[-6:]
    seq = 1
    sel = StkLot.query.filter(StkLot.siteCd == siteCd, StkLot.lotNo.like(
        findKey + '%')).order_by(StkLot.lotNo.desc()).first()
    if sel is not None:
        seq = int(sel.lotNo[-6:]) + 1
    lotNo = findKey + (6 - len(str(seq))) * '0' + str(seq)

    # check stk_in
    if not inCd:
        findKey_inCd = 'IN' + inDate[-6:]
        seq_inCd = 1
        sel_inCd = StkIn.query.filter(StkIn.siteCd == siteCd, StkIn.inCd.like(
            findKey_inCd + '%')).order_by(StkIn.inCd.desc()).first()
        if sel_inCd is not None:
            seq_inCd = int(sel_inCd.inCd[-6:]) + 1
        inCd = findKey_inCd + (6 - len(str(seq_inCd))) * '0' + str(seq_inCd)

    inSeq = 1
    sel_inSeq = StkIn.query.filter(
        StkIn.siteCd == siteCd, StkIn.inCd == inCd).order_by(StkIn.inSeq.desc()).first()
    if sel_inSeq is not None:
        inSeq = int(sel_inSeq.inSeq) + 1

    # check pur_order
    order_chk = db.session.query(func.sum(StkIn.inQty)).filter(
        StkIn.siteCd == siteCd, StkIn.poCd == poCd, StkIn.state == 'R').group_by(StkIn.poCd).first()
    chk_poQty = order.poQty
    chk_sum = 0
    if order_chk is not None:
        chk_sum = order_chk[0]

     # pur_order update
    if int(chk_poQty) <= int(chk_sum) + int(inQty):
        order.poState = 'C'
    else:
        order.poState = 'P'

    # stk_lot insert
    lot = StkLot(siteCd=siteCd,
                 lotNo=lotNo,
                 sn=sn,
                 partCd=partCd,
                 whCd=whCd,
                 loc=loc,
                 curQty=inQty,
                 docQty=inQty,
                 unit=inUnit,
                 stkType=stkType,
                 posState=order.posState,
                 state='R',
                 regUser=user,
                 regDate=datetime.now(),
                 modUser=None,
                 modDate=None)

    # 내자 일경우 입고단가 = 공급가액 + 부가세 (X)
    # 내자 일경우 입고단가 = 공급가액 (2021-02-24)
    if order.poType1 == 'A':
        # inAmt = order.purcAmt + order.taxAmt
        inAmt = order.purcAmt
    else:
        inAmt = 0.00

    # stk_in insert
    stkIn = StkIn(siteCd=siteCd,
                  inCd=inCd,
                  inSeq=inSeq,
                  inNo=inNo,
                  inDate=inDate,
                  lotNo=lotNo,
                  sn=sn,
                  inKind=inKind,
                  purcYn=purcYn,
                  inType=inType,
                  poCd=poCd,
                  partCd=partCd,
                  inQty=inQty,
                  inUnit=inUnit,
                  inAmt=inAmt,
                  currency=currency,
                  cmLoc=cmLoc,
                  whCd=whCd,
                  loc=loc,
                  bl=bl,
                  invoice=invoice,
                  inWarr=inWarr,
                  partRank=partRank,
                  stkType=stkType,
                  note=note,
                  state='R',
                  regUser=user,
                  regDate=datetime.now(),
                  modUser=None,
                  modDate=None)

    db.session.add(order)
    db.session.add(lot)
    db.session.add(stkIn)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkIn': stkIn.to_json()
    })


@main.route('/api/selPurIncoming', methods=['POST'])
def select_pur_incoming():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    poNo = json_data.get('poNo')
    bl = json_data.get('bl')
    sn = json_data.get('sn')
    loc = json_data.get('loc')
    stkType = json_data.get('stkType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT * \
           FROM ( \
                SELECT '0' as chk, a.siteCd, a.poCd, b.poNo, \
                        b.poType1, fn_get_codename('P0003', b.poType1) AS poType1Nm, \
                        b.poType2, fn_get_codename('P0004', b.poType2) AS poType2Nm, \
                        b.poType3, fn_get_codename('P0005', b.poType3) AS poType3Nm, \
                        a.partCd, d.partNm, b.poQty, \
                        b.poState, fn_get_codename('P0002', b.poState) AS poStateNm, \
                        /*CASE WHEN b.poDate is null THEN '' ELSE CONCAT(LEFT(b.poDate, 4), '-', SUBSTRING(b.poDate, 5, 2), '-', RIGHT(b.poDate, 2)) END AS poDate,*/ \
                        STR_TO_DATE(b.poDate, '%Y%m%d') AS poDate, \
                        a.inCd, a.inSeq, a.inNo, \
                        /*CONCAT(LEFT(a.inDate, 4), '-', SUBSTRING(a.inDate, 5, 2), '-', RIGHT(a.inDate, 2)) AS inDate,*/ \
                        STR_TO_DATE(a.inDate, '%Y%m%d') AS inDate, \
                        a.lotNo, a.sn, \
                        a.inKind, fn_get_codename('W0001', a.inKind) AS inKindNm, \
                        a.purcYn, \
                        a.inType, fn_get_codename('W0002', a.inType) AS inTypeNm, \
                        a.inQty, \
                        d.partUnit AS inUnit, fn_get_codename('S0005', d.partUnit) AS inUnitNm, \
                        IFNULL(a.inAmt, 0.00) inAmt, \
                        a.currency, fn_get_codename('S0006', a.currency) AS currencyNm, \
                        a.cmLoc, \
                        a.whCd, e.whNm, \
                        a.loc, fn_get_codename('C0008', a.loc) AS locNm, \
                        a.bl, a.invoice, \
                        a.inWarr, fn_get_codename('W0003', a.inWarr) AS inWarrNm, \
                        a.partRank AS partRank, fn_get_codename('W0004', a.partRank) AS partRankNm, \
                        a.note, \
                        IFNULL(b.unitAmt, 0.00) unitAmt, \
                        a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm \
                    FROM stk_in a \
                    LEFT OUTER JOIN pur_order b \
                    ON a.siteCd = b.siteCd \
                    AND a.poCd = b.poCd \
                    AND b.state = 'R' \
                    INNER JOIN stk_lot c \
                    ON a.siteCd = c.siteCd \
                    AND a.lotNo = c.lotNo \
                    LEFT OUTER JOIN mst_part d \
                    ON a.siteCd = d.siteCd \
                    AND a.partCd = d.partCd \
                    LEFT OUTER JOIN mst_wh e \
                    ON a.siteCd = e.siteCd \
                    AND a.whCd = e.whCd \
                    WHERE a.siteCd = '" + siteCd + "' \
                    AND a.inDate BETWEEN '" + fDate + "' AND '" + tDate + "' \
                    AND a.state = 'R' "

    if poNo is not None:
        sql += " AND b.poNo LIKE CONCAT('%', '" + poNo + "', '%')"
    if partCd is not None:
        sql += " AND a.partCd = '" + partCd + "'"
    if partText is not None:
        sql += " AND ( a.partCd LIKE CONCAT('%', '" + partText + \
            "', '%') OR d.partNm LIKE CONCAT('%', '" + partText + "', '%') )"
    if bl is not None:
        sql += " AND a.bl like '%" + bl + "%' "
    if sn is not None:
        sql += " AND a.sn like '%" + sn + "%' "
    if stkType is not None:
        sql += " AND a.stkType = '" + stkType + "'"
    sql += " ) t"
    if loc is not None:
        sql += " WHERE ( loc like '%" + loc + \
            "%' or locNm like '%" + loc + "%' ) "
    sql += " order by inCd desc, inSeq desc"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poType1'] = tr[4]
        dic['poType1Nm'] = tr[5]
        dic['poType2'] = tr[6]
        dic['poType2Nm'] = tr[7]
        dic['poType3'] = tr[8]
        dic['poType3Nm'] = tr[9]
        dic['partCd'] = tr[10]
        dic['partNm'] = tr[11]
        dic['poQty'] = tr[12]
        dic['poState'] = tr[13]
        dic['poStateNm'] = tr[14]
        dic['poDate'] = tr[15]
        dic['inCd'] = tr[16]
        dic['inSeq'] = tr[17]
        dic['inNo'] = tr[18]
        dic['inDate'] = tr[19]
        dic['lotNo'] = tr[20]
        dic['sn'] = tr[21]
        dic['inKind'] = tr[22]
        dic['inKindNm'] = tr[23]
        dic['purcYn'] = tr[24]
        dic['inType'] = tr[25]
        dic['inTypeNm'] = tr[26]
        dic['inQty'] = tr[27]
        dic['inUnit'] = tr[28]
        dic['inUnitNm'] = tr[29]
        dic['inAmt'] = tr[30]
        dic['currency'] = tr[31]
        dic['currencyNm'] = tr[32]
        dic['cmLoc'] = tr[33]
        dic['whCd'] = tr[34]
        dic['whNm'] = tr[35]
        dic['loc'] = tr[36]
        dic['locNm'] = tr[37]
        dic['bl'] = tr[38]
        dic['invoice'] = tr[39]
        dic['inWarr'] = tr[40]
        dic['inWarrNm'] = tr[41]
        dic['partRank'] = tr[42]
        dic['partRankNm'] = tr[43]
        dic['note'] = tr[44]
        dic['unitAmt'] = tr[45]
        dic['stkType'] = tr[46]
        dic['stkTypeNm'] = tr[47]

        data[index] = dic

    # return jsonify({'order': data})
    return simplejson.dumps({'incoming': data}, default=jsonhandler.date_handler)


@main.route('/api/insPurIncomingEtc', methods=['POST'])
def insert_pur_incoming_etc():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    inCd = json_data.get('inCd')
    inDate = json_data.get('inDate')
    inNo = json_data.get('inNo')
    sn = json_data.get('sn')
    inKind = json_data.get('inKind')
    purcYn = json_data.get('purcYn')
    inType = json_data.get('inType')
    partCd = json_data.get('partCd')
    inQty = json_data.get('inQty')
    inUnit = json_data.get('inUnit')
    inAmt = json_data.get('inAmt')
    currency = json_data.get('currency')
    cmLoc = json_data.get('cmLoc')
    whCd = json_data.get('whCd')
    loc = json_data.get('loc')
    bl = json_data.get('bl')
    invoice = json_data.get('invoice')
    inWarr = json_data.get('inWarr')
    partRank = json_data.get('partRank')
    stkType = json_data.get('stkType')
    note = json_data.get('note')
    user = json_data.get('user')

    # check stk_lot
    findKey = 'LOT' + inDate[-6:]
    seq = 1
    sel = StkLot.query.filter(StkLot.siteCd == siteCd, StkLot.lotNo.like(
        findKey + '%')).order_by(StkLot.lotNo.desc()).first()
    if sel is not None:
        seq = int(sel.lotNo[-6:]) + 1
    lotNo = findKey + (6 - len(str(seq))) * '0' + str(seq)

    # check stk_in
    if not inCd:
        findKey_inCd = 'IN' + inDate[-6:]
        seq_inCd = 1
        sel_inCd = StkIn.query.filter(StkIn.siteCd == siteCd, StkIn.inCd.like(
            findKey_inCd + '%')).order_by(StkIn.inCd.desc()).first()
        if sel_inCd is not None:
            seq_inCd = int(sel_inCd.inCd[-6:]) + 1
        inCd = findKey_inCd + (6 - len(str(seq_inCd))) * '0' + str(seq_inCd)

    inSeq = 1
    sel_inSeq = StkIn.query.filter(
        StkIn.siteCd == siteCd, StkIn.inCd == inCd).order_by(StkIn.inSeq.desc()).first()
    if sel_inSeq is not None:
        inSeq = int(sel_inSeq.inSeq) + 1

    # stk_lot insert
    lot = StkLot(siteCd=siteCd,
                 lotNo=lotNo,
                 sn=sn,
                 partCd=partCd,
                 whCd=whCd,
                 loc=loc,
                 curQty=inQty,
                 docQty=inQty,
                 unit=inUnit,
                 stkType=stkType,
                 state='R',
                 regUser=user,
                 regDate=datetime.now(),
                 modUser=None,
                 modDate=None)

    # stk_in insert
    stkIn = StkIn(siteCd=siteCd,
                  inCd=inCd,
                  inSeq=inSeq,
                  inNo=inNo,
                  inDate=inDate,
                  lotNo=lotNo,
                  sn=sn,
                  inKind=inKind,
                  purcYn=purcYn,
                  inType=inType,
                  partCd=partCd,
                  inQty=inQty,
                  inUnit=inUnit,
                  inAmt=inAmt,
                  currency=currency,
                  cmLoc=cmLoc,
                  whCd=whCd,
                  loc=loc,
                  bl=bl,
                  invoice=invoice,
                  inWarr=inWarr,
                  partRank=partRank,
                  stkType=stkType,
                  note=note,
                  state='R',
                  regUser=user,
                  regDate=datetime.now(),
                  modUser=None,
                  modDate=None)

    db.session.add(lot)
    db.session.add(stkIn)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkIn': stkIn.to_json()
    })


@main.route('/api/updPurIncoming', methods=['POST'])
def update_pur_incoming():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    inCd = json_data.get('inCd')
    inSeq = json_data.get('inSeq')
    inDate = json_data.get('inDate')
    inNo = json_data.get('inNo')
    sn = json_data.get('sn')
    inKind = json_data.get('inKind')
    purcYn = json_data.get('purcYn')
    inType = json_data.get('inType')
    partCd = json_data.get('partCd')
    inQty = json_data.get('inQty')
    inUnit = json_data.get('inUnit')
    inAmt = json_data.get('inAmt')
    currency = json_data.get('currency')
    cmLoc = json_data.get('cmLoc')
    whCd = json_data.get('whCd')
    loc = json_data.get('loc')
    bl = json_data.get('bl')
    invoice = json_data.get('invoice')
    inWarr = json_data.get('inWarr')
    partRank = json_data.get('partRank')
    note = json_data.get('note')
    user = json_data.get('user')
    state = json_data.get('state')
    updPriceYn = json_data.get('updPriceYn')

    data = StkIn.query.filter_by(
        siteCd=siteCd, inCd=inCd, inSeq=inSeq, state='R').first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    lot = StkLot.query.filter_by(
        siteCd=siteCd, lotNo=data.lotNo, state='R').first()
    if lot is None:
        return jsonify({
            'result': {
                'code': 8603,
                'msg': '재고정보가 존재하지 않습니다.'
            }
        })

    out = StkOut.query.filter_by(
        siteCd=siteCd, lotNo=data.lotNo, state='R').first()
    if out is not None and updPriceYn != 'Y':
        return jsonify({
            'result': {
                'code': 8604,
                'msg': '출고내역이 존재하여 처리할수 없습니다.'
            }
        })

    if state == 'D':
        if data.poCd is not None:
            chk_sum = 0
            order = PurOrder.query.filter_by(
                siteCd=siteCd, poCd=data.poCd).first()

            if order is not None:
                in_chk = db.session.query(func.sum(StkIn.inQty)).filter(
                    StkIn.siteCd == siteCd, StkIn.poCd == data.poCd, StkIn.state == 'R').group_by(StkIn.poCd).first()
                if in_chk is not None:
                    chk_sum = in_chk[0]

                if chk_sum - data.inQty == 0:
                    order.poState = 'N'
                else:
                    if order.poQty > chk_sum - data.inQty:
                        order.poState = 'P'
                    else:
                        order.poState = 'C'

            db.session.add(order)
    else:
        data.inDate = inDate or data.inDate
        data.inNo = inNo or data.inNo
        data.sn = sn or data.sn
        data.inKind = inKind or data.inKind
        data.purcYn = purcYn or data.purcYn
        data.inType = inType or data.inType
        data.partCd = partCd or data.partCd
        data.inQty = inQty or data.inQty
        data.inUnit = inUnit or data.inUnit
        data.inAmt = inAmt or data.inAmt
        data.currency = currency or data.currency
        data.cmLoc = cmLoc or data.cmLoc
        data.whCd = whCd or data.whCd
        data.loc = loc or data.loc
        data.bl = bl or data.bl
        data.invoice = invoice or data.invoice
        data.inWarr = inWarr or data.inWarr
        data.partRank = partRank or data.partRank
        data.note = note or data.note

        lot.partCd = partCd or lot.partCd
        lot.sn = sn or lot.sn
        lot.curQty = inQty or lot.curQty
        lot.docQty = inQty or lot.docQty
        lot.whCd = whCd or lot.whCd
        lot.loc = loc or lot.loc
        lot.unit = inUnit or lot.unit

    data.modUser = user or data.modUser
    data.modDate = datetime.now()
    data.state = state or data.state

    lot.modUser = user or lot.modUser
    lot.modDate = datetime.now()
    lot.state = state or lot.state

    db.session.add(data)
    db.session.add(lot)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        }
    })


@main.route('/api/updPurIncomingPrice', methods=['POST'])
def update_pur_incoming_price():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    inCd = json_data.get('inCd')
    inSeq = json_data.get('inSeq')
    inAmt = json_data.get('inAmt')
    user = json_data.get('user')
    state = json_data.get('state')

    data = StkIn.query.filter_by(
        siteCd=siteCd, inCd=inCd, inSeq=inSeq, state='R').first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    lot = StkLot.query.filter_by(
        siteCd=siteCd, lotNo=data.lotNo, state='R').first()
    if lot is None:
        return jsonify({
            'result': {
                'code': 8603,
                'msg': '재고정보가 존재하지 않습니다.'
            }
        })

    data.inAmt = inAmt or data.inAmt
    data.modUser = user or data.modUser
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        }
    })
