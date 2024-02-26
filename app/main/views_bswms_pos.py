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
import copy

from . import main

@main.route('/api/selPosMnge', methods=['POST'])
def select_pos_mnge():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    dateType = json_data.get('dateType')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    
    reseller = json_data.get('reseller')
    resellerText  = json_data.get('resellerText')
    endUser = json_data.get('endUser')
    endUserText = json_data.get('endUserText')
    spa = json_data.get('spa')
    posState = json_data.get('posState')
    am = json_data.get('am')
    outNo = json_data.get('outNo')
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()
    
    sql = "SELECT t.*, \
                  fn_get_codename('P0001', t.posState1) AS posStateNm1, \
                  case when t.posState1 in ('C', 'W') then t.posState1 else 'W' end AS posStateSave \
           FROM ( \
                SELECT '0' as chk, \
                    a.siteCd, \
                    a.poCd, \
                    a.poNo, \
                    CONCAT(LEFT(a.poDate, 4), '-', SUBSTRING(a.poDate, 5, 2), '-', RIGHT(a.poDate, 2)) AS poDate, \
                    a.poState, \
                    fn_get_codename('P0002', a.poState) AS poStateNm, \
                    a.poType1, \
                    fn_get_codename('P0003', a.poType1) AS poType1Nm, \
                    a.poType2, \
                    fn_get_codename('P0004', a.poType2) AS poType2Nm, \
                    a.poType3, \
                    fn_get_codename('P0005', a.poType3) AS poType3Nm, \
                    a.partCd, e.partNm, \
                    a.custCd, f.custNm, \
                    a.soNo, \
                    a.poQty, \
                    IFNULL(a.unitAmt, 0) * IFNULL(a.poQty, 0) AS listAmt, \
                    a.unitAmt, \
                    a.purcAmt, \
                    a.taxAmt, \
                    IFNULL(a.purcAmt, 0) + IFNULL(a.taxAmt, 0) AS totPurcAmt, \
                    a.currency, \
                    fn_get_codename('S0006', a.currency) AS currencyNm, \
                    a.posState, \
                    fn_get_codename('P0001', a.posState) AS posStateNm, \
                    b.lotNo, \
                    c.sn, c.whCd, c.loc, c.curQty, c.docQty, c.unit,\
                    d.posCd, \
                    d.spa, \
                    CONCAT(LEFT(d.posDate, 4), '-', SUBSTRING(d.posDate, 5, 2), '-', RIGHT(d.posDate, 2)) AS posDate, \
                    d.posQty, d.dc, \
                    d.reseller, \
                    d.endUser, \
                    d.netPos, d.am, d.partner, d.jda, d.vertical, d.year, d.quater,\
                    d.week, d.note, d.state, \
                    fn_get_custname_en(d.siteCd, d.reseller) AS resellerNm, \
                    fn_get_custname_en(d.siteCd, d.endUser) AS endUserNm, \
                    /*IFNULL((SELECT CASE WHEN posState = 'D' THEN null ELSE posState END FROM pos_pos_log WHERE siteCd = a.siteCd AND poCd = a.poCd AND lotNo = c.lotNo ORDER BY regDate DESC LIMIT 1), a.posState) AS posState1*/ \
                    c.posState AS posState1, \
                    g.outNo, \
                    CONCAT(LEFT(g.outDate, 4), '-', SUBSTRING(g.outDate, 5, 2), '-', RIGHT(g.outDate, 2)) AS outDate, \
                    g.requester AS outRequester, g.custCd AS outCustCd, fn_get_custName_en(g.siteCd, g.custCd) AS outCustNm, \
                    s.spaQty, \
                    CONCAT(LEFT(s.dateEffective, 4), '-', SUBSTRING(s.dateEffective, 5, 2), '-', RIGHT(s.dateEffective, 2)) AS dateEffective, \
                    CONCAT(LEFT(s.dateExpiration, 4), '-', SUBSTRING(s.dateExpiration, 5, 2), '-', RIGHT(s.dateExpiration, 2)) AS dateExpiration, \
                    case when s.spa IS NULL then null \
                        when d.posDate < s.dateEffective then 'Y' \
                        ELSE null \
                    END AS spaEffectiveErr, \
                    case when s.spa IS NULL then null \
                        when d.posDate > s.dateExpiration then 'Y' \
                        ELSE null \
                    END AS spaExpirationErr, \
                    case when s.spa IS NULL then null \
                        when (SELECT sum(x1.posQty) \
                                    FROM pos_pos x1 \
                                    INNER JOIN stk_lot x2 \
                                    ON x1.siteCd = x2.siteCd \
                                    AND x1.lotNo = x2.lotNo \
                                    WHERE x1.siteCd = d.siteCd \
                                    AND x1.spa = d.spa \
                                    AND x1.state = 'R' \
                                    AND x2.partCd = c.partCd) > s.spaQty then 'Y' \
                        ELSE null \
                    END AS spaQtyErr, \
                    d.regUser as posRegUser, \
                    d.regDate AS posRegDate \
                FROM pur_order a \
                INNER JOIN stk_in b \
                ON a.siteCd = b.siteCd \
                AND a.poCd = b.poCd \
                INNER JOIN stk_lot c \
                ON c.lotNo = b.lotNo \
                AND c.siteCd = b.siteCd \
                LEFT OUTER JOIN pos_pos d \
                ON d.siteCd = a.siteCd \
                AND b.lotNo = d.lotNo \
                AND d.state = 'R' \
                AND d.poCd = a.poCd \
                LEFT OUTER JOIN mst_part e \
                ON a.siteCd = e.siteCd \
                AND a.partCd = e.partCd \
                LEFT OUTER JOIN mst_cust f \
                ON a.siteCd = f.siteCd \
                AND a.custCd = f.custCd \
                LEFT OUTER JOIN stk_out g \
                ON c.siteCd = g.siteCd \
                AND c.lotNo = g.lotNo \
                AND g.state = 'R' \
                LEFT OUTER JOIN ( \
                    SELECT s1.siteCd, s1.spa, s1.partCd, SUM(s1.qty) AS spaQty, MAX(s2.dateEffective) AS dateEffective, MIN(s2.dateExpiration) AS dateExpiration \
                    FROM pos_spa s1 \
                    INNER JOIN pos_spa_ext s2 \
                    ON s1.siteCd = s2.siteCd \
                    AND s1.spaCd = s2.spaCd \
                    AND s1.spaSeq = s2.spaSeq \
                    WHERE s1.state = 'R' \
                    AND s2.state = 'R' \
                    GROUP BY s1.siteCd, s1.spa, s1.partCd \
                ) s \
                ON d.siteCd = s.siteCd \
                AND d.spa = s.spa \
                AND c.partCd = s.partCd	\
                WHERE a.siteCd = '" + siteCd + "' \
                AND a.state = 'R' AND b.state = 'R' AND c.state = 'R' \
                AND a.poType2 = 'P' \
            "
    if dateType != '':
        if dateType == 'A':
            sql += " AND a.poDate BETWEEN '" + fDate + "' AND  '"+ tDate + "' "
        elif dateType == 'B':
            sql += " AND d.posDate BETWEEN '" + fDate + "' AND  '"+ tDate + "' "
    if reseller is not None and reseller != '':
        sql += " AND d.reseller LIKE '%" + reseller + "%' "
    # elif resellerText != '':
    #     sql += "AND (d.reseller LIKE CONCAT ('%', '{resellerText}','%')) OR (d.resellerNm LIKE CONCAT('%','{resellerText}','%'))".format_map({'resellerText':resellerText})
    if endUser is not None and endUser != '':
        sql += " AND d.endUser LIKE '%" + endUser + "%' "       
    # elif endUserText != '':
    #     sql += "AND (d.endUser LIKE CONCAT ('%', '{endUserText}','%')) OR (d.endUserNm LIKE CONCAT('%','{endUserText}','%'))".format_map({'endUserText':endUserText})
    if outNo is not None and outNo != '':
        sql += " AND g.outNo LIKE '%" + outNo + "%' "   
    if spa is not None and spa != '':  
        sql += "AND d.spa LIKE '%{spa}%'".format_map({'spa':spa})    
    if am is not None and am != '':  
        sql += "AND d.am LIKE '%{am}%'".format_map({'am':am})    
    sql += ") t "
    if posState is not None and posState != '':  
        sql += " WHERE t.posState1 = '{posState1}'".format_map({'posState1':posState})
    sql += " ORDER BY t.poCd desc, t.lotNo desc;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()
    print('DATA = ', data)
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
        dic['partCd'] = tr[13]
        dic['partNm'] = tr[14]
        dic['custCd'] = tr[15]
        dic['custNm'] = tr[16]
        dic['soNo'] = tr[17]
        dic['poQty'] = tr[18]
        dic['listAmt'] = tr[19]
        dic['unitAmt'] = tr[20]
        dic['purcAmt'] = tr[21]
        dic['taxAmt'] = tr[22]
        dic['totPurcAmt'] = tr[23]
        dic['currency'] = tr[24]
        dic['currencyNm'] = tr[25]
        dic['posState'] = tr[26]
        dic['posStateNm'] = tr[27]
        dic['lotNo'] = tr[28]
        dic['sn'] = tr[29]
        dic['whCd'] = tr[30]
        dic['loc'] = tr[31]
        dic['curQty'] = tr[32]
        dic['docQty'] = tr[33]
        dic['unit'] = tr[34]
        dic['posCd'] = tr[35]        
        dic['spa1'] = tr[36]
        dic['posDate1'] = tr[37]
        dic['posQty'] = tr[38]
        dic['dc'] = tr[39]
        dic['reseller'] = tr[40]
        dic['endUser'] = tr[41]
        dic['netPos'] = tr[42]
        dic['am'] = tr[43]
        dic['partner'] = tr[44]
        dic['jda'] = tr[45]
        dic['vertical'] = tr[46]
        dic['year'] = tr[47]
        dic['quater'] = tr[48]
        dic['week'] = tr[49]
        dic['note'] = tr[50]
        dic['state'] = tr[51]        
        dic['resellerNm'] = tr[52]
        dic['endUserNm'] = tr[53]
        dic['posState1'] = tr[54]
        dic['outNo'] = tr[55]
        dic['outDate'] = tr[56]
        dic['outRequester'] = tr[57]
        dic['outCustCd'] = tr[58]
        dic['outCustNm'] = tr[59]
        dic['spaQty'] = tr[60]
        dic['dateEffective'] = tr[61]
        dic['dateExpiration'] = tr[62]
        dic['spaEffectiveErr'] = tr[63]
        dic['spaExpirationErr'] = tr[64]
        dic['spaQtyErr'] = tr[65]
        dic['posRegUser'] = tr[66]
        dic['posRegDate'] = None if tr[67] is None else tr[67] if tr[67] == '0000-00-00 00:00:00' else tr[67].strftime('%Y-%m-%d %H:%M:%S')
        dic['posStateNm1'] = tr[68]
        dic['posStateSave'] = tr[69]

        data[index] = dic
    # print("data = ", dic)
    #return jsonify({'order': data})    
    return simplejson.dumps({'pos': data})

@main.route('/api/insPosMnge', methods=['POST'])
def insert_pos_mnge():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    posState = json_data.get('posState')
    spa = json_data.get('spa')
    posDate = json_data.get('posDate')
    posQty = json_data.get('posQty')
    dc = json_data.get('dc')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    netPos = json_data.get('netPos')
    am = json_data.get('am')
    partner = json_data.get('partner')
    jda = json_data.get('jda')
    vertical = json_data.get('vertical')
    year = json_data.get('year')
    quater = json_data.get('quater')
    week = json_data.get('week')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    lot = StkLot.query.filter(StkLot.siteCd == siteCd, StkLot.lotNo == lotNo, StkLot.state == 'R').first()

    findKey = 'POS' + posDate[-6:] #datetime.now().strftime('%y%m%d')
    seq = 1
    sel = PosPo.query.filter(PosPo.siteCd == siteCd, PosPo.posCd.like(findKey + '%')).order_by(PosPo.posCd.desc()).first()
    if sel is not None:
        seq = int(sel.posCd[-6:]) + 1    
    posCd = findKey + (6 - len(str(seq))) * '0' + str(seq)
   
    pos = PosPo(siteCd=siteCd,
                posCd=posCd,
                posState=posState,
                spa=spa,
                posDate=posDate,
                posQty=posQty,
                dc=dc,
                reseller=reseller,
                endUser=endUser,
                netPos=netPos,
                am=am,
                partner=partner,
                jda=jda,
                vertical=vertical,
                year=year,
                quater=quater,
                week=week,
                poCd=poCd,
                lotNo=lotNo,
                note=note,
                state=state,
                regUser=user,
                regDate=datetime.now(),
                modUser=None,
                modDate=None)
    db.session.add(pos)
    
    seqLog = 1
    selLog = PosPosLog.query.filter(PosPosLog.siteCd == siteCd, PosPosLog.posCd == posCd).order_by(PosPosLog.logSeq.desc()).first()
    if selLog is not None:
        seqLog = int(selLog.logSeq) + 1    
    logSeq = seqLog

    posLog = PosPosLog(siteCd=siteCd,
                posCd=posCd,
                logSeq=logSeq,                
                posState=posState,
                spa=spa,
                posDate=posDate, 
                posQty=posQty,
                dc=dc,
                reseller=reseller,
                endUser=endUser,
                netPos=netPos,
                am=am,
                partner=partner,
                jda=jda,
                vertical=vertical,
                year=year,
                quater=quater,
                week=week,
                poCd=poCd,
                lotNo=lotNo,
                note=note,      
                state=state,
                regUser=user,
                regDate=datetime.now(),
                modUser=None,
                modDate=None)
    db.session.add(posLog)

    if lot is not None:
        lot.posState = posState
        lot.modUser = user
        lot.modDate = datetime.now()
        db.session.add(lot)

    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'pos': pos.to_json()
    })

@main.route('/api/updPosMnge', methods=['POST'])
def update_pos_mnge():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    posState = json_data.get('posState')
    spa = json_data.get('spa')
    posDate = json_data.get('posDate')
    posQty = json_data.get('posQty')
    dc = json_data.get('dc')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    netPos = json_data.get('netPos')
    am = json_data.get('am')
    partner = json_data.get('partner')
    jda = json_data.get('jda')
    vertical = json_data.get('vertical')
    year = json_data.get('year')
    quater = json_data.get('quater')
    week = json_data.get('week')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = PosPo.query.filter_by(siteCd = siteCd, posCd = posCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })    

    prePosState = data.posState

    lot = StkLot.query.filter(StkLot.siteCd == siteCd, StkLot.lotNo == lotNo, StkLot.state == 'R').first()
    
    if state != 'D':
        data.posState = posState       
        data.spa = spa
        data.posDate = posDate
        data.posQty = posQty
        data.dc = dc
        data.reseller = reseller
        data.endUser = endUser
        data.netPos = netPos
        data.am = am
        data.partner = partner
        data.jda = jda
        data.vertical = vertical
        data.year = year
        data.quater = quater  
        data.week = week
        data.poCd = poCd
        data.lotNo = lotNo
        data.note = note  
        data.modUser = user
        data.modDate = datetime.now()
    data.posState = posState      
    data.state = state

    print("data = ", data)
    db.session.add(data)

    if prePosState != posState:
        seqLog = 1
        selLog = PosPosLog.query.filter(PosPosLog.siteCd == siteCd, PosPosLog.posCd == posCd).order_by(PosPosLog.logSeq.desc()).first()
        if selLog is not None:
            seqLog = int(selLog.logSeq) + 1    
        logSeq = seqLog

        posLog = PosPosLog(siteCd=siteCd,
                    posCd=posCd,
                    logSeq=logSeq,                
                    posState=posState,
                    spa=spa,
                    posDate=posDate, 
                    posQty=posQty,
                    dc=dc,
                    reseller=reseller,
                    endUser=endUser,
                    netPos=netPos,
                    am=am,
                    partner=partner,
                    jda=jda,
                    vertical=vertical,
                    year=year,
                    quater=quater,
                    week=week,
                    poCd=poCd,
                    lotNo=lotNo,
                    note=note,      
                    state=state,
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        db.session.add(posLog)

    if lot is not None:
        lot.posState = 'N' if posState == 'D' else posState
        lot.modUser = user
        lot.modDate = datetime.now()
        db.session.add(lot)

    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

@main.route('/api/selPosSales', methods=['POST'])
def select_pos_sales():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    year = json_data.get('year')
    quater = json_data.get('quater')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    spa = json_data.get('spa')
    partner = json_data.get('partner')
    vertical = json_data.get('vertical')
    am = json_data.get('am')
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()
    
    sql = "SELECT * \
           FROM ( \
                SELECT '0' as chk, \
                    a.siteCd, \
                    a.poCd, \
                    a.poNo, \
                    CONCAT(LEFT(a.poDate, 4), '-', SUBSTRING(a.poDate, 5, 2), '-', RIGHT(a.poDate, 2)) AS poDate, \
                    a.poState, fn_get_codename('P0002', a.poState) AS poStateNm, \
                    a.poType1, fn_get_codename('P0003', a.poType1) AS poType1Nm, \
                    a.poType2, fn_get_codename('P0004', a.poType2) AS poType2Nm, \
                    a.poType3, fn_get_codename('P0005', a.poType3) AS poType3Nm, \
                    a.partCd, e.partNm, \
                    a.custCd, f.custNm, \
                    a.soNo, \
                    a.poQty, \
                    IFNULL(a.unitAmt, 0) * IFNULL(a.poQty, 0) AS listAmt, \
                    a.unitAmt, \
                    a.purcAmt, \
                    a.taxAmt, \
                    IFNULL(a.purcAmt, 0) + IFNULL(a.taxAmt, 0) AS totPurcAmt, \
                    a.currency, fn_get_codename('S0006', a.currency) AS currencyNm, \
                    a.posState, fn_get_codename('P0001', a.posState) AS posStateNm, \
                    b.lotNo, \
                    c.sn, c.whCd, c.loc, c.curQty, c.docQty, c.unit,\
                    d.posCd, \
                    CASE WHEN d.posCd is null then a.posState else d.posState end AS posState1, \
                    fn_get_codename('P0001', CASE WHEN d.posCd is null then a.posState else d.posState end) AS posStateNm1, \
                    d.spa, \
                    CONCAT(LEFT(d.posDate, 4), '-', SUBSTRING(d.posDate, 5, 2), '-', RIGHT(d.posDate, 2)) AS posDate, \
                    d.posQty, d.dc, \
                    d.reseller, \
                    d.endUser, \
                    d.netPos, d.am, d.partner, d.jda, d.vertical, d.year, d.quater,\
                    d.week, d.note, d.state, \
                    fn_get_custname(d.siteCd, d.reseller) AS resellerNm, \
                    fn_get_custname(d.siteCd, d.endUser) AS endUserNm \
                FROM pur_order a \
                INNER JOIN stk_in b \
                ON a.siteCd = b.siteCd \
                AND a.poCd = b.poCd \
                INNER JOIN stk_lot c \
                ON c.lotNo = b.lotNo \
                AND c.siteCd = b.siteCd \
                LEFT OUTER JOIN pos_pos d \
                ON d.siteCd = a.siteCd \
                AND b.lotNo = d.lotNo \
                AND d.state = 'R' \
                AND d.poCd = a.poCd \
                LEFT OUTER JOIN mst_part e \
                ON a.siteCd = e.siteCd \
                AND a.partCd = e.partCd \
                LEFT OUTER JOIN mst_cust f \
                ON a.siteCd = f.siteCd \
                AND a.custCd = f.custCd \
                WHERE a.siteCd = '" + siteCd + "' \
                AND d.posState = 'C' \
            "
    if reseller != '':
        sql += "AND d.reseller LIKE '%" + reseller + "%'"
    if endUser != '':
        sql += "AND d.endUser LIKE '%" + endUser + "%'"
    if spa != '':  
        sql += "AND d.spa LIKE '%{spa}%'".format_map({'spa':spa})    
    if am != '':  
        sql += "AND d.am LIKE '%{am}%'".format_map({'am':am})
    if year != '':  
        sql += "AND d.year LIKE '%{year}%'".format_map({'year':year})
    if quater != '':  
        sql += "AND d.quater LIKE '%{quater}%'".format_map({'quater':quater})
    if partner != '':  
        sql += "AND d.partner LIKE '%{partner}%'".format_map({'partner':partner})
    if vertical != '':  
        sql += "AND d.vertical LIKE '%{vertical}%'".format_map({'vertical':vertical})
    sql += ") t "
    sql += " ORDER BY t.poCd;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()
    print('DATA = ', data)
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
        dic['partCd'] = tr[13]
        dic['partNm'] = tr[14]
        dic['custCd'] = tr[15]
        dic['custNm'] = tr[16]
        dic['soNo'] = tr[17]
        dic['poQty'] = tr[18]
        dic['listAmt'] = tr[19]
        dic['unitAmt'] = tr[20]
        dic['purcAmt'] = tr[21]
        dic['taxAmt'] = tr[22]
        dic['totPurcAmt'] = tr[23]
        dic['currency'] = tr[24]
        dic['currencyNm'] = tr[25]
        dic['posState'] = tr[26]
        dic['posStateNm'] = tr[27]
        dic['lotNo'] = tr[28]
        dic['sn'] = tr[29]
        dic['whCd'] = tr[30]
        dic['loc'] = tr[31]
        dic['curQty'] = tr[32]
        dic['docQty'] = tr[33]
        dic['unit'] = tr[34]
        dic['posCd'] = tr[35]
        dic['posState1'] = tr[36]
        dic['posStateNm1'] = tr[37]
        dic['spa1'] = tr[38]
        dic['posDate1'] = tr[39]
        dic['posQty'] = tr[40]
        dic['dc'] = tr[41]
        dic['reseller'] = tr[42]
        dic['endUser'] = tr[43]
        dic['netPos'] = tr[44]
        dic['am'] = tr[45]
        dic['partner'] = tr[46]
        dic['jda'] = tr[47]
        dic['vertical'] = tr[48]
        dic['year'] = tr[49]
        dic['quater'] = tr[50]
        dic['week'] = tr[51]
        dic['note'] = tr[52]
        dic['state'] = tr[53]
        dic['state'] = tr[53]
        dic['resellerNm'] = tr[54]
        dic['endUserNm'] = tr[55]

        data[index] = dic
    print("data = ", dic)
    #return jsonify({'order': data})    
    return simplejson.dumps({'pos': data})

@main.route('/api/insPosSales', methods=['POST'])
def update_pos_sales():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    posState = json_data.get('posState')
    spa = json_data.get('spa')
    posDate = json_data.get('posDate')
    posQty = json_data.get('posQty')
    dc = json_data.get('dc')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    netPos = json_data.get('netPos')
    am = json_data.get('am')
    partner = json_data.get('partner')
    jda = json_data.get('jda')
    vertical = json_data.get('vertical')
    year = json_data.get('year')
    quater = json_data.get('quater')
    week = json_data.get('week')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = PosPo.query.filter_by(siteCd = siteCd, posCd = posCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    if state != 'D':
        data.posState = posState or data.posState        
        data.spa = spa or data.spa
        data.posDate = posDate or data.posDate
        data.posQty = posQty or data.posQty
        data.dc = dc or data.dc
        data.reseller = reseller or data.reseller
        data.endUser = endUser or data.endUser
        data.netPos = netPos or data.netPos
        data.am = am or data.am
        data.partner = partner or data.partner
        data.jda = jda or data.jda
        data.vertical = vertical or data.vertical
        data.year = year or data.year
        data.quater = quater or data.quater    
        data.week = week or data.week
        data.poCd = poCd or data.poCd
        data.lotNo = lotNo or data.lotNo
        data.note = note or data.note    
        data.modUser = user or data.modUser
        data.modDate = datetime.now()
    data.posState = posState or data.posState        
    data.state = state or data.state

    print("data = ", data)
    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

@main.route('/api/chkCmReg', methods=['POST'])
def chkeck_cm_registration():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    print('JSON_DATA : ', json_data)
    cmReg = ''

    posCmData = PosCm.query.filter_by(siteCd=siteCd, posCd=posCd, cmState='C', state='R').first()
    if posCmData is None:
        cmReg = 'N'
    else:
        cmReg = 'Y'
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'cmReg':cmReg
    })

@main.route('/api/selPosLog', methods=['POST'])
def select_pos_log():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')

    conn = pymysql.connect(host=db.engine.url.host,
                        user=db.engine.url.username,
                        password=db.engine.url.password,
                        db=db.engine.url.database,
                        charset=db.engine.url.query['charset'],
                        port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT d.siteCd, d.posState, \
			        fn_get_codename('P0001', d.posState) AS posStateNm, \
                    d.lotNo, d.posCd, \
                    d.spa, \
                    CONCAT(LEFT(d.posDate, 4), '-', SUBSTRING(d.posDate, 5, 2), '-', RIGHT(d.posDate, 2)) AS posDate, \
                    d.posQty, d.dc, \
                    d.reseller, \
                    fn_get_custname_en(d.siteCd, d.reseller) AS resellerNm, \
                    d.endUser, \
                    fn_get_custname_en(d.siteCd, d.endUser) AS endUserNm, \
                    d.netPos, d.am, d.partner, d.jda, d.vertical, d.year, d.quater,\
                    d.week, d.note, d.state, d.poCd, \
                    a.poState, fn_get_codename('P0002', a.poState) AS poStateNm, \
                    a.poType1, fn_get_codename('P0003', a.poType1) AS poType1Nm, \
                    a.poType2, fn_get_codename('P0004', a.poType2) AS poType2Nm, \
                    a.poType3, fn_get_codename('P0005', a.poType3) AS poType3Nm, \
                    a.poNo, \
                    s.sn, \
                    c.custNmEn AS custNm, b.partNm, \
                    CONCAT(LEFT(a.poDate, 4), '-', SUBSTRING(a.poDate, 5, 2), '-', RIGHT(a.poDate, 2)) AS poDate, \
                    a.soNo, \
                    d.regDate, \
                    d.regUser \
           FROM pos_pos_log d \
           INNER JOIN stk_lot s \
           ON d.lotNo = s.lotNo \
           AND d.siteCd = s.siteCd \
           LEFT OUTER JOIN pur_order a \
           ON d.siteCd = a.siteCd \
           AND d.poCd = a.poCd \
           LEFT OUTER JOIN mst_part b \
           ON a.siteCd = b.siteCd \
           AND a.partCd = b.partCd \
           LEFT OUTER JOIN mst_cust c \
           ON a.siteCd = c.siteCd \
           AND a.custCd = c.custCd \
           WHERE d.siteCd = '" + siteCd + "' \
           "
    if poCd != '':  
        sql += "AND d.poCd = '{poCd}'".format_map({'poCd':poCd})  
    if lotNo != '':
        sql += "AND d.lotNo = '{lotNo}'".format_map({'lotNo':lotNo})  
    sql += " ORDER BY d.regDate;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()
    print('DATA = ', data)
    for index, tr in enumerate(data):
        dic = dict()
        dic['siteCd'] = tr[0]
        dic['posState'] = tr[1]
        dic['posStateNm'] = tr[2]
        dic['lotNo'] = tr[3]
        dic['posCd'] = tr[4]        
        dic['spa'] = tr[5]
        dic['posDate'] = tr[6]
        dic['posQty'] = tr[7]
        dic['dc'] = tr[8]
        dic['reseller'] = tr[9]
        dic['resellerNm'] = tr[10]
        dic['endUser'] = tr[11]
        dic['endUserNm'] = tr[12]
        dic['netPos'] = tr[13]
        dic['am'] = tr[14]
        dic['partner'] = tr[15]
        dic['jda'] = tr[16]
        dic['vertical'] = tr[17]
        dic['year'] = tr[18]
        dic['quater'] = tr[19]
        dic['week'] = tr[20]
        dic['note'] = tr[21]
        dic['state'] = tr[22]
        dic['poCd'] = tr[23]
        dic['poState'] = tr[24]
        dic['poStateNm'] = tr[25]
        dic['poType1'] = tr[26]
        dic['poType1Nm'] = tr[27]
        dic['poType2'] = tr[28]
        dic['poType2Nm'] = tr[29]
        dic['poType3'] = tr[30]
        dic['poType3Nm'] = tr[31]
        dic['poNo'] = tr[32]
        dic['sn'] = tr[33]
        dic['custNm'] = tr[34]
        dic['partNm'] = tr[35]
        dic['poDate'] = tr[36]
        dic['soNo'] = tr[37]
        dic['regDate'] = None if tr[38] is None else tr[38] if tr[38] == '0000-00-00 00:00:00' else tr[38].strftime('%Y-%m-%d %H:%M:%S')
        dic['regUser'] = tr[39]
        
        data[index] = dic
    # print("data = ", dic)
    #return jsonify({'order': data})    
    return simplejson.dumps({'pos_log': data})

@main.route('/api/insPosPosLog', methods=['POST'])
def insert_pos_log():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    #logSeq = json_data.get('logSeq')
    #logState = json_data.get('logState')
    posState = json_data.get('posState')
    spa = json_data.get('spa')
    posDate = json_data.get('posDate')
    posQty = json_data.get('posQty')
    dc = json_data.get('dc')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    netPos = json_data.get('netPos')
    am = json_data.get('am')
    partner = json_data.get('partner')
    jda = json_data.get('jda')
    vertical = json_data.get('vertical')
    year = json_data.get('year')
    quater = json_data.get('quater')
    week = json_data.get('week')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    findKey = 'POS' + posDate[-6:] #datetime.now().strftime('%y%m%d')

    posList = PosPo.query.filter(PosPo.siteCd == siteCd, PosPo.posCd == posCd).order_by(PosPo.posCd.desc()).first()
    if posList is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    seq = 1
    sel = PosPosLog.query.filter(PosPosLog.siteCd == siteCd, PosPosLog.posCd == posCd).order_by(PosPosLog.logSeq.desc()).first()
    if sel is not None:
        seq = int(sel.logSeq) + 1    
    logSeq = seq

    pos = PosPosLog(siteCd=siteCd,
                posCd=posCd,
                logSeq=logSeq,
                #logState=logState,
                posState=posState,
                spa=spa,
                posDate=posDate, 
                posQty=posQty,
                dc=dc,
                reseller=reseller,
                endUser=endUser,
                netPos=netPos,
                am=am,
                partner=partner,
                jda=jda,
                vertical=vertical,
                year=year,
                quater=quater,
                week=week,
                poCd=poCd,
                lotNo=lotNo,
                note=note,      
                state=state,
                regUser=user,
                regDate=datetime.now(),
                modUser=None,
                modDate=None)

    db.session.add(pos)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })   

@main.route('/api/updPosSales', methods=['POST'])
def update_pos_Sales():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    posCd = json_data.get('posCd')
    posState = json_data.get('posState')
    spa = json_data.get('spa')
    posDate = json_data.get('posDate')
    posQty = json_data.get('posQty')
    dc = json_data.get('dc')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    netPos = json_data.get('netPos')
    am = json_data.get('am')
    partner = json_data.get('partner')
    jda = json_data.get('jda')
    vertical = json_data.get('vertical')
    year = json_data.get('year')
    quater = json_data.get('quater')
    week = json_data.get('week')
    poCd = json_data.get('poCd')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = PosPo.query.filter_by(siteCd = siteCd, posCd = posCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    if state != 'D':
        data.posState = posState or data.posState        
        data.spa = spa or data.spa
        data.posDate = posDate or data.posDate
        data.posQty = posQty or data.posQty
        data.dc = dc or data.dc
        data.reseller = reseller or data.reseller
        data.endUser = endUser or data.endUser
        data.netPos = netPos or data.netPos
        data.am = am or data.am
        data.partner = partner or data.partner
        data.jda = jda or data.jda
        data.vertical = vertical or data.vertical
        data.year = year or data.year
        data.quater = quater or data.quater    
        data.week = week or data.week
        data.poCd = poCd or data.poCd
        data.lotNo = lotNo or data.lotNo
        data.note = note or data.note    
        data.modUser = user or data.modUser
        data.modDate = datetime.now()
    data.posState = posState or data.posState        
    data.state = state or data.state

    print("data = ", data)
    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

@main.route('/api/selReseller', methods=['POST'])
def select_pos_reseller():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    custType = json_data.get('custType')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    cp = MstCust.query.filter(MstCust.siteCd==siteCd, MstCust.custType.like('%' + 'R' + '%'), MstCust.custCd.like('%' + custCd + '%') | MstCust.custNm.like('%' + custNm + '%') | MstCust.custNmEn.like('%' + custNm + '%'), MstCust.state=='R').all()    

    return jsonify({
        'cust': [c.to_json() for c in cp]
    })

@main.route('/api/regReseller', methods=['POST'])
def regist_pos_reseller():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    #custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
    varId = json_data.get('varId')
    #sellYn = json_data.get('sellYn')
    #purcYn = json_data.get('purcYn')
    address1 = json_data.get('address1')
    address2 = json_data.get('address2')
    address3 = json_data.get('address3')
    city = json_data.get('city')
    province = json_data.get('province')
    country = json_data.get('country')
    zipCode = json_data.get('zipCode')
    #contact = json_data.get('contact')
    #phone = json_data.get('phone')
    #fax = json_data.get('fax')
    #corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    user = json_data.get('user')    

    
    chk = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()

    findKey = 'R'  #datetime.now().strftime('%y%m%d')
    seq = 1
    sel = MstCust.query.filter(MstCust.siteCd == siteCd, MstCust.custCd.like(findKey + '%')).order_by(MstCust.custCd.desc()).first()
    if sel is not None:
        seq = int(sel.custCd[-5:]) + 1    
    custCd = findKey + (5 - len(str(seq))) * '0' + str(seq)

    if chk is not None:
        chk.custNm = custNm
        chk.custNmEn = custNmEn
        # chk.custAbb = custAbb
        chk.custCd = custCd
        chk.custType = custType
        chk.varId = varId
        # chk.sellYn = sellYn
        # chk.purcYn = purcYn
        chk.address1 = address1
        chk.address2 = address2
        chk.address3 = address3
        chk.city = city
        chk.province = province
        chk.country = country
        chk.zipCode = zipCode
        # chk.contact = contact
        # chk.phone = phone
        # chk.fax = fax
        # chk.corpNo = corpNo
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
            'cust': chk.to_json()
        })
    else:
        data = MstCust(
                    siteCd=siteCd,
                    custCd=custCd,
                    custNm=custNm,
                    custNmEn=custNmEn,
                    # custAbb=custAbb,
                    custType=custType,
                    varId=varId,
                    sellYn='N',
                    purcYn='N',
                    address1=address1,
                    address2=address2,
                    address3=address3,
                    city=city,
                    province=province,
                    country=country,
                    zipCode=zipCode,
                    # contact=contact,
                    # phone=phone,
                    # fax=fax,
                    # corpNo=corpNo,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        print("data = ", data)
        db.session.add(data)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'cust': data.to_json()
        })

@main.route('/api/updReseller', methods=['POST'])
def update_pos_reseller():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    #custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
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
    #contact = json_data.get('contact')
    #phone = json_data.get('phone')
    #fax = json_data.get('fax')
    #corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')    

    data = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()
    if user is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.custNm = custNm    
    data.custNmEn = custNmEn
    data.custType = data.custType
    data.varId = varId
    data.address1 = address1
    data.address2 = address2
    data.address3 = address3
    data.city = city
    data.province = province
    data.country = country
    data.zipCode = zipCode    
    data.note = note    
    data.modUser = user
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

@main.route('/api/selEndUser', methods=['POST'])
def select_pos_enduser():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    custType = json_data.get('custType')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    cp = MstCust.query.filter(MstCust.siteCd==siteCd, MstCust.custType.like('%' + 'E' + '%'), MstCust.custCd.like('%' + custCd + '%') | MstCust.custNm.like('%' + custNm + '%') | MstCust.custNmEn.like('%' + custNm + '%'), MstCust.state=='R').all()    

    return jsonify({
        'enduser': [c.to_json() for c in cp]
    })

@main.route('/api/regEndUser', methods=['POST'])
def regist_pos_enduser():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    #custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
    varId = json_data.get('varId')
    #sellYn = json_data.get('sellYn')
    #purcYn = json_data.get('purcYn')
    address1 = json_data.get('address1')
    address2 = json_data.get('address2')
    address3 = json_data.get('address3')
    city = json_data.get('city')
    province = json_data.get('province')
    country = json_data.get('country')
    zipCode = json_data.get('zipCode')
    #contact = json_data.get('contact')
    #phone = json_data.get('phone')
    #fax = json_data.get('fax')
    #corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    user = json_data.get('user')    

    
    chk = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()

    findKey = 'E'  #datetime.now().strftime('%y%m%d')
    seq = 1
    sel = MstCust.query.filter(MstCust.siteCd == siteCd, MstCust.custCd.like(findKey + '%')).order_by(MstCust.custCd.desc()).first()
    if sel is not None:
        seq = int(sel.custCd[-5:]) + 1    
    custCd = findKey + (5 - len(str(seq))) * '0' + str(seq)

    if chk is not None:
        chk.custNm = custNm
        chk.custNmEn = custNmEn
        # chk.custAbb = custAbb
        chk.custCd = custCd
        chk.custType = custType
        chk.varId = varId
        # chk.sellYn = sellYn
        # chk.purcYn = purcYn
        chk.address1 = address1
        chk.address2 = address2
        chk.address3 = address3
        chk.city = city
        chk.province = province
        chk.country = country
        chk.zipCode = zipCode
        # chk.contact = contact
        # chk.phone = phone
        # chk.fax = fax
        # chk.corpNo = corpNo
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
            'enduser': chk.to_json()
        })
    else:
        data = MstCust(
                    siteCd=siteCd,
                    custCd=custCd,
                    custNm=custNm,
                    custNmEn=custNmEn,
                    # custAbb=custAbb,
                    custType=custType,
                    varId=varId,
                    sellYn='N',
                    purcYn='N',
                    address1=address1,
                    address2=address2,
                    address3=address3,
                    city=city,
                    province=province,
                    country=country,
                    zipCode=zipCode,
                    # contact=contact,
                    # phone=phone,
                    # fax=fax,
                    # corpNo=corpNo,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
        
        print("data = ", data)
        db.session.add(data)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'enduser': data.to_json()
        })

@main.route('/api/updEndUser', methods=['POST'])
def update_pos_enduser():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    custCd = json_data.get('custCd')
    custNm = json_data.get('custNm')
    custNmEn = json_data.get('custNmEn')
    #custAbb = json_data.get('custAbb')
    custType = json_data.get('custType')
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
    #contact = json_data.get('contact')
    #phone = json_data.get('phone')
    #fax = json_data.get('fax')
    #corpNo = json_data.get('corpNo')    
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')    

    data = MstCust.query.filter_by(siteCd = siteCd, custCd = custCd).first()
    if user is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    data.custNm = custNm
    data.custNmEn = custNmEn
    data.custType = custType
    data.varId = varId    
    data.address1 = address1
    data.address2 = address2
    data.address3 = address3
    data.city = city
    data.province = province
    data.country = country
    data.zipCode = zipCode
    data.note = note
    data.modUser = user
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'enduser': data.to_json()
    })

@main.route('/api/selPosCm', methods=['POST'])
def cm_Mnge():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    posStDate = json_data.get('posStDate')
    posEdDate = json_data.get('posEdDate')
    reseller = json_data.get('reseller')
    resellerText = json_data.get('resellerText')
    spa = json_data.get('spa')
    endUser = json_data.get('endUser')
    endUserText = json_data.get('endUserText')
    cmNo = json_data.get('cmNo')
    am = json_data.get('am')

    search_query = "AND g.siteCd = '{siteCd}'".format_map({'siteCd':siteCd})

    if reseller != '':
        search_query += "AND g.reseller = '{reseller}'".format_map({'reseller':reseller})
    elif resellerText != '':
        search_query += "AND (g.reseller LIKE CONCAT ('%', '{resellerText}','%')) OR (g.resellerNm LIKE CONCAT('%','{resellerText}','%'))".format_map({'resellerText':resellerText})
    if spa != '':
        search_query += "AND g.spa LIKE '%{spa}%'".format_map({'spa':spa})
    if endUser != '':
        search_query += "AND g.endUser = '{endUser}'".format_map({'endUser':endUser})
    elif endUserText != '':
        search_query += "AND (g.endUser LIKE CONCAT ('%', '{endUserText}','%')) OR (g.endUserNm LIKE CONCAT('%', '{endUserText}','%'))".format_map({'endUserText':endUserText})
    if cmNo != '':
        search_query += "AND h.cmNo LIKE CONCAT ('%', '{cmNo}','%')".format_map({'cmNo':cmNo})
    if am != '':
        search_query += "AND g.am LIKE CONCAT ('%', '{am}','%')".format_map({'am':am})
    if posStDate != '' and posEdDate != '':
        search_query += "AND g.posDate BETWEEN '" + posStDate + "' AND  '"+ posEdDate + "'"
    
    print("SEARCH_QUERY : ", search_query)

    conn = pymysql.connect(host=db.engine.url.host,
                        user=db.engine.url.username,
                        password=db.engine.url.password,
                        db=db.engine.url.database,
                        charset=db.engine.url.query['charset'],
                        port=db.engine.url.port)

    curs = conn.cursor()

    sql = """
    SELECT g.* ,
        h.cmCd,
        h.cmState, fn_get_codename('P0006', h.cmState) AS poStateNm,
        h.cmDate,
        h.cmNo,
        IFNULL(h.rebAmt, 0.00) AS rebAmt,
        IFNULL(h.remAmt, 0.00) AS remAmt,
        IFNULL(h.excRate, 0.00) AS excRate,
        IFNULL(h.rebWonAmt, 0.00) AS rebWonAmt,
        IFNULL(h.costWonAmt, 0.00) AS costWonAmt,
        h.posCd,
        h.note,
        i.custNm
	FROM (
		SELECT d.* , 
				 e.partNm,
				 f.inAmt
			FROM(
		        SELECT a.siteCd,
		             b.poCd,
		             b.poNo,
		             b.poState, fn_get_codename('P0002', b.poState) AS poStateNm,
		             b.poDate,
		             b.poType1, fn_get_codename('P0003', b.poType1) AS poType1Nm,
		             b.poType2, fn_get_codename('P0004', b.poType2) AS poType2Nm,
		             b.poType3, fn_get_codename('P0005', b.poType3) AS poType3Nm, 
		             b.custCd,
		             c.partCd,
		             b.soNo,
		             b.poQty,
		             b.unitAmt,
		             b.taxAmt,
		             b.purcAmt,
		             b.currency,
		             b.svcStDate,
		             b.svcEdDate,
		             c.lotNo,
		             c.sn,
		             c.whCd,
		             c.loc,
		             c.curQty,
		             c.docQty,
		             c.unit,
		             a.posCd,
		             a.posState, fn_get_codename('P0001', a.posState) AS posStateNm, 
		             a.spa,
		             a.posDate,
		             a.posQty,
		             a.dc,
		             a.reseller, fn_get_custname_en(a.siteCd, a.reseller) AS resellerNm, 
		             a.endUser, fn_get_custname_en(a.siteCd, a.endUser) AS endUserNm ,
		             a.netPos,
		             a.am,
		             a.partner,
		             a.jda,
		             a.vertical,
		             a.YEAR,
		             a.quater,
		             a.WEEK
                     
		        FROM pos_pos AS a
		        INNER JOIN pur_order AS b
		        ON a.poCd = b.poCd
		        AND a.siteCd = b.siteCd
		        INNER JOIN stk_lot AS c
		        ON a.lotNo = c.lotNo
		        AND a.siteCd = c.siteCd
		        
		        AND a.state = 'R'
		        AND b.state = 'R'
		        AND c.state = 'R'
		        WHERE 1=1
		        AND b.poType2 = 'P'
                AND a.posState = 'C'
		    	) AS d
			INNER JOIN mst_part AS e
			ON e.partCd = d.partCd
			AND e.siteCd = d.siteCd
			
			INNER JOIN stk_in AS f
			ON f.lotNo = d.lotNo
			AND f.siteCd = d.siteCd
			
			#WHERE 1=1
         AND e.state = 'R'
         AND f.state = 'R'
	   ) AS g
	   
    LEFT JOIN pos_cm AS h
    ON g.siteCd = h.siteCd	
    AND g.posCd = h.posCd
    AND h.state = 'R'

    LEFT JOIN mst_cust AS i
    ON g.siteCd = i.siteCd
    AND g.custCd = i.custCd    
    WHERE 1=1
    {search_query}

    ORDER BY posDate DESC, g.posCd DESC
    """.format_map({'search_query':search_query})
    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    
    print('BEFORE DATA : ', data)

    for index, cmData in enumerate(data):
        dicCm = dict()
        dicCm['siteCd'] = cmData[0]
        dicCm['poCd'] = cmData[1]
        dicCm['poNo'] = cmData[2]
        dicCm['poState'] = cmData[4]
        dicCm['poDate'] = cmData[5]
        dicCm['poType1'] = cmData[7]
        dicCm['poType2'] = cmData[9]
        dicCm['poType3'] = cmData[11]
        dicCm['custCd'] = cmData[12]
        dicCm['partCd'] = cmData[13]
        dicCm['soNo'] = cmData[14]
        dicCm['poQty'] = cmData[15]
        dicCm['unitAmt'] = cmData[16]
        dicCm['taxAmt'] = cmData[17]
        dicCm['purcAmt'] = cmData[18]
        dicCm['currency'] = cmData[19]
        dicCm['svcStDate'] = cmData[20]
        dicCm['svcEdDate'] = cmData[21]
        dicCm['lotNo'] = cmData[22]
        dicCm['sn'] = cmData[23]
        dicCm['whCd'] = cmData[24]
        dicCm['loc'] = cmData[25]
        dicCm['curQty'] = cmData[26]
        dicCm['docQty'] = cmData[27]
        dicCm['unit'] = cmData[28]
        dicCm['posCd2'] = cmData[29]
        dicCm['posState'] = cmData[31]
        dicCm['spa'] = cmData[32]
        dicCm['posDate'] = cmData[33]
        dicCm['posQty'] = cmData[34]
        dicCm['dc'] = cmData[35]
        dicCm['reseller'] = cmData[36]
        dicCm['resellerNm'] = cmData[37]
        dicCm['endUser'] = cmData[38]
        dicCm['endUserNm'] = cmData[39]
        dicCm['netPos'] = cmData[40]
        dicCm['am'] = cmData[41]
        dicCm['partner'] = cmData[42]
        dicCm['jda'] = cmData[43]
        dicCm['vertical'] = cmData[44]
        dicCm['year'] = cmData[45]
        dicCm['quater'] = cmData[46]
        dicCm['week'] = cmData[47]
        dicCm['partNm'] = cmData[48]
        dicCm['inAmt'] = cmData[49]
        dicCm['cmCd'] = cmData[50]
        dicCm['cmState'] = cmData[51]
        dicCm['cmStateNm'] = cmData[52]
        dicCm['cmDate'] = cmData[53]
        dicCm['cmNo'] = cmData[54]
        dicCm['rebAmt'] = cmData[55]
        dicCm['remAmt'] = cmData[56]
        dicCm['excRate'] = cmData[57]
        dicCm['rebWonAmt'] = cmData[58]
        dicCm['costWonAmt'] = cmData[59]
        dicCm['note'] = cmData[61]
        dicCm['custNm'] = cmData[62]

        data[index] = dicCm
    #return jsonify({
    #    'cmMnge':data
    #})

    print('DATA : ', data)
    return simplejson.dumps({'cmMnge':data})
        

@main.route('/api/insPosCm', methods=['POST'])
def insert_pos_cm_in():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    cmNo = json_data.get('cmNo')
    cmDate = json_data.get('cmDate')
    costWonAmt = json_data.get('costWonAmt')
    remAmt = json_data.get('remAmt')
    excRate = json_data.get('excRate')
    rebAmt = json_data.get('rebAmt')
    rebWonAmt = json_data.get('rebWonAmt')
    posCd = json_data.get('posCd')
    note = json_data.get('note')
    user = json_data.get('user')
    print('JSON_DATA : ', json_data)

    cmDate = cmDate.replace("-","")
    cmDate = cmDate[:8]  

    if costWonAmt == '':
        costWonAmt = 0.0

    pos = PosPo.query.filter_by(siteCd = siteCd, posCd = posCd, state = 'R').first()
    if pos is None:
        return jsonify({
            'result': {
                'code': 8601,
                'msg': 'POS 정보가 존재하지 않습니다.'
            }
        })
    print('POS : ', pos)
    # cm = PosCm.query.filter_by(siteCd = siteCd, cmNo = cmNo, state = 'R').first()
    # if cm is not None:
    #     return jsonify({
    #         'result': {
    #             'code': 8503,
    #             'msg': gettext('8503') 
    #         }
    #     })
    
    #check pos_cm
    findKey = 'CM' + cmDate[-6:]
    print('KEY : ', findKey)
    seq = 1
    sel = PosCm.query.filter(PosCm.siteCd == siteCd, PosCm.cmCd.like(findKey + '%')).order_by(PosCm.cmCd.desc()).first()
    if sel is not None:
        seq = int(sel.cmCd[-6:]) + 1
    cmCd = findKey + (6 - len(str(seq)))* '0' + str(seq)
    print('CMCD : ', cmCd)
    cmState = 'C'
    
    cmData = PosCm(siteCd=siteCd,
                    cmCd=cmCd,
                    cmState=cmState,
                    cmDate=cmDate,
                    cmNo=cmNo,
                    rebAmt=rebAmt,
                    remAmt=remAmt,
                    excRate=excRate,
                    rebWonAmt=rebWonAmt,
                    costWonAmt=costWonAmt,
                    posCd=posCd,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
            
    db.session.add(cmData)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'cm': cmData.to_json()        
    })

# # CM 등록 확인 체크
# @main.route('/api/chkCmReg', methods=['POST'])
# def chkeck_cm_registration():
#     json_data = json.loads(request.data, strict=False)
#     siteCd = json_data.get('siteCd')
#     posCd = json_data.get('posCd')
#     print('JSON_DATA : ', json_data)
#     cmReg = ''

#     posCmData = PosCm.query.filter_by(siteCd=siteCd, posCd=posCd, cmState='C', state='R').first()
#     if posCmData is None:
#         cmReg = 'N'
#     else:
#         cmReg = 'Y'
    
#     return jsonify({
#         'result': {
#             'code': 1000,
#             'msg' : gettext('1000')
#         },
#         'cmReg':cmReg
#     })


@main.route('/api/chkCmUse', methods=['POST'])
def check_cm_use_log():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    cmCd = json_data.get('cmCd')
    cmNo = json_data.get('cmNo')

    print('JSON_DATA :', json_data)
    result = 'N'
    cm = PosCm.query.filter_by(siteCd=siteCd, cmCd=cmCd, cmState='C', state = 'R').first()
    
    if cm is None:
        return jsonify({
            'result': {
                'code': 8601,
                'msg': 'CM 정보가 존재하지 않습니다. '
            }
        })
    
    cmUse = PosCmUse.query.filter_by(siteCd=siteCd, cmCd=cmCd, state='R').first()

    if cmUse is not None:
        result = 'Y'
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'use':result
    })


@main.route('/api/updPosCm', methods=['POST'])
def update_pos_cm():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    cmCd = json_data.get('cmCd')
    cmNo = json_data.get('cmNo')
    cmDate = json_data.get('cmDate')
    costWonAmt = json_data.get('costWonAmt')
    remAmt = json_data.get('remAmt')
    excRate = json_data.get('excRate')
    rebAmt = json_data.get('rebAmt')
    rebWonAmt = json_data.get('rebWonAmt')
    posCd = json_data.get('posCd')
    note = json_data.get('note')
    user = json_data.get('user')
    state = json_data.get('state')
    
    
    print('JSON_DATA : ', json_data)
    cm = PosCm.query.filter_by(siteCd=siteCd, cmCd=cmCd, cmState='C', state='R').first()
    if cm is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : 'cmData has not exist'
            }            
        })
    
    log = PosCmLog.query.filter_by(siteCd=siteCd, cmCd=cmCd, cmState='C', state='R').first()
    if log is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : 'log has not exist'
            }            
        })

    print('LOG : ', log)
    if state == 'R':

        cmDate = cmDate.replace("-","")
        cmDate = cmDate[:8]  
        cm.cmNo = cmNo or cm.cmNo
        cm.cmDate = cmDate or cm.cmDate
        cm.costWonAmt = costWonAmt or cm.costWonAmt
        cm.remAmt = remAmt or cm.remAmt
        cm.excRate = excRate or cm.excRate
        cm.rebAmt = rebAmt or cm.rebAmt
        cm.rebWonAmt = rebWonAmt or cm.rebWonAmt
        cm.note = note or cm.note
        cm.modUser = user or cm.modUser
        cm.modDate = datetime.now()

        log.cmNo = cmNo or log.cmNo
        log.costWonAmt = costWonAmt or log.costWonAmt
        log.remAmt = remAmt or log.remAmt
        log.excRate = excRate or log.excRate
        log.rebAmt = rebAmt or log.rebAmt
        log.rebWonAmt = rebWonAmt or log.rebWonAmt
        log.note = note or log.note
        log.modUser = user or log.modUser
        log.modDate = datetime.now()



    cm.state = state or cm.state
    log.state = state or log.state
    db.session.add(cm)
    db.session.add(log)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

@main.route('/api/selPosCmUse', methods=['POST'])
def select_pos_cm_use():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    cmStDate = json_data.get('cmStDate')
    cmEdDate = json_data.get('cmEdDate')
    soNo = json_data.get('soNo')
    poNo = json_data.get('poNo')
    spa = json_data.get('spa')
    cmNo = json_data.get('cmNo')

    search_query = "AND c.siteCd = '{siteCd}'".format_map({'siteCd':siteCd})

    if soNo != '':
        search_query += "AND d.soNo LIKE CONCAT ('%','{soNo}','%')".format_map({'soNo':soNo})
    if poNo != '':
        search_query += "AND d.poNo LIKE CONCAT ('%', '{poNo}' , '%')".format_map({'poNo':poNo})
    if spa != '':
        search_query += "AND c.spa LIKE CONCAT ('%', '{spa}', '%')".format_map({'spa':spa})
    if cmNo != '':
        search_query += "AND c.cmNo LIKE CONCAT ('%', '{cmNo}', '%')".format_map({'cmNo':cmNo})
    if cmStDate != '' and cmEdDate != '':
        search_query += "AND c.cmDate BETWEEN '" + cmStDate + "' AND  '"+ cmEdDate + "'"
    
    print("SEARCH_QUERY : ", search_query)

    conn = pymysql.connect(host=db.engine.url.host,
                        user=db.engine.url.username,
                        password=db.engine.url.password,
                        db=db.engine.url.database,
                        charset=db.engine.url.query['charset'],
                        port=db.engine.url.port)

    curs = conn.cursor()

    
    sql = """
        SELECT c.*, 
                d.poCd,
                d.poNo,
                d.soNo
        FROM	(
            SELECT a.siteCd, 
                    a.cmCd ,
                    a.cmNo,
                    a.cmDate,
                    a.costWonAmt,
                    a.rebAmt,
                    a.excRate,
                    a.rebWonAmt,
                    a.remAmt,
                    (a.posCd) AS cmPosCd,
                    a.note,
                    b.posCd,  
                    b.posState , fn_get_codename('P0001', b.posState) AS posStateNm,
                    (b.poCd) AS posPoCd,
                    b.lotNo,
                    b.spa
            FROM pos_cm AS a
            INNER JOIN pos_pos AS b
            ON b.posCd = a.posCd
            AND b.siteCd = a.siteCd
            AND a.state = 'R'
            AND b.state = 'R'
            ) AS c
        INNER JOIN pur_order AS d
        ON d.poCd = c.posPoCd
        AND d.siteCd = c.siteCd
        AND d.state = 'R'
    WHERE 1=1 
    {search_query}
    ORDER BY cmDate DESC, cmCd DESC
    """.format_map({'search_query':search_query})

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()
    print('BEFORE DATA : ', data)

    for index, dt in enumerate(data):
        cmUseDic = dict()
        cmUseDic['siteCd'] = dt[0]
        cmUseDic['cmCd'] = dt[1]
        cmUseDic['cmNo'] = dt[2]
        cmUseDic['cmDate'] = dt[3]
        cmUseDic['costWonAmt'] = dt[4]
        cmUseDic['rebAmt'] = dt[5]
        cmUseDic['excRate'] = dt[6]
        cmUseDic['rebWonAmt'] = dt[7]
        cmUseDic['remAmt'] = dt[8]
        cmUseDic['note'] = dt[10]
        cmUseDic['posCd'] = dt[11]
        cmUseDic['posState'] = dt[12]
        cmUseDic['posStateNm'] = dt[13]
        cmUseDic['lotNo'] = dt[15]
        cmUseDic['spa'] = dt[16]
        cmUseDic['poCd'] = dt[17]
        cmUseDic['poNo'] = dt[18]
        cmUseDic['soNo'] = dt[19]
        
        data[index] = cmUseDic
    print('DATA : ',data)
    return simplejson.dumps({'cmUse': data})

@main.route('/api/selPosCmUsePop', methods=['POST'])
def select_select_cm_use():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')

    conn = pymysql.connect(host=db.engine.url.host,
                        user=db.engine.url.username,
                        password=db.engine.url.password,
                        db=db.engine.url.database,
                        charset=db.engine.url.query['charset'],
                        port=db.engine.url.port)
    
    curs = conn.cursor()

    sql = """
       SELECT c.*,
		d.poNo,
		d.soNo
    FROM (
        SELECT a.siteCd, 
                a.cmCd ,
                a.cmNo,
                a.cmDate,
                a.rebAmt,
                a.excRate,
                a.rebWonAmt,
                a.remAmt,
                a.costWonAmt,
                b.spa,
                b.poCd
        
        FROM pos_cm AS a 
        INNER JOIN pos_pos AS b
        ON b.siteCd = a.siteCd
        AND b.posCd = a.posCd
        AND b.state = 'R'
        AND a.state = 'R'
        
        WHERE 1=1
        AND a.remAmt > 0
        ) AS c
        
    INNER JOIN pur_order AS d
    ON d.siteCd = c.siteCd
    AND d.poCd = c.poCd
    AND d.state = 'R'

    WHERE 1=1
    AND c.siteCd='{siteCd}'


    ORDER BY  cmCd DESC, cmDate DESC 

    """.format_map({'siteCd':siteCd})
    

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()


    print('BEFORE DATA : ', data)
    for index, cmUse in enumerate(data):
        dic = dict()
        dic['siteCd'] = cmUse[0]
        dic['cmCd'] = cmUse[1]
        dic['cmNo'] = cmUse[2]
        dic['cmDate'] = cmUse[3]
        dic['rebAmt'] = cmUse[4]
        dic['excRate'] = cmUse[5]
        dic['rebWonAmt'] = cmUse[6]
        dic['remAmt'] = cmUse[7]
        dic['costWonAmt'] = cmUse[8]
        dic['spa'] = cmUse[9]
        dic['poCd'] = cmUse[10]
        dic['poNo'] = cmUse[11]
        dic['soNo'] = cmUse[12]
        
        data[index] = dic

    return simplejson.dumps({'cmUse':data})



@main.route('/api/insPosCmUse', methods=['POST'])
def insert_pos_cm_use():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    preAmt = json_data.get('preAmt')
    useAmt = json_data.get('useAmt')
    remAmt = json_data.get('remAmt')
    cmDate = json_data.get('cmDate')
    note = json_data.get('note')
    user = json_data.get('user')

    print("JSON_DATA : ", json_data)
    cmDate = cmDate.replace("-","")
    cmDate = cmDate[:8]  

    useAmt = float(useAmt)
    cmData = PosCm.query.filter(PosCm.siteCd == siteCd, PosCm.state == 'R', PosCm.remAmt > 0).order_by(PosCm.cmDate.asc(), PosCm.cmCd.asc()).all()
    
    # seq=1
    cmOrigin = copy.deepcopy(cmData)
    # idxData = PosCmUse.query.filter(PosCmUse.siteCd == siteCd, PosCmUse.state == 'R' ).order_by(PosCmUse.useSeq.desc()).first()
    # if idxData is not None:
    #     seq = idxData.useSeq + 1
    
    print('CM Data : ', cmData)
    cnt=0
    sumRebAmt = 0.0
    
    for i in range(len(cmData)):
        sumRebAmt = sumRebAmt + float(cmData[i].remAmt)
        if useAmt >0 :
            cnt = i
            useAmt -= float(cmData[i].remAmt)
            print("[{cnt}]({cmDate}) : {remAmt}".format_map({'cnt': cnt, 'cmDate':cmData[i].cmDate , 'remAmt':cmData[i].remAmt}))
#    sumRebAmt = round(sumRebAmt,2)
#     print('SUMREB : ', sumRebAmt)       
#     if round(sumRebAmt,2) != float(preAmt):
#         return jsonify({
#             'result': {
#                 'code': 8504,
#                 'msg' : '사용 전 잔액이 맞지 않습니다.'
#             }            
#         })     
    print('CNT : ', cnt)
    for u in range(cnt):
        cmData[u].remAmt = 0
    cmData[cnt].remAmt = abs(useAmt)

    sumRemAmt = 0.0
    for index, data in enumerate(cmData):
        sumRemAmt = sumRemAmt + float(data.remAmt)
    
    # print('SUMREM : ', sumRemAmt)   

    # if round(sumRemAmt,2) != float(remAmt):
    #     return jsonify({
    #         'result': {
    #             'code': 8503,
    #             'msg' : '사용 후 잔액이 맞지 않습니다.'
    #         }
    #     })


    for idx in range(cnt+1):

        seq = 1        
        idxData = PosCmUse.query.filter(PosCmUse.siteCd == siteCd, PosCmUse.cmCd == cmData[idx].cmCd ).order_by(PosCmUse.useSeq.desc()).first()
        if idxData is not None:
            seq = idxData.useSeq + 1

        print('RANGE : ',idx)
        print("""
            siteCd : {siteCd},
            cmCd : {cmCd},
            useDate : {cmDate},
            useSeq : {useSeq},
            preAmt : {preAmt},
            useAmt : {useAmt},
            remAmt : {remAmt}

            """.format_map({'siteCd': siteCd, 'cmCd': cmData[idx].cmCd, 'cmDate':cmDate ,'useSeq':seq, 'preAmt':cmOrigin[idx].remAmt, 'useAmt': float(cmOrigin[idx].remAmt) - float(cmData[idx].remAmt),
            'remAmt':cmData[idx].remAmt})
        )

        cmUse = PosCmUse(siteCd=siteCd,
                        cmCd=cmData[idx].cmCd,
                        useSeq = seq,
                        useDate = cmDate,
                        preAmt = cmOrigin[idx].remAmt,
                        useAmt = float(cmOrigin[idx].remAmt) - float(cmData[idx].remAmt),
                        remAmt = cmData[idx].remAmt,
                        note = note,
                        state = 'R',
                        regUser=user,
                        regDate=datetime.now(),
                        modUser=None,
                        modDate=None
                        )

        print("CMUSE : ",cmUse)
        # seq = seq+1
        print('DATA : ', cmData[idx].remAmt)
        db.session.add(cmUse)
        db.session.add(cmData[idx])
    db.session.commit()

    return jsonify({'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }})

@main.route('/api/selPosCmUseLog', methods=['POST'])
def select_pos_cm_use_Log():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    cmCd = json_data.get('cmCd') or ''
    cmNo = json_data.get('cmNo') or ''
    poNo = json_data.get('poNo') or ''
    soNo = json_data.get('soNo') or ''
    start = json_data.get('start') or ''
    end = json_data.get('end') or ''
    spa = json_data.get('spa') or ''
    user = json_data.get('user') or ''

    print('JSON_DATA : ', json_data)

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)
    
    curs = conn.cursor()
    
    search_query = "AND e.siteCd = '{siteCd}'".format_map({'siteCd':siteCd})

    if cmCd != '':
        search_query += "AND e.cmCd = '{cmCd}'".format_map({'cmCd':cmCd})
    if cmNo != '':
        search_query += "AND e.cmNo LIKE CONCAT ('%','{cmNo}', '%')".format_map({'cmNo':cmNo})
    if poNo != '':
        search_query += "AND f.poNo LIKE CONCAT ('%', '{poNo}', '%')".format_map({'poNo':poNo})
    if soNo != '':
        search_query += "AND f.soNo LIKE CONCAT ('%', '{soNo}', '%')".format_map({'soNo':soNo})
    if spa != '':
        search_query += "AND e.spa LIKE CONCAT ('%', '{spa}', '%')".format_map({'spa':spa})
    if start != '' and end != '':
        search_query += "AND e.useDate BETWEEN '{start}' AND  '{end}'".format_map({'start':start, 'end':end})
    
    print("SEARCH_QUERY : ", search_query)

    sql = """
        SELECT e.*,
                f.poNo,
                f.soNo
        FROM(
            SELECT c.*,
                    d.spa,
                    d.poCd
            FROM(
                SELECT a.siteCd,
                        a.cmCd,
                        b.cmNo,
                        a.useSeq,
                        b.cmDate,
                        b.rebAmt,
                        b.excRate,
                        b.rebWonAmt,
                        b.posCd,
                        a.useDate,
                        a.preAmt,
                        a.useAmt,
                        a.remAmt,
                        a.note
                FROM pos_cm_use AS a
                INNER JOIN pos_cm AS b
                ON b.cmCd = a.cmCd
                AND b.siteCd = a.siteCd
                AND a.state = 'R'
                AND b.state = 'R'
                ) AS c
            INNER JOIN pos_pos AS d
            ON d.posCd = c.posCd
            AND d.siteCd = c.siteCd
            AND d.state = 'R'
            ) AS e
        INNER JOIN pur_order AS f
        ON f.poCd = e.poCd
        AND f.siteCd = e.siteCd
        AND f.state = 'R'

        WHERE 1=1
        {search_query}
        ORDER BY useSeq DESC

        """.format_map({'search_query':search_query})


    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, cmLog in enumerate(data):
        dic = dict()
        dic['siteCd'] = cmLog[0]
        dic['cmCd'] = cmLog[1]
        dic['cmNo'] = cmLog[2]
        dic['useSeq'] = cmLog[3]
        dic['cmDate'] = cmLog[4]
        dic['rebAmt'] = cmLog[5]
        dic['excRate'] = cmLog[6]
        dic['rebWonAmt'] = cmLog[7]
        dic['posCd'] = cmLog[8]
        dic['useDate'] = cmLog[9]
        dic['preAmt'] = cmLog[10]
        dic['useAmt'] = cmLog[11]
        dic['remAmt'] = cmLog[12]
        dic['note'] = cmLog[13]
        dic['spa'] = cmLog[14]
        dic['poCd'] = cmLog[15]
        dic['poNo'] = cmLog[16]
        dic['soNo'] = cmLog[17]      
        data[index] = dic

    print('DATA : ', data)
    return simplejson.dumps({'cmLog':data})


@main.route('/api/insPosCmLog', methods=['POST'])
def insert_pos_cm_log():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    cmCd = json_data.get('cmCd')
    # cmNo = json_data.get('cmNo')
    # cmDate = json_data.get('cmDate')
    # posCd = json_data.get('posCd')
    cmState = json_data.get('cmState')
    user = json_data.get('user')
    print('JSON_DATA : ', json_data)
    # cmDate = cmDate.replace("-","")
    # cmDate = cmDate[:8]  

    cmData = None
    # if cmState == 'C':
    #     cmData = PosCm.query.filter_by(siteCd=siteCd, cmNo=cmNo, cmDate=cmDate, posCd=posCd, cmState='C', state='R').first()
    # elif cmState == 'D':
    #     cmData = PosCm.query.filter_by(siteCd=siteCd, cmNo=cmNo, cmDate=cmDate, posCd=posCd, cmState='C').first()

    cmData = PosCm.query.filter_by(siteCd=siteCd, cmCd=cmCd).first()
    if cmData is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : 'Have not cmData'
            }
        })
    
    seq = 1
    sel = PosCmLog.query.filter(PosCmLog.siteCd == siteCd, PosCmLog.cmCd == cmCd).order_by(PosCmLog.logSeq.desc()).first()
    if sel is not None:
        seq = int(sel.logSeq)+1
    
    log = PosCmLog(siteCd=siteCd,
                    cmCd=cmData.cmCd,
                    logSeq=seq,
                    # logState = logState,
                    cmState = cmState,
                    cmDate = cmData.cmDate,
                    cmNo = cmData.cmNo,
                    rebAmt = cmData.rebAmt,
                    remAmt = cmData.remAmt,
                    excRate = cmData.excRate,
                    rebWonAmt = cmData.rebWonAmt,
                    costWonAmt = cmData.costWonAmt,
                    posCd = cmData.posCd,
                    note = cmData.note,
                    state = 'R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
    db.session.add(log)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

@main.route('/api/selPosSpa', methods=['POST'])
def select_pos_spa():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')    
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    custCd = json_data.get('custCd')
    custText = json_data.get('custText')
    spa = json_data.get('spa')
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT '0' AS chk, \
                    concat(left(a.spaDate, 4), '-', SUBSTRING(a.spaDate, 5, 2), '-', RIGHT(a.spaDate, 2)) AS spaDate, \
                    a.spaCd, a.spaSeq, a.spa, \
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
                    b.productLine, b.productFamily, b.lineNumber, b.parentLineNumber, b.configNumber, b.configInstance, b.serviceDuration, b.reportType, b.distributorId, distributorName \
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
            AND a.spaDate BETWEEN '" + fDate + "' AND '" + tDate + "' "            
    if custCd is not None:
        sql += " AND a.endUser = '" + custCd + "' "
    if custText is not None:
        sql += " AND ( a.endUser LIKE CONCAT('%', '" + custText + "', '%') OR c.custNm LIKE CONCAT('%', '" + custText + "', '%') ) "
    if spa is not None:
        sql += " AND a.spa LIKE '%" + spa + "%' " 
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
        dic['spa'] = tr[4]
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

        data[index] = dic
    
    return simplejson.dumps({'posSpa': data})

@main.route('/api/insPosSpa', methods=['POST'])
def insert_pos_spa():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    spaCd = json_data.get('spaCd')
    spaSeq = json_data.get('spaSeq')
    spaDate = json_data.get('spaDate')    
    spa = json_data.get('spa')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    partCd = json_data.get('partCd')
    qty = json_data.get('qty')
    listPrice = json_data.get('listPrice')
    dc = json_data.get('dc')
    extListPrice = json_data.get('extListPrice')
    extDiscount = json_data.get('extDiscount')    
    extNetTotal = json_data.get('extNetTotal')
    note = json_data.get('note')
    user = json_data.get('user')

    reportType = json_data.get('reportType')
    distributorId = json_data.get('distributorId')
    distributorName = json_data.get('distributorName')
    resellerVarId = json_data.get('resellerVarId')
    resellerName = json_data.get('resellerName')
    theatre = json_data.get('theatre')
    region = json_data.get('region')
    dealState = json_data.get('dealState')
    partnerLevel = json_data.get('partnerLevel')
    dateEffective = json_data.get('dateEffective')
    dateExpiration = json_data.get('dateExpiration')
    dateLastPublished = json_data.get('dateLastPublished')
    revision = json_data.get('revision')
    # shipAndDebitId = json_data.get('shipAndDebitId')
    endCustomerId = json_data.get('endCustomerId')
    endUserVatId = json_data.get('endUserVatId')
    endUserName = json_data.get('endUserName')
    endCostomerAddress1 = json_data.get('endCostomerAddress1')
    endCostomerAddress2 = json_data.get('endCostomerAddress2')
    endCostomerAddress3 = json_data.get('endCostomerAddress3')
    endUserCity = json_data.get('endUserCity')
    endUserProvince = json_data.get('endUserProvince')
    endUserZipCode = json_data.get('endUserZipCode')
    endUserCountry = json_data.get('endUserCountry')
    jnprSalesRep = json_data.get('jnprSalesRep')
    lastUpdatedBy = json_data.get('lastUpdatedBy')
    sku = json_data.get('sku')
    skuDescription = json_data.get('skuDescription')
    fulfillmentType = json_data.get('fulfillmentType')
    # quantity = json_data.get('quantity')
    # listPrice = json_data.get('listPrice')
    # discountRateDistributor = json_data.get('discountRateDistributor')
    suggestedDiscountRateReseller = json_data.get('suggestedDiscountRateReseller')
    suggestedDiscountRateEndUser = json_data.get('suggestedDiscountRateEndUser')
    # extendedListPrice = json_data.get('extendedListPrice')
    # extendedDiscount = json_data.get('extendedDiscount')
    # extendedNetTotal = json_data.get('extendedNetTotal')
    productLine = json_data.get('productLine')
    productFamily = json_data.get('productFamily')
    lineNumber = json_data.get('lineNumber')
    parentLineNumber = json_data.get('parentLineNumber')
    configNumber = json_data.get('configNumber')
    configInstance = json_data.get('configInstance')
    serviceDuration = json_data.get('serviceDuration')

    # check pos_spa
    if spaCd is None:
        findKey_spaCd = 'SPA' + spaDate[-6:]
        seq_spaCd = 1
        sel_spaCd = PosSpa.query.filter(PosSpa.siteCd == siteCd, PosSpa.spaCd.like(findKey_spaCd + '%')).order_by(PosSpa.spaCd.desc()).first()
        if sel_spaCd is not None:
            seq_spaCd = int(sel_spaCd.spaCd[-6:]) + 1
        spaCd = findKey_spaCd + (6 - len(str(seq_spaCd))) * '0' + str(seq_spaCd)    
    
    data = PosSpa.query.filter_by(siteCd = siteCd, spaCd = spaCd, spaSeq = spaSeq).first()
    
    if data is None:
        # pos_spa insert
        posSpa = PosSpa(siteCd=siteCd,
                        spaCd=spaCd,
                        spaSeq=spaSeq,
                        spaDate=spaDate,
                        spa=spa,
                        reseller=reseller,
                        endUser=endUser,
                        partCd=partCd,
                        qty=qty,
                        listPrice=listPrice,
                        dc=dc,
                        extListPrice=extListPrice,
                        extDiscount=extDiscount,
                        extNetTotal=extNetTotal,
                        note=note,
                        state='R',
                        regUser=user,
                        regDate=datetime.now(),
                        modUser=None,
                        modDate=None)
        db.session.add(posSpa)

        posSpaExt = PosSpaExt(siteCd=siteCd,
                            spaCd=spaCd,
                            spaSeq=spaSeq,
                            reportType=reportType,
                            distributorId=distributorId,
                            distributorName=distributorName,
                            resellerVarId=resellerVarId,
                            resellerName=resellerName,
                            theatre=theatre,
                            region=region,
                            dealState=dealState,
                            partnerLevel=partnerLevel,
                            dateEffective=dateEffective,
                            dateExpiration=dateExpiration,
                            dateLastPublished=dateLastPublished,
                            revision=revision,
                            shipAndDebitId=spa,
                            endCustomerId=endCustomerId,
                            endUserVatId=endUserVatId,
                            endUserName=endUserName,
                            endCostomerAddress1=endCostomerAddress1,
                            endCostomerAddress2=endCostomerAddress2,
                            endCostomerAddress3=endCostomerAddress3,
                            endUserCity=endUserCity,
                            endUserProvince=endUserProvince,
                            endUserZipCode=endUserZipCode,
                            endUserCountry=endUserCountry,
                            jnprSalesRep=jnprSalesRep,
                            lastUpdatedBy=lastUpdatedBy,
                            sku=sku,
                            skuDescription=skuDescription,
                            fulfillmentType=fulfillmentType,
                            quantity=qty,
                            listPrice=listPrice,
                            discountRateDistributor=dc,
                            suggestedDiscountRateReseller=suggestedDiscountRateReseller,
                            suggestedDiscountRateEndUser=suggestedDiscountRateEndUser,
                            extendedListPrice=extListPrice,
                            extendedDiscount=extDiscount,
                            extendedNetTotal=extNetTotal,
                            productLine=productLine,
                            productFamily=productFamily,
                            lineNumber=lineNumber,
                            parentLineNumber=parentLineNumber,
                            configNumber=configNumber,
                            configInstance=configInstance,
                            serviceDuration=serviceDuration,
                            state='R',
                            regUser=user,
                            regDate=datetime.now(),
                            modUser=None,
                            modDate=None)
        db.session.add(posSpaExt)

        db.session.commit()
    
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'posSpa': posSpa.to_json()        
        })
    
    else:       

        data.spaDate = spaDate
        data.spa = spa
        data.reseller = reseller
        data.endUser = endUser
        data.partCd = partCd
        data.qty = qty
        data.listPrice = listPrice
        data.dc = dc
        data.extListPrice = extListPrice
        data.extDiscount = extDiscount
        data.extNetTotal = extNetTotal
        data.note = note
        data.state = 'R'
        data.modDate = datetime.now()
        data.modUser = user    
        db.session.add(data)

        dataExt = PosSpaExt.query.filter_by(siteCd = siteCd, spaCd = spaCd, spaSeq = spaSeq).first()
        if dataExt is not None:
            dataExt.reportType = reportType
            dataExt.distributorId = distributorId
            dataExt.distributorName = distributorName
            dataExt.resellerVarId = resellerVarId
            dataExt.resellerName = resellerName
            dataExt.theatre = theatre
            dataExt.region = region
            dataExt.dealState = dealState
            dataExt.partnerLevel = partnerLevel
            dataExt.dateEffective = dateEffective
            dataExt.dateExpiration = dateExpiration
            dataExt.dateLastPublished = dateLastPublished
            dataExt.revision = revision
            dataExt.shipAndDebitId = spa
            dataExt.endCustomerId = endCustomerId
            dataExt.endUserVatId = endUserVatId
            dataExt.endUserName = endUserName
            dataExt.endCostomerAddress1 = endCostomerAddress1
            dataExt.endCostomerAddress2 = endCostomerAddress2
            dataExt.endCostomerAddress3 = endCostomerAddress3
            dataExt.endUserCity = endUserCity
            dataExt.endUserProvince = endUserProvince
            dataExt.endUserZipCode = endUserZipCode
            dataExt.endUserCountry = endUserCountry
            dataExt.jnprSalesRep = jnprSalesRep
            dataExt.lastUpdatedBy = lastUpdatedBy
            dataExt.sku = sku
            dataExt.skuDescription = skuDescription
            dataExt.fulfillmentType = fulfillmentType
            dataExt.quantity = qty
            dataExt.listPrice = listPrice
            dataExt.discountRateDistributor = dc
            dataExt.suggestedDiscountRateReseller = suggestedDiscountRateReseller
            dataExt.suggestedDiscountRateEndUser = suggestedDiscountRateEndUser
            dataExt.extendedListPrice = extListPrice
            dataExt.extendedDiscount = extDiscount
            dataExt.extendedNetTotal = extNetTotal
            dataExt.productLine = productLine
            dataExt.productFamily = productFamily
            dataExt.lineNumber = lineNumber
            dataExt.parentLineNumber = parentLineNumber
            dataExt.configNumber = configNumber
            dataExt.configInstance = configInstance
            dataExt.serviceDuration = serviceDuration
            dataExt.state = 'R'
            dataExt.modUser = datetime.now()
            dataExt.modUser = user
            db.session.add(dataExt)

        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'posSpa': data.to_json()        
        })

@main.route('/api/updPosSpa', methods=['POST'])
def update_pos_spa():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    spaCd = json_data.get('spaCd')
    spaSeq = json_data.get('spaSeq')
    spaDate = json_data.get('spaDate')    
    spa = json_data.get('spa')
    reseller = json_data.get('reseller')
    endUser = json_data.get('endUser')
    partCd = json_data.get('partCd')
    qty = json_data.get('qty')
    listPrice = json_data.get('listPrice')
    dc = json_data.get('dc')
    extListPrice = json_data.get('extListPrice')
    extDiscount = json_data.get('extDiscount')    
    extNetTotal = json_data.get('extNetTotal')
    note = json_data.get('note')
    user = json_data.get('user')
    state = json_data.get('state')

    reportType = json_data.get('reportType')
    distributorId = json_data.get('distributorId')
    distributorName = json_data.get('distributorName')
    resellerVarId = json_data.get('resellerVarId')
    resellerName = json_data.get('resellerName')
    theatre = json_data.get('theatre')
    region = json_data.get('region')
    dealState = json_data.get('dealState')
    partnerLevel = json_data.get('partnerLevel')
    dateEffective = json_data.get('dateEffective')
    dateExpiration = json_data.get('dateExpiration')
    dateLastPublished = json_data.get('dateLastPublished')
    revision = json_data.get('revision')
    # shipAndDebitId = json_data.get('shipAndDebitId')
    endCustomerId = json_data.get('endCustomerId')
    endUserVatId = json_data.get('endUserVatId')
    endUserName = json_data.get('endUserName')
    endCostomerAddress1 = json_data.get('endCostomerAddress1')
    endCostomerAddress2 = json_data.get('endCostomerAddress2')
    endCostomerAddress3 = json_data.get('endCostomerAddress3')
    endUserCity = json_data.get('endUserCity')
    endUserProvince = json_data.get('endUserProvince')
    endUserZipCode = json_data.get('endUserZipCode')
    endUserCountry = json_data.get('endUserCountry')
    jnprSalesRep = json_data.get('jnprSalesRep')
    lastUpdatedBy = json_data.get('lastUpdatedBy')
    sku = json_data.get('sku')
    skuDescription = json_data.get('skuDescription')
    fulfillmentType = json_data.get('fulfillmentType')
    # quantity = json_data.get('quantity')
    # listPrice = json_data.get('listPrice')
    # discountRateDistributor = json_data.get('discountRateDistributor')
    suggestedDiscountRateReseller = json_data.get('suggestedDiscountRateReseller')
    suggestedDiscountRateEndUser = json_data.get('suggestedDiscountRateEndUser')
    # extendedListPrice = json_data.get('extendedListPrice')
    # extendedDiscount = json_data.get('extendedDiscount')
    # extendedNetTotal = json_data.get('extendedNetTotal')
    productLine = json_data.get('productLine')
    productFamily = json_data.get('productFamily')
    lineNumber = json_data.get('lineNumber')
    parentLineNumber = json_data.get('parentLineNumber')
    configNumber = json_data.get('configNumber')
    configInstance = json_data.get('configInstance')
    serviceDuration = json_data.get('serviceDuration')

    # check pos_spa
    data = PosSpa.query.filter_by(siteCd = siteCd, spaCd = spaCd, spaSeq = spaSeq).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    dataExt = PosSpaExt.query.filter_by(siteCd = siteCd, spaCd = spaCd, spaSeq = spaSeq).first()
    if dataExt is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    if state != 'D':        
        data.spaDate = spaDate
        data.spa = spa
        data.reseller = reseller
        data.endUser = endUser
        data.partCd = partCd
        data.qty = qty
        data.listPrice = listPrice
        data.dc = dc
        data.extListPrice = extListPrice
        data.extDiscount = extDiscount
        data.extNetTotal = extNetTotal
        data.note = note

        dataExt.reportType = reportType
        dataExt.distributorId = distributorId
        dataExt.distributorName = distributorName
        dataExt.resellerVarId = resellerVarId
        dataExt.resellerName = resellerName
        dataExt.theatre = theatre
        dataExt.region = region
        dataExt.dealState = dealState
        dataExt.partnerLevel = partnerLevel
        dataExt.dateEffective = dateEffective
        dataExt.dateExpiration = dateExpiration
        dataExt.dateLastPublished = dateLastPublished
        dataExt.revision = revision
        dataExt.shipAndDebitId = spa
        dataExt.endCustomerId = endCustomerId
        dataExt.endUserVatId = endUserVatId
        dataExt.endUserName = endUserName
        dataExt.endCostomerAddress1 = endCostomerAddress1
        dataExt.endCostomerAddress2 = endCostomerAddress2
        dataExt.endCostomerAddress3 = endCostomerAddress3
        dataExt.endUserCity = endUserCity
        dataExt.endUserProvince = endUserProvince
        dataExt.endUserZipCode = endUserZipCode
        dataExt.endUserCountry = endUserCountry
        dataExt.jnprSalesRep = jnprSalesRep
        dataExt.lastUpdatedBy = lastUpdatedBy
        dataExt.sku = sku
        dataExt.skuDescription = skuDescription
        dataExt.fulfillmentType = fulfillmentType
        dataExt.quantity = qty
        dataExt.listPrice = listPrice
        dataExt.discountRateDistributor = dc
        dataExt.suggestedDiscountRateReseller = suggestedDiscountRateReseller
        dataExt.suggestedDiscountRateEndUser = suggestedDiscountRateEndUser
        dataExt.extendedListPrice = extListPrice
        dataExt.extendedDiscount = extDiscount
        dataExt.extendedNetTotal = extNetTotal
        dataExt.productLine = productLine
        dataExt.productFamily = productFamily
        dataExt.lineNumber = lineNumber
        dataExt.parentLineNumber = parentLineNumber
        dataExt.configNumber = configNumber
        dataExt.configInstance = configInstance
        dataExt.serviceDuration = serviceDuration       

    else:        
        data.state = state
        dataExt.state = state

    data.modDate = datetime.now()
    data.modUser = user
    dataExt.modUser = datetime.now()
    dataExt.modUser = user

    db.session.add(data)
    db.session.add(dataExt)

    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'posSpa': data.to_json()
    })