# -- coding: utf-8 --

import os
import simplejson
from bson import json_util

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

# def date_handler(obj):
#     return obj.isoformat() if hasattr(obj, 'isoformat') else obj        

@main.route('/api/selStkStock', methods=['POST'])
def select_stk_stock():
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
    whCd = json_data.get('whCd')
    stkType = json_data.get('stkType')
    withZero = json_data.get('withZero')
    posState = json_data.get('posState')
    baseDate = json_data.get('baseDate')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT t.*, fn_get_codename('P0001', t.posState1) AS posState1Nm \
           FROM ( \
                SELECT '0' as chk, a.siteCd, a.poCd, b.poNo, \
			            b.poType1, \
                        fn_get_codename('P0003', b.poType1) AS poType1Nm, \
					    b.poType2, \
                        fn_get_codename('P0004', b.poType2) AS poType2Nm, \
					    b.poType3, \
                        fn_get_codename('P0005', b.poType3) AS poType3Nm, \
						a.partCd, d.partNm, b.poQty, \
						b.poState, \
                        fn_get_codename('P0002', b.poState) AS poStateNm, \
                        STR_TO_DATE(b.poDate, '%Y%m%d') AS poDate, \
						a.inCd, a.inSeq, a.inNo, \
                        STR_TO_DATE(a.inDate, '%Y%m%d') AS inDate, \
						a.lotNo, c.sn, \
						a.inKind, \
                        fn_get_codename('W0001', a.inKind) AS inKindNm, \
						a.purcYn, \
						a.inType, \
                        fn_get_codename('W0002', a.inType) AS inTypeNm, \
						a.inQty, \
						d.partUnit AS inUnit, \
                        fn_get_codename('S0005', d.partUnit) AS inUnitNm, \
						IFNULL(a.inAmt, 0.00) inAmt, \
						a.currency, \
                        fn_get_codename('S0006', a.currency) AS currencyNm, \
						a.cmLoc, \
						c.whCd, e.whNm, \
                        c.loc, \
                        fn_get_codename('C0008', c.loc) AS locNm, \
                        a.bl, a.invoice, \
                        a.inWarr, \
                        fn_get_codename('W0003', a.inWarr) AS inWarrNm, \
                        a.partRank AS partRank, \
                        fn_get_codename('W0004', a.partRank) AS partRankNm, \
                        IFNULL(b.unitAmt, 0.00) unitAmt, \
						IFNULL(c.curQty, 0.00) curQty, \
						IFNULL(c.docQty, 0.00) docQty, \
						f.outCd, f.outSeq, f.outNo, \
						STR_TO_DATE(f.outDate, '%Y%m%d') AS outDate, \
						f.outKind, \
                        fn_get_codename('W0011', f.outKind) AS outKindNm, \
						f.sellYn, \
						f.outType, \
                        fn_get_codename('W0012', f.outType) AS outTypeNm, \
						f.requester, f.sender, f.outQty, f.outUnit, f.arrAddr, f.recipient, f.recipientTel, \
						f.transporter, f.transporterTel, f.receiptYn, f.sellCd, f.sellSeq, f.sellNo, \
                        STR_TO_DATE(f.sellDate, '%Y%m%d') AS sellDate, \
                        f.sellState, '' AS sellStateNm, \
                        f.psvType, \
                        fn_get_codename('P0004', f.psvType) AS psvTypeNm, \
                        f.serviceYn, \
                        case when j.prjCd is null then f.project else j.prjNm end AS project, \
                        f.manager, \
						f.unitAmt AS sellUnitAmt, f.taxAmt AS sellTaxAmt, f.sellAmt, \
						g.posState, \
                        fn_get_codename('P0001', g.posState) AS posStateNm, \
						g.spa, \
						STR_TO_DATE(g.posDate, '%Y%m%d') AS posDate, \
						g.posQty, g.dc, g.reseller, g.endUser, g.netPos, g.am, g.partner, g.jda, g.vertical, g.year, g.quater, g.week, \
						g.cmCd, \
                        STR_TO_DATE(g.cmDate, '%Y%m%d') AS cmDate, \
                        g.cmNo, g.rebAmt, g.remAmt, g.excRate, g.rebWonAmt, g.costWonAmt, \
                        f.custCd AS outCustCd, h1.custNm AS outCustNm, \
                        h2.custNm AS resellerNm, \
                        h3.custNm AS endUserNm, \
                        a.stkType, \
                        fn_get_codename('W0023', a.stkType) AS stkTypeNm, \
                        c.posState AS posState1, \
                        i.roCd, i.roSeq, \
                        STR_TO_DATE(i.resvDate, '%Y%m%d') AS resvDate, \
                        i.resvUser, \
                        i.note AS resvNote, \
                        a.note AS inNote, \
                        IFNULL(a.inAmt, 0) - IFNULL(g.rebWonAmt, 0) AS goodsAmt, \
                        f.prjCd, \
                        f.note AS outNote, \
                        f.note2 AS outNote2, \
                        f.note3 AS outNote3 \
				FROM stk_in a \
				LEFT OUTER JOIN pur_order b \
				ON a.siteCd = b.siteCd \
				AND a.poCd = b.poCd \
				AND b.state = 'R' \
				INNER JOIN stk_lot c \
				ON a.siteCd = c.siteCd \
				AND a.lotNo = c.lotNo \
				AND c.state = 'R' \
				LEFT OUTER JOIN mst_part d \
				ON a.siteCd = d.siteCd \
				AND a.partCd = d.partCd \
				LEFT OUTER JOIN mst_wh e \
				ON c.siteCd = e.siteCd \
				AND c.whCd = e.whCd \
				LEFT OUTER JOIN ( \
					SELECT f1.*, f2.sellCd, f2.sellSeq, f2.sellNo, f2.sellDate, f2.sellState, f2.psvType, f2.serviceYn, \
							 f2.prjCd, f2.project, f2.manager, f2.unitAmt, f2.taxAmt, f2.sellAmt, f2.currency \
					FROM stk_out f1 \
					LEFT OUTER JOIN stk_sell f2 \
					ON f1.siteCd = f2.siteCd \
					AND f1.outCd = f2.outCd \
                    AND f1.outSeq = f2.outSeq \
					AND f2.state = 'R' "
    if baseDate is not None:
        sql += "    WHERE f1.outDate <= '" + baseDate + "' \
                    AND f2.sellDate <= '" + baseDate + "' "
    
    sql += " ) f \
				ON c.siteCd = f.siteCd \
				AND c.lotNo = f.lotNo \
				AND f.state = 'R' \
				LEFT OUTER JOIN ( \
					SELECT g1.*, g2.cmCd, g2.cmState, g2.cmDate, g2.cmNo, g2.rebAmt, g2.remAmt, g2.excRate, g2.rebWonAmt, g2.costWonAmt \
					FROM pos_pos g1 \
					LEFT OUTER JOIN pos_cm g2 \
					ON g1.siteCd = g2.siteCd \
					AND g1.posCd = g2.posCd \
					AND g2.state = 'R' "
    if baseDate is not None:
        sql += "    WHERE g1.posDate <= '" + baseDate + "' \
                    AND g2.cmDate <= '" + baseDate + "' "

    sql += " ) g \
				ON c.siteCd = g.siteCd \
				AND c.lotNo = g.lotNo \
				AND b.siteCd = g.siteCd \
				AND b.poCd = g.poCd \
                AND g.state = 'R' \
                LEFT OUTER JOIN mst_cust h1 \
                ON f.siteCd = h1.siteCd \
                AND f.custCd = h1.custCd \
                LEFT OUTER JOIN mst_cust h2 \
                ON g.siteCd = h2.siteCd \
                AND g.reseller = h2.custCd \
                LEFT OUTER JOIN mst_cust h3 \
                ON g.siteCd = h3.siteCd \
                AND g.endUser = h3.custCd \
                LEFT OUTER JOIN stk_reserve_out i \
                ON c.siteCd = i.siteCd \
                AND c.lotNo = i.lotNo \
                AND i.state = 'R' "
    if baseDate is not None:
        sql += " AND i.resvDate <= '" + baseDate + "' "
    sql += " LEFT OUTER JOIN mst_project j \
             ON f.siteCd = j.siteCd \
             AND f.prjCd = j.prjCd \
             WHERE a.siteCd = '" + siteCd + "' "
    if baseDate is not None:
        sql += " AND a.inDate <= '" + baseDate + "' "
    else:
        sql += " AND a.inDate BETWEEN '" + fDate + "' AND '" + tDate + "' "
    
    sql += " AND a.state = 'R' "

    if whCd is not None:
        sql += " AND c.whCd = '" + whCd + "'"
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
        sql += " AND a.stkType = '" + stkType + "' "
    if withZero == 'N':
        if whCd is not None:
            sql += " AND c.docQty > 0 "
        else:
            sql += " AND c.curQty > 0 "
    sql += " ) t \
        WHERE 1 = 1 "
    if loc is not None:
        sql += " AND ( loc like '%" + loc + \
            "%' or locNm like '%" + loc + "%' ) "
    if posState is not None:
        sql += " AND posState1 = '" + posState + "' "
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
        dic['unitAmt'] = tr[44]
        dic['curQty'] = tr[45]
        dic['docQty'] = tr[46]
        dic['outCd'] = tr[47]
        dic['outSeq'] = tr[48]
        dic['outNo'] = tr[49]
        dic['outDate'] = tr[50]
        dic['outKind'] = tr[51]
        dic['outKindNm'] = tr[52]
        dic['sellYn'] = tr[53]
        dic['outType'] = tr[54]
        dic['outTypeNm'] = tr[55]
        dic['requester'] = tr[56]
        dic['sender'] = tr[57]
        dic['outQty'] = tr[58]
        dic['outUnit'] = tr[59]
        dic['arrAddr'] = tr[60]
        dic['recipient'] = tr[61]
        dic['recipientTel'] = tr[62]
        dic['transporter'] = tr[63]
        dic['transporterTel'] = tr[64]
        dic['receiptYn'] = tr[65]
        dic['sellCd'] = tr[66]
        dic['sellSeq'] = tr[67]
        dic['sellNo'] = tr[68]
        dic['sellDate'] = tr[69]
        dic['sellState'] = tr[70]
        dic['sellStateNm'] = tr[71]
        dic['psvType'] = tr[72]
        dic['psvTypeNm'] = tr[73]
        dic['serviceYn'] = tr[74]
        dic['project'] = tr[75]
        dic['manager'] = tr[76]
        dic['sellUnitAmt'] = tr[77]
        dic['sellTaxAmt'] = tr[78]
        dic['sellAmt'] = tr[79]
        dic['posState'] = tr[80]
        dic['posStateNm'] = tr[81]
        dic['spa'] = tr[82]
        dic['posDate'] = tr[83]
        dic['posQty'] = tr[84]
        dic['dc'] = tr[85]
        dic['reseller'] = tr[86]
        dic['endUser'] = tr[87]
        dic['netPos'] = tr[88]
        dic['am'] = tr[89]
        dic['partner'] = tr[90]
        dic['jda'] = tr[91]
        dic['vertical'] = tr[92]
        dic['year'] = tr[93]
        dic['quater'] = tr[94]
        dic['week'] = tr[95]
        dic['cmCd'] = tr[96]
        dic['cmDate'] = tr[97]
        dic['cmNo'] = tr[98]
        dic['rebAmt'] = tr[99]
        dic['remAmt'] = tr[100]
        dic['excRate'] = tr[101]
        dic['rebWonAmt'] = tr[102]
        dic['costWonAmt'] = tr[103]
        dic['outCustCd'] = tr[104]
        dic['outCustNm'] = tr[105]
        dic['resellerNm'] = tr[106]
        dic['endUserNm'] = tr[107]
        dic['stkType'] = tr[108]
        dic['stkTypeNm'] = tr[109]
        dic['posState1'] = tr[110]
        dic['roCd'] = tr[111]
        dic['roSeq'] = tr[112]
        dic['resvDate'] = tr[113]
        dic['resvUser'] = tr[114]
        dic['resvNote'] = tr[115]
        dic['inNote'] = tr[116]
        dic['goodsAmt'] = tr[117]
        dic['prjCd'] = tr[118]
        dic['outNote'] = tr[119]
        dic['outNote2'] = tr[120]
        dic['outNote3'] = tr[121]
        dic['posState1Nm'] = tr[122]

        data[index] = dic

    # return jsonify({'stock': data})
    return simplejson.dumps({'stock': data}, default=jsonhandler.date_handler)


@main.route('/api/updStkStock', methods=['POST'])
def update_stk_stock():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    lotNo = json_data.get('lotNo')
    loc = json_data.get('loc')
    user = json_data.get('user')

    data = StkLot.query.filter_by(
        siteCd=siteCd, lotNo=lotNo, state='R').first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8603,
                'msg': '재고정보가 존재하지 않습니다.'
            }
        })

    data.loc = loc
    data.modUser = user
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        }
    })


@main.route('/api/insStkStockOutgoing', methods=['POST'])
def insert_stk_stock_outgoing():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    outCd = json_data.get('outCd')
    outDate = json_data.get('outDate')
    outNo = json_data.get('outNo')
    lotNo = json_data.get('lotNo')
    outKind = json_data.get('outKind')
    sellYn = json_data.get('sellYn')
    outType = json_data.get('outType')
    requester = json_data.get('requester')
    sender = json_data.get('sender')
    poCd = json_data.get('poCd')
    outQty = json_data.get('outQty')
    outUnit = json_data.get('outUnit')
    whCd = json_data.get('whCd')
    custCd = json_data.get('custCd')
    arrAddr = json_data.get('arrAddr')
    recipient = json_data.get('recipient')
    recipientTel = json_data.get('recipientTel')
    transporter = json_data.get('transporter')
    transporterTel = json_data.get('transporterTel')
    receiptYn = json_data.get('receiptYn')
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    user = json_data.get('user')

    # check stk_lot
    lot = StkLot.query.filter_by(siteCd=siteCd, lotNo=lotNo, state='R').first()
    if lot is None:
        return jsonify({
            'result': {
                'code': 8605,
                'msg': '재고가 존재하지 않습니다.'
            }
        })
    else:
        if lot.curQty <= 0:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고가 존재하지 않습니다.'
                }
            })

    # check stk_out
    if not outCd:
        findKey_outCd = 'OT' + outDate[-6:]
        seq_outCd = 1
        sel_outCd = StkOut.query.filter(StkOut.siteCd == siteCd, StkOut.outCd.like(
            findKey_outCd + '%')).order_by(StkOut.outCd.desc()).first()
        if sel_outCd is not None:
            seq_outCd = int(sel_outCd.outCd[-6:]) + 1
        outCd = findKey_outCd + \
            (6 - len(str(seq_outCd))) * '0' + str(seq_outCd)

    outSeq = 1
    sel_outSeq = StkOut.query.filter(
        StkOut.siteCd == siteCd, StkOut.outCd == outCd).order_by(StkOut.outSeq.desc()).first()
    if sel_outSeq is not None:
        outSeq = int(sel_outSeq.outSeq) + 1

    # stk_out insert
    stkOut = StkOut(siteCd=siteCd,
                    outCd=outCd,
                    outSeq=outSeq,
                    outNo=outNo,
                    outDate=outDate,
                    lotNo=lotNo,
                    sn=lot.sn,
                    outKind=outKind,
                    sellYn=sellYn,
                    outType=outType,
                    requester=requester,
                    sender=sender,
                    outQty=outQty,
                    outUnit=outUnit,
                    whCd=whCd,
                    poCd=poCd,
                    custCd=custCd,
                    arrAddr=arrAddr,
                    recipient=recipient,
                    recipientTel=recipientTel,
                    transporter=transporter,
                    transporterTel=transporterTel,
                    receiptYn=receiptYn,
                    note=note,
                    note2=note2,
                    note3=note3,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)

    # stk_lot update
    lot.curQty = int(lot.curQty) - int(outQty)
    # lot.docQty = int(lot.docQty) - int(outQty)
    if whCd == 'WH0002' or outKind == 'E':
        lot.docQty = int(lot.docQty) - int(outQty)

    lot.modUser = user
    lot.modDate = datetime.now()

    db.session.add(stkOut)
    db.session.add(lot)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOut': stkOut.to_json()
    })


@main.route('/api/insStkStockWhOutgoing', methods=['POST'])
def insert_stk_stockwh_outgoing():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    outCd = json_data.get('outCd')
    outDate = json_data.get('outDate')
    outNo = json_data.get('outNo')
    lotNo = json_data.get('lotNo')
    outKind = json_data.get('outKind')
    sellYn = json_data.get('sellYn')
    outType = json_data.get('outType')
    requester = json_data.get('requester')
    sender = json_data.get('sender')
    poCd = json_data.get('poCd')
    outQty = json_data.get('outQty')
    outUnit = json_data.get('outUnit')
    whCd = json_data.get('whCd')
    custCd = json_data.get('custCd')
    arrAddr = json_data.get('arrAddr')
    recipient = json_data.get('recipient')
    recipientTel = json_data.get('recipientTel')
    transporter = json_data.get('transporter')
    transporterTel = json_data.get('transporterTel')
    receiptYn = json_data.get('receiptYn')
    note = json_data.get('note')
    user = json_data.get('user')

    # check stk_lot
    lot = StkLot.query.filter_by(siteCd=siteCd, lotNo=lotNo, state='R').first()
    if lot is None:
        return jsonify({
            'result': {
                'code': 8605,
                'msg': '재고가 존재하지 않습니다.'
            }
        })
    else:
        if lot.curQty <= 0:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고가 존재하지 않습니다.'
                }
            })

    # check stk_out
    if not outCd:
        findKey_outCd = 'OT' + outDate[-6:]
        seq_outCd = 1
        sel_outCd = StkOut.query.filter(StkOut.siteCd == siteCd, StkOut.outCd.like(
            findKey_outCd + '%')).order_by(StkOut.outCd.desc()).first()
        if sel_outCd is not None:
            seq_outCd = int(sel_outCd.outCd[-6:]) + 1
        outCd = findKey_outCd + \
            (6 - len(str(seq_outCd))) * '0' + str(seq_outCd)

    outSeq = 1
    sel_outSeq = StkOut.query.filter(
        StkOut.siteCd == siteCd, StkOut.outCd == outCd).order_by(StkOut.outSeq.desc()).first()
    if sel_outSeq is not None:
        outSeq = int(sel_outSeq.outSeq) + 1

    # stk_out insert
    stkOut = StkOut(siteCd=siteCd,
                    outCd=outCd,
                    outSeq=outSeq,
                    outNo=outNo,
                    outDate=outDate,
                    lotNo=lotNo,
                    sn=lot.sn,
                    outKind=outKind,
                    sellYn=sellYn,
                    outType=outType,
                    requester=requester,
                    sender=sender,
                    outQty=outQty,
                    outUnit=outUnit,
                    whCd=whCd,
                    poCd=poCd,
                    custCd=custCd,
                    arrAddr=arrAddr,
                    recipient=recipient,
                    recipientTel=recipientTel,
                    transporter=transporter,
                    transporterTel=transporterTel,
                    receiptYn=receiptYn,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)

    # stk_lot update
    lot.curQty = int(lot.curQty) - int(outQty)
    # lot.docQty = int(lot.docQty) - int(outQty)
    lot.modUser = user
    lot.modDate = datetime.now()

    db.session.add(stkOut)
    db.session.add(lot)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOut': stkOut.to_json()
    })


@main.route('/api/selStkOutgoing', methods=['POST'])
def select_stk_outgoing():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    whCd = json_data.get('whCd')
    outKind = json_data.get('outKind')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    poNo = json_data.get('poNo')
    bl = json_data.get('bl')
    sn = json_data.get('sn')
    loc = json_data.get('loc')
    outNo = json_data.get('outNo')
    stkType = json_data.get('stkType')
    sellYn = json_data.get('sellYn')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT t.*, fn_get_codename('P0001', t.posState1) AS posState1Nm \
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
						a.lotNo, c.sn, \
						a.inKind, fn_get_codename('W0001', a.inKind) AS inKindNm, \
						a.purcYn, \
						a.inType, fn_get_codename('W0002', a.inType) AS inTypeNm, \
						a.inQty, \
						d.partUnit AS inUnit, fn_get_codename('S0005', d.partUnit) AS inUnitNm, \
						IFNULL(a.inAmt, 0.00) inAmt, \
						a.currency, fn_get_codename('S0006', a.currency) AS currencyNm, \
						a.cmLoc, \
						c.whCd, e.whNm, \
                        c.loc, fn_get_codename('C0008', c.loc) AS locNm, \
                        a.bl, a.invoice, \
                        a.inWarr, fn_get_codename('W0003', a.inWarr) AS inWarrNm, \
                        a.partRank AS partRank, fn_get_codename('W0004', a.partRank) AS partRankNm, \
                        IFNULL(b.unitAmt, 0.00) unitAmt, \
						IFNULL(c.curQty, 0.00) curQty, \
						IFNULL(c.docQty, 0.00) docQty, \
						f.outCd, f.outSeq, f.outNo, \
						/*CASE WHEN f.outDate is null THEN '' ELSE CONCAT(LEFT(f.outDate, 4), '-', SUBSTRING(f.outDate, 5, 2), '-', RIGHT(f.outDate, 2)) END AS outDate,*/ \
                        STR_TO_DATE(f.outDate, '%Y%m%d') AS outDate, \
						f.outKind, fn_get_codename('W0011', f.outKind) AS outKindNm, \
						f.sellYn, \
						f.outType, fn_get_codename('W0012', f.outType) AS outTypeNm, \
						f.requester, f.sender, f.outQty, f.outUnit, f.arrAddr, f.recipient, f.recipientTel, \
						f.transporter, f.transporterTel, f.receiptYn, f.sellCd, f.sellSeq, f.sellNo, \
                        /*CASE WHEN f.sellDate is null THEN '' ELSE CONCAT(LEFT(f.sellDate, 4), '-', SUBSTRING(f.sellDate, 5, 2), '-', RIGHT(f.sellDate, 2)) END AS sellDate,*/ \
                        STR_TO_DATE(f.sellDate, '%Y%m%d') AS sellDate, \
                        f.sellState, fn_get_codename('W0021', f.sellState) AS sellStateNm, \
                        f.psvType, fn_get_codename('W0022', f.psvType) AS psvTypeNm, \
                        f.serviceYn, \
                        case when j.prjCd is null then f.project else j.prjNm end AS project, \
                        f.manager, \
						IFNULL(f.unitAmt, 0.00) AS sellUnitAmt, IFNULL(f.taxAmt, 0.00) AS sellTaxAmt, IFNULL(f.sellAmt, 0.00) AS sellAmt, \
						g.posState, fn_get_codename('P0001', g.posState) AS posStateNm, \
						g.spa, \
						/*CASE WHEN g.posDate is null THEN '' ELSE CONCAT(LEFT(g.posDate, 4), '-', SUBSTRING(g.posDate, 5, 2), '-', RIGHT(g.posDate, 2)) END AS posDate,*/ \
                        STR_TO_DATE(g.posDate, '%Y%m%d') AS posDate, \
						g.posQty, g.dc, g.reseller, g.endUser, g.netPos, g.am, g.partner, g.jda, g.vertical, g.year, g.quater, g.week, \
						g.cmCd, \
                        /*CASE WHEN g.cmDate is null THEN '' ELSE CONCAT(LEFT(g.cmDate, 4), '-', SUBSTRING(g.cmDate, 5, 2), '-', RIGHT(g.cmDate, 2)) END AS cmDate,*/ \
                        STR_TO_DATE(g.cmDate, '%Y%m%d') AS cmDate, \
                        g.cmNo, g.rebAmt, g.remAmt, g.excRate, \
                        IFNULL(g.rebWonAmt, 0) AS rebWonAmt, \
                        g.costWonAmt, \
                        f.custCd AS outCustCd, h1.custNm AS outCustNm, \
                        h2.custNm AS resellerNm, \
                        h3.custNm AS endUserNm, \
                        f.sellCustCd, h4.custNm AS sellCustNm, \
                        a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm, \
                        c.posState AS posState1, \
                        a.note AS inNote, \
                        IFNULL(a.inAmt, 0) - IFNULL(g.rebWonAmt, 0) AS goodsAmt, \
                        f.outEtcCd, f.outEtcSeq, f.outEtcNo, \
                        /*CASE WHEN f.outEtcDate is null THEN '' ELSE CONCAT(LEFT(f.outEtcDate, 4), '-', SUBSTRING(f.outEtcDate, 5, 2), '-', RIGHT(f.outEtcDate, 2)) END AS outEtcDate,*/ \
                        STR_TO_DATE(f.outEtcDate, '%Y%m%d') AS outEtcDate, \
                        f.outEtcRemark, f.outEtcNote, f.prjCd, f.note AS outNote, \
                        i.roCd, i.roSeq, \
                        /*CASE WHEN i.resvDate is null THEN '' ELSE CONCAT(LEFT(i.resvDate, 4), '-', SUBSTRING(i.resvDate, 5, 2), '-', RIGHT(i.resvDate, 2)) END AS resvDate,*/ \
                        STR_TO_DATE(i.resvDate, '%Y%m%d') AS resvDate, \
                        i.resvUser, \
                        i.note AS resvNote, \
                        f.note2 AS outNote2, \
                        f.note3 AS outNote3 \
				FROM stk_in a \
				LEFT OUTER JOIN pur_order b \
				ON a.siteCd = b.siteCd \
				AND a.poCd = b.poCd \
				AND b.state = 'R' \
				INNER JOIN stk_lot c \
				ON a.siteCd = c.siteCd \
				AND a.lotNo = c.lotNo \
				AND c.state = 'R' \
				LEFT OUTER JOIN mst_part d \
				ON a.siteCd = d.siteCd \
				AND a.partCd = d.partCd \
				LEFT OUTER JOIN mst_wh e \
				ON c.siteCd = e.siteCd \
				AND c.whCd = e.whCd \
				INNER JOIN ( \
					SELECT f1.*, f2.sellCd, f2.sellSeq, f2.sellNo, f2.sellDate, f2.sellState, f2.psvType, f2.serviceYn, \
							 f2.prjCd, f2.project, f2.manager, f2.unitAmt, f2.taxAmt, f2.sellAmt, f2.currency, f2.custCd AS sellCustCd, \
                             f3.outEtcCd, f3.outEtcSeq, f3.outEtcNo, f3.outEtcDate, f3.remark as outEtcRemark, f3.note as outEtcNote \
					FROM stk_out f1 \
					LEFT OUTER JOIN stk_sell f2 \
					ON f1.siteCd = f2.siteCd \
					AND f1.outCd = f2.outCd \
                    AND f1.outSeq = f2.outSeq \
					AND f2.state = 'R' \
                    LEFT OUTER JOIN stk_out_etc f3 \
                    ON f1.siteCd = f3.siteCd \
                    AND f1.outCd = f3.outCd \
                    AND f1.outSeq = f3.outSeq \
                    AND f3.state = 'R' \
				) f \
				ON c.siteCd = f.siteCd \
				AND c.lotNo = f.lotNo \
				AND f.state = 'R' \
				LEFT OUTER JOIN ( \
					SELECT g1.*, g2.cmCd, g2.cmState, g2.cmDate, g2.cmNo, g2.rebAmt, g2.remAmt, g2.excRate, g2.rebWonAmt, g2.costWonAmt \
					FROM pos_pos g1 \
					LEFT OUTER JOIN pos_cm g2 \
					ON g1.siteCd = g2.siteCd \
					AND g1.posCd = g2.posCd \
					AND g2.state = 'R' \
				) g \
				ON c.siteCd = g.siteCd \
				AND c.lotNo = g.lotNo \
				AND b.siteCd = g.siteCd \
				AND b.poCd = g.poCd \
                AND g.state = 'R' \
                LEFT OUTER JOIN mst_cust h1 \
                ON f.siteCd = h1.siteCd \
                AND f.custCd = h1.custCd \
                LEFT OUTER JOIN mst_cust h2 \
                ON g.siteCd = h2.siteCd \
                AND g.reseller = h2.custCd \
                LEFT OUTER JOIN mst_cust h3 \
                ON g.siteCd = h3.siteCd \
                AND g.endUser = h3.custCd \
                LEFT OUTER JOIN mst_cust h4 \
                ON f.siteCd = h4.siteCd \
                AND f.sellCustCd = h4.custCd \
                LEFT OUTER JOIN mst_project j \
                ON f.siteCd = j.siteCd \
                AND f.prjCd = j.prjCd \
                LEFT OUTER JOIN stk_reserve_out i \
                ON c.siteCd = i.siteCd \
                AND c.lotNo = i.lotNo \
                AND i.state = 'R' \
				WHERE a.siteCd = '" + siteCd + "' \
				AND a.state = 'R' "

    if outKind == 'E':
        sql += " AND f.outEtcDate BETWEEN '" + fDate + "' AND '" + tDate + "'"
    else:
        sql += " AND f.outDate BETWEEN '" + fDate + "' AND '" + tDate + "'"
    if whCd is not None:
        sql += " AND c.whCd = '" + whCd + "'"
    if outKind is not None:
        sql += " AND f.outKind = '" + outKind + "'"
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
    if sellYn is not None:
        sql += " AND f.sellYn = '" + sellYn + "'"
    if outNo is not None:
        sql += " AND f.outNo like '%" + outNo + "%' "
    sql += " ) t"
    if loc is not None:
        sql += " WHERE ( loc like '%" + loc + \
            "%' or locNm like '%" + loc + "%' ) "
    if outKind == 'E':
        sql += " order by outEtcCd desc, outEtcSeq desc"
    else:
        sql += " order by outCd desc, outSeq desc"

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
        dic['unitAmt'] = tr[44]
        dic['curQty'] = tr[45]
        dic['docQty'] = tr[46]
        dic['outCd'] = tr[47]
        dic['outSeq'] = tr[48]
        dic['outNo'] = tr[49]
        dic['outDate'] = tr[50]
        dic['outKind'] = tr[51]
        dic['outKindNm'] = tr[52]
        dic['sellYn'] = tr[53]
        dic['outType'] = tr[54]
        dic['outTypeNm'] = tr[55]
        dic['requester'] = tr[56]
        dic['sender'] = tr[57]
        dic['outQty'] = tr[58]
        dic['outUnit'] = tr[59]
        dic['arrAddr'] = tr[60]
        dic['recipient'] = tr[61]
        dic['recipientTel'] = tr[62]
        dic['transporter'] = tr[63]
        dic['transporterTel'] = tr[64]
        dic['receiptYn'] = tr[65]
        dic['sellCd'] = tr[66]
        dic['sellSeq'] = tr[67]
        dic['sellNo'] = tr[68]
        dic['sellDate'] = tr[69]
        dic['sellState'] = tr[70]
        dic['sellStateNm'] = tr[71]
        dic['psvType'] = tr[72]
        dic['psvTypeNm'] = tr[73]
        dic['serviceYn'] = tr[74]
        dic['project'] = tr[75]
        dic['manager'] = tr[76]
        dic['sellUnitAmt'] = tr[77]
        dic['sellTaxAmt'] = tr[78]
        dic['sellAmt'] = tr[79]
        dic['posState'] = tr[80]
        dic['posStateNm'] = tr[81]
        dic['spa'] = tr[82]
        dic['posDate'] = tr[83]
        dic['posQty'] = tr[84]
        dic['dc'] = tr[85]
        dic['reseller'] = tr[86]
        dic['endUser'] = tr[87]
        dic['netPos'] = tr[88]
        dic['am'] = tr[89]
        dic['partner'] = tr[90]
        dic['jda'] = tr[91]
        dic['vertical'] = tr[92]
        dic['year'] = tr[93]
        dic['quater'] = tr[94]
        dic['week'] = tr[95]
        dic['cmCd'] = tr[96]
        dic['cmDate'] = tr[97]
        dic['cmNo'] = tr[98]
        dic['rebAmt'] = tr[99]
        dic['remAmt'] = tr[100]
        dic['excRate'] = tr[101]
        dic['rebWonAmt'] = tr[102]
        dic['costWonAmt'] = tr[103]
        dic['outCustCd'] = tr[104]
        dic['outCustNm'] = tr[105]
        dic['resellerNm'] = tr[106]
        dic['endUserNm'] = tr[107]
        dic['sellCustCd'] = tr[108]
        dic['sellCustNm'] = tr[109]
        dic['stkType'] = tr[110]
        dic['stkTypeNm'] = tr[111]
        dic['posState1'] = tr[112]
        dic['inNote'] = tr[113]
        dic['goodsAmt'] = tr[114]
        dic['outEtcCd'] = tr[115]
        dic['outEtcSeq'] = tr[116]
        dic['outEtcNo'] = tr[117]
        dic['outEtcDate'] = tr[118]
        dic['outEtcRemark'] = tr[119]
        dic['outEtcNote'] = tr[120]
        dic['prjCd'] = tr[121]
        dic['outNote'] = tr[122]
        dic['roCd'] = tr[123]
        dic['roSeq'] = tr[124]
        dic['resvDate'] = tr[125]
        dic['resvUser'] = tr[126]
        dic['resvNote'] = tr[127]
        dic['outNote2'] = tr[128]
        dic['outNote3'] = tr[129]
        dic['posState1Nm'] = tr[130]

        data[index] = dic

    # return jsonify({'stock': data})
    return simplejson.dumps({'stock': data}, default=jsonhandler.date_handler)


@main.route('/api/updStkStockOutgoing', methods=['POST'])
def update_stk_stock_outgoing():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    outDate = json_data.get('outDate')
    outNo = json_data.get('outNo')
    outKind = json_data.get('outKind')
    sellYn = json_data.get('sellYn')
    outType = json_data.get('outType')
    requester = json_data.get('requester')
    sender = json_data.get('sender')
    custCd = json_data.get('custCd')
    arrAddr = json_data.get('arrAddr')
    recipient = json_data.get('recipient')
    recipientTel = json_data.get('recipientTel')
    transporter = json_data.get('transporter')
    transporterTel = json_data.get('transporterTel')
    receiptYn = json_data.get('receiptYn')
    note = json_data.get('note')
    note2 = json_data.get('note2')
    note3 = json_data.get('note3')
    user = json_data.get('user')
    state = json_data.get('state')

    data = StkOut.query.filter_by(
        siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
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

    sell = StkSell.query.filter_by(
        siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
    if sell is not None:
        return jsonify({
            'result': {
                'code': 8604,
                'msg': '매출내역이 존재하여 처리할수 없습니다.'
            }
        })

    if state == 'D':
        if data.whCd == 'WH0002' or data.outKind == 'E':
            lot.docQty = lot.docQty + data.outQty

        lot.curQty = lot.curQty + data.outQty
        lot.modUser = user
        lot.modDate = datetime.now()

        db.session.add(lot)
    else:
        data.outDate = outDate or data.outDate
        data.outNo = outNo or data.outNo
        data.outKind = outKind or data.outKind
        data.sellYn = sellYn or data.sellYn
        data.outType = outType or data.outType
        data.requester = requester or data.requester
        data.sender = sender or data.sender
        data.custCd = custCd or data.custCd
        data.arrAddr = arrAddr or data.arrAddr
        data.recipient = recipient or data.recipient
        data.recipientTel = recipientTel or data.recipientTel
        data.transporter = transporter or data.transporter
        data.transporterTel = transporterTel or data.transporterTel
        data.receiptYn = receiptYn or data.receiptYn
        data.note = note if note is not None else data.note
        data.note2 = note2 if note2 is not None else data.note2
        data.note3 = note3 if note3 is not None else data.note3

    data.modUser = user
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


@main.route('/api/insStkStockSell', methods=['POST'])
def insert_stk_sell():
    json_data = json.loads(request.data, strict=False)
    insType = json_data.get('insType')
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')
    sellDate = json_data.get('sellDate')
    sellNo = json_data.get('sellNo')
    sellState = json_data.get('sellState')
    psvType = json_data.get('psvType')
    serviceYn = json_data.get('serviceYn')
    poCd = json_data.get('poCd')
    custCd = json_data.get('custCd')
    prjCd = json_data.get('prjCd')
    manager = json_data.get('manager')
    unitAmt = json_data.get('unitAmt')
    taxAmt = json_data.get('taxAmt')
    sellAmt = json_data.get('sellAmt')
    currency = json_data.get('currency')
    tempServiceAmt = json_data.get('tempServiceAmt')
    tempExcRate = json_data.get('tempExcRate')
    tempWonAmt = json_data.get('tempWonAmt')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    note = json_data.get('note')
    user = json_data.get('user')

    if outCd:
        # check stk_out
        out = StkOut.query.filter_by(
            siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
        if out is None:
            return jsonify({
                'result': {
                    'code': 8606,
                    'msg': '출고정보가 존재하지 않습니다.'
                }
            })

        lot = StkLot.query.filter_by(
            siteCd=siteCd, lotNo=out.lotNo, state='R').first()
        if lot is None:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고정보가 존재하지 않습니다.'
                }
            })

    # check stk_sell
    if not sellCd:
        findKey_sellCd = 'SL' + sellDate[-6:]
        seq_sellCd = 1
        sel_sellCd = StkSell.query.filter(StkSell.siteCd == siteCd, StkSell.sellCd.like(
            findKey_sellCd + '%')).order_by(StkSell.sellCd.desc()).first()
        if sel_sellCd is not None:
            seq_sellCd = int(sel_sellCd.sellCd[-6:]) + 1
        sellCd = findKey_sellCd + \
            (6 - len(str(seq_sellCd))) * '0' + str(seq_sellCd)

    if insType == 'V':
        sellSeq = 1
    else:
        sellSeq = 0
    sel_sellSeq = StkSell.query.filter(
        StkSell.siteCd == siteCd, StkSell.sellCd == sellCd).order_by(StkSell.sellSeq.desc()).first()
    if sel_sellSeq is not None:
        sellSeq = int(sel_sellSeq.sellSeq) + 1

    # stk_sell insert
    stkSell = StkSell(siteCd=siteCd,
                      sellCd=sellCd,
                      sellSeq=sellSeq,
                      sellNo=sellNo,
                      sellDate=sellDate,
                      sellState=sellState,
                      psvType=psvType,
                      serviceYn=serviceYn,
                      poCd=poCd,
                      custCd=custCd,
                      prjCd=prjCd,
                      manager=manager,
                      unitAmt=unitAmt,
                      taxAmt=taxAmt,
                      sellAmt=sellAmt,
                      currency=currency,
                      tempServiceAmt=tempServiceAmt,
                      tempExcRate=tempExcRate,
                      tempWonAmt=tempWonAmt,
                      outCd=outCd,
                      outSeq=outSeq,
                      note=note,
                      state='R',
                      regUser=user,
                      regDate=datetime.now(),
                      modUser=None,
                      modDate=None)
    if outCd:
        # stk_lot update
        lot.docQty = int(lot.docQty) - int(out.outQty)
        lot.modUser = user
        lot.modDate = datetime.now()

        # stk_out update
        out.sellYn = 'Y'

    db.session.add(stkSell)

    if outCd:
        db.session.add(lot)
        db.session.add(out)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkSell': stkSell.to_json()
    })


@main.route('/api/selStkSellTemp', methods=['POST'])
def select_stk_sell_temp():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    custCd = json_data.get('custCd')
    custText = json_data.get('custText')
    sellNo = json_data.get('sellNo')
    prjCd = json_data.get('prjCd')
    prjText = json_data.get('prjText')
    manager = json_data.get('manager')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT '0' as chk, a.siteCd, a.sellCd, a.sellSeq, a.sellNo, \
                CONCAT(LEFT(a.sellDate, 4), '-', SUBSTRING(a.sellDate, 5, 2), '-', RIGHT(a.sellDate, 2)) AS sellDate, \
                a.sellState, fn_get_codename('W0021', a.sellState) as sellStateNm, \
                a.psvType, a.serviceYn, a.poCd, a.custCd, b.custNm, \
                case when c.prjCd is null then a.project else c.prjNm end AS project, \
                a.manager, \
                ifnull(a.unitAmt, 0.00) as unitAmt, \
                ifnull(a.taxAmt, 0.00) as taxAmt, \
                ifnull(a.sellAmt, 0.00) as sellAmt, \
                ifnull(a.tempServiceAmt, 0.00) AS tempServiceAmt, \
                ifnull(a.tempExcRate, 0.00) AS tempExcRate, \
                ifnull(a.tempWonAmt, 0.00) AS tempWonAmt, \
                (ifnull(a.tempServiceAmt, 0.00) + ifnull(a.tempWonAmt, 0.00)) * ifnull(a.tempExcRate, 0.00) AS wonAmt, \
                case when ifnull(a.unitAmt, 0.00) > 0 then (1 - ((ifnull(a.tempServiceAmt, 0.00) + ifnull(a.tempWonAmt, 0.00)) * ifnull(a.tempExcRate, 0.00) / a.unitAmt)) * 100 else 0.00 end AS profitRate, \
                a.note, \
                a.prjCd \
            FROM stk_sell a \
            LEFT OUTER JOIN mst_cust b \
            ON a.siteCd = b.siteCd \
            AND a.custCd = b.custCd \
            LEFT OUTER JOIN mst_project c \
            ON a.siteCd = c.siteCd \
            AND a.prjCd = c.prjCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.sellDate BETWEEN '" + fDate + "' AND '" + tDate + "' \
            AND a.state = 'R' \
            AND a.sellSeq = 0 "
    if sellNo is not None:
        sql += " AND a.sellNo LIKE CONCAT('%', '" + sellNo + "', '%')"
    if custCd is not None:
        sql += " AND a.custCd = '" + custCd + "'"
    if custText is not None and custText != '':
        sql += " AND ( a.custCd LIKE CONCAT('%', '" + custText + \
            "', '%') OR b.custNm LIKE CONCAT('%', '" + custText + "', '%') )"
    if prjCd is not None:
        sql += " AND a.prjCd = '" + prjCd + "' "
    if prjText is not None and prjText != '':
        sql += " AND ( a.prjCd LIKE CONCAT('%', '" + prjText + \
            "', '%') OR c.prjNm LIKE CONCAT('%', '" + prjText + "', '%') )"
    if manager is not None:
        sql += " AND a.manager like '%" + manager + "%' "
    sql += " order by sellCd desc"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['sellCd'] = tr[2]
        dic['SellSeq'] = tr[3]
        dic['sellNo'] = tr[4]
        dic['sellDate'] = tr[5]
        dic['sellState'] = tr[6]
        dic['sellStateNm'] = tr[7]
        dic['psvType'] = tr[8]
        dic['serviceYn'] = tr[9]
        dic['poCd'] = tr[10]
        dic['custCd'] = tr[11]
        dic['custNm'] = tr[12]
        dic['project'] = tr[13]
        dic['manager'] = tr[14]
        dic['unitAmt'] = tr[15]
        dic['taxAmt'] = tr[16]
        dic['sellAmt'] = tr[17]
        dic['tempServiceAmt'] = tr[18]
        dic['tempExcRate'] = tr[19]
        dic['tempWonAmt'] = tr[20]
        dic['wonAmt'] = tr[21]
        dic['profitRate'] = tr[22]
        dic['note'] = tr[23]
        dic['prjCd'] = tr[24]

        data[index] = dic

    return simplejson.dumps({'sellTemp': data})


@main.route('/api/selStkSellTempDetail', methods=['POST'])
def select_stk_sell_temp_detail():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')
    psvTypeMulti = json_data.get('psvTypeMulti')
    modSelectType = json_data.get('modSelectType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    # sql = "SELECT '0' AS chk, a.siteCd, d.poCd, d.poNo, \
    #                 d.poState, fn_get_codename('P0002', d.poState) AS poStateNm, \
    #                 CONCAT(LEFT(d.poDate, 4), '-', SUBSTRING(d.poDate, 5, 2), '-', RIGHT(d.poDate, 2)) AS poDate, \
    #                 d.poType1, fn_get_codename('P0003', d.poType1) AS poType1Nm, \
    #                 d.poType2, fn_get_codename('P0004', d.poType2) AS poType2Nm, \
    #                 d.poType3, fn_get_codename('P0005', d.poType3) AS poType3Nm, \
    #                 d.custCd AS poCustCd, fn_get_custname(d.siteCd, d.custCd) AS poCustNm, \
    #                 d.soNo, d.poQty, d.unitAmt, d.taxAmt, d.purcAmt, \
    #                 d.posState, fn_get_codename('P0001', d.posState) AS posStateNm, \
    #                 d.note AS poNote, \
    #                 c.inCd, c.inSeq, c.inNo, \
    #                 CONCAT(LEFT(c.inDate, 4), '-', SUBSTRING(c.inDate, 5, 2), '-', RIGHT(c.inDate, 2)) AS inDate, \
    #                 c.lotNo, c.sn, \
    #                 c.inKind, fn_get_codename('W0001', c.inKind) AS inKindNm, \
    #                 c.purcYn, \
    #                 c.inType, fn_get_codename('W0002', c.inType) AS inTypeNm, \
    #                 c.inQty, \
    #                 c.inAmt, \
    #                 c.currency, fn_get_codename('S0006', c.currency) AS currencyNm, \
    #                 c.cmLoc, c.bl, c.invoice, c.inWarr, \
    #                 c.partRank, fn_get_codename('W0004', c.partRank) AS pratRankNm, \
    #                 c.note AS inNote, \
    #                 b.outCd, b.outSeq, b.outNo, \
    #                 CONCAT(LEFT(b.outDate, 4), '-', SUBSTRING(b.outDate, 5, 2), '-', RIGHT(b.outDate, 2)) AS outDate, \
    #                 b.outKind, fn_get_codename('W0011', b.outKind) AS outKindNm, \
    #                 b.sellYn, \
    #                 b.outType, fn_get_codename('W0012', b.outType) AS outTypeNm, \
    #                 b.requester, b.sender, b.outQty, b.arrAddr, b.recipient, b.recipientTel, b.transporter, b.transporterTel, b.receiptYn, \
    #                 b.note AS outNote, \
    #                 a.lotNo, \
    #                 a.sn, \
    #                 a.partCd, e.partNm, a.whCd, f.whNm, a.loc, a.curQty, a.docQty, \
    #                 a.unit, fn_get_codename('S0005', a.unit) AS unitNm, \
    #                 g.sellCd, g.sellSeq, g.sellNo, \
    #                 CONCAT(LEFT(g.sellDate, 4), '-', SUBSTRING(g.sellDate, 5, 2), '-', RIGHT(g.sellDate, 2)) AS sellDate, \
    #                 g.sellState, fn_get_codename('W0021', g.sellState) AS sellStateNm, \
    #                 g.psvType, fn_get_codename('W0022', g.psvType) AS psvTypeNm, \
    #                 g.serviceYn, \
    #                 g.custCd AS sellCustCd, fn_get_custname(g.siteCd, g.custCd) AS sellCustNm, \
    #                 g.project, g.manager, IFNULL(g.unitAmt, 0.00) AS sellUnitAmt, IFNULL(g.taxAmt, 0.00) AS sellTaxAmt, IFNULL(g.sellAmt, 0.00) AS sellAmt, g.note AS sellNote, \
    #                 a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm \
    #         FROM stk_lot a \
    #         INNER JOIN stk_out b \
    #         ON a.siteCd = b.siteCd \
    #         AND a.lotNo = b.lotNo \
    #         AND b.state = 'R' \
    #         INNER JOIN stk_in c \
    #         ON a.siteCd = c.siteCd \
    #         AND a.lotNo = c.lotNo \
    #         AND c.state = 'R' \
    #         LEFT OUTER JOIN pur_order d \
    #         ON c.siteCd = d.siteCd \
    #         AND c.poCd = d.poCd \
    #         AND d.state = 'R' \
    #         LEFT OUTER JOIN mst_part e \
    #         ON a.siteCd = e.siteCd \
    #         AND a.partCd = e.partCd \
    #         LEFT OUTER JOIN mst_wh f \
    #         ON a.siteCd = f.siteCd \
    #         AND a.whCd = f.whCd \
    #         INNER JOIN stk_sell g \
    #         ON b.siteCd = g.siteCd \
    #         AND b.outCd = g.outCd \
    #         AND b.outSeq = g.outSeq \
    #         AND g.state = 'R' \
    #         WHERE g.siteCd = '" + siteCd + "' \
    #         AND g.sellCd = '" + sellCd + "'"

    sql = "SELECT '0' AS chk, x.siteCd, y.poCd, y.poNo, \
                    y.poState, fn_get_codename('P0002', y.poState) AS poStateNm,  \
                    CONCAT(LEFT(y.poDate, 4), '-', SUBSTRING(y.poDate, 5, 2), '-', RIGHT(y.poDate, 2)) AS poDate,  \
                    y.poType1, fn_get_codename('P0003', y.poType1) AS poType1Nm,  \
                    y.poType2, fn_get_codename('P0004', y.poType2) AS poType2Nm,  \
                    y.poType3, fn_get_codename('P0005', y.poType3) AS poType3Nm,  \
                    y.poCustCd, fn_get_custname(y.siteCd, y.poCustCd) AS poCustNm, \
                    y.soNo, y.poQty, y.unitAmt, y.taxAmt, y.purcAmt, \
                    y.posState, fn_get_codename('P0001', y.posState) AS posStateNm,  \
                    y.poNote,  \
                    y.inCd, y.inSeq, y.inNo,  \
                    CONCAT(LEFT(y.inDate, 4), '-', SUBSTRING(y.inDate, 5, 2), '-', RIGHT(y.inDate, 2)) AS inDate, \
                    y.inKind, fn_get_codename('W0001', y.inKind) AS inKindNm, \
                    y.purcYn, \
                    y.inType, fn_get_codename('W0002', y.inType) AS inTypeNm, \
                    y.inQty, \
                    y.inAmt, \
                    y.currency, fn_get_codename('S0006', y.currency) AS currencyNm, \
                    y.cmLoc, y.bl, y.invoice, y.inWarr, \
                    y.partRank, fn_get_codename('W0004', y.partRank) AS pratRankNm, \
                    y.inNote, \
                    y.outCd, y.outSeq, y.outNo, \
                    CONCAT(LEFT(y.outDate, 4), '-', SUBSTRING(y.outDate, 5, 2), '-', RIGHT(y.outDate, 2)) AS outDate, \
                    y.outKind, fn_get_codename('W0011', y.outKind) AS outKindNm, \
                    y.sellYn, \
                    y.outType, fn_get_codename('W0012', y.outType) AS outTypeNm, \
                    y.requester, y.sender, y.outQty, y.arrAddr, y.recipient, y.recipientTel, y.transporter, y.transporterTel, y.receiptYn, \
                    y.outNote, \
                    y.lotNo, \
                    y.sn, \
                    y.partCd, y.partNm, y.whCd, y.whNm, y.loc, y.curQty, y.docQty, \
                    y.unit, fn_get_codename('S0005', y.unit) AS unitNm, \
                    x.sellCd, x.sellSeq, x.sellNo, \
                    CONCAT(LEFT(x.sellDate, 4), '-', SUBSTRING(x.sellDate, 5, 2), '-', RIGHT(x.sellDate, 2)) AS sellDate, \
                    x.sellState, fn_get_codename('W0021', x.sellState) AS sellStateNm, \
                    x.psvType, fn_get_codename('W0022', x.psvType) AS psvTypeNm, \
                    x.serviceYn, \
                    x.custCd AS sellCustCd, fn_get_custname(x.siteCd, x.custCd) AS sellCustNm, \
                    case when z.prjCd is null then x.project else z.prjNm end AS project, \
                    x.manager, IFNULL(x.unitAmt, 0.00) AS sellUnitAmt, IFNULL(x.taxAmt, 0.00) AS sellTaxAmt, IFNULL(x.sellAmt, 0.00) AS sellAmt, x.note AS sellNote, \
                    y.stkType, fn_get_codename('W0023', y.stkType) AS stkTypeNm, \
                    IFNULL(x.tempServiceAmt, 0.00) AS tempServiceAmt, \
                    IFNULL(x.tempExcRate, 0.00) AS tempExcRate, \
                    IFNULL(x.tempWonAmt, 0.00) AS tempWonAmt, \
                    (IFNULL(x.tempServiceAmt, 0.00) + IFNULL(x.tempWonAmt, 0.00)) * IFNULL(x.tempExcRate, 0.00) AS wonAmt, \
                    case when IFNULL(x.unitAmt, 0.00) > 0 then (1 - ((IFNULL(x.tempServiceAmt, 0.00) + IFNULL(x.tempWonAmt, 0.00)) * IFNULL(x.tempExcRate, 0.00) / x.unitAmt)) * 100 ELSE 0.00 end AS profitRate, \
                    x.prjCd \
            FROM stk_sell x \
            LEFT OUTER JOIN ( \
                SELECT a.siteCd, d.poCd, d.poNo, d.poState, d.poDate, d.poType1, d.poType2, d.poType3, d.custCd AS poCustCd, d.soNo, d.poQty, d.unitAmt, d.taxAmt, d.purcAmt, d.posState, d.note AS poNote, \
                        c.inCd, c.inSeq, c.inNo, c.inDate, c.inKind, c.purcYn, c.inType, c.inQty, c.inAmt, c.currency, c.cmLoc, c.bl, c.invoice, c.inWarr, c.partRank, c.note AS inNote, \
                        b.outCd, b.outSeq, b.outNo, b.outDate, b.outKind, b.sellYn, b.outType, b.requester, b.sender, b.outQty, b.arrAddr, b.recipient, b.recipientTel, b.transporter, b.transporterTel, b.receiptYn, b.note AS outNote, \
                        a.lotNo, a.sn, a.partCd, e.partNm, a.whCd, f.whNm, a.loc, a.curQty, a.docQty, a.unit, a.stkType \
                FROM stk_lot a \
                INNER JOIN stk_out b \
                ON a.siteCd = b.siteCd \
                AND a.lotNo = b.lotNo \
                AND b.state = 'R' \
                INNER JOIN stk_in c \
                ON a.siteCd = c.siteCd \
                AND a.lotNo = c.lotNo \
                AND c.state = 'R' \
                LEFT OUTER JOIN pur_order d \
                ON c.siteCd = d.siteCd \
                AND c.poCd = d.poCd \
                AND d.state = 'R' \
                LEFT OUTER JOIN mst_part e \
                ON a.siteCd = e.siteCd \
                AND a.partCd = e.partCd \
                LEFT OUTER JOIN mst_wh f \
                ON a.siteCd = f.siteCd \
                AND a.whCd = f.whCd \
                INNER JOIN stk_sell g \
                ON b.siteCd = g.siteCd \
                AND b.outCd = g.outCd \
                AND b.outSeq = g.outSeq \
                AND g.state = 'R' \
            ) y \
            ON x.siteCd = y.siteCd \
            AND x.outCd = y.outCd \
            AND x.outSeq = y.outSeq \
            LEFT OUTER JOIN mst_project z \
            ON x.siteCd = z.siteCd \
            AND x.prjCd = z.prjCd \
            WHERE x.siteCd = '" + siteCd + "' \
            AND x.sellCd = '" + sellCd + "' \
            AND x.state = 'R'"

    if psvTypeMulti:
        sql += " AND x.psvType in (" + psvTypeMulti + ")"

    if modSelectType is None:
        sql += " AND x.sellSeq <> 0"

    sql += " ORDER BY x.sellSeq;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poState'] = tr[4]
        dic['poStateNm'] = tr[5]
        dic['poDate'] = tr[6]
        dic['poType1'] = tr[7]
        dic['poType1Nm'] = tr[8]
        dic['poType2'] = tr[9]
        dic['poType2Nm'] = tr[10]
        dic['poType3'] = tr[11]
        dic['poType3Nm'] = tr[12]
        dic['poCustCd'] = tr[13]
        dic['poCustNm'] = tr[14]
        dic['soNo'] = tr[15]
        dic['poQty'] = tr[16]
        dic['unitAmt'] = tr[17]
        dic['taxAmt'] = tr[18]
        dic['purcAmt'] = tr[19]
        dic['posState'] = tr[20]
        dic['posStateNm'] = tr[21]
        dic['poNote'] = tr[22]
        dic['inCd'] = tr[23]
        dic['inSeq'] = tr[24]
        dic['inNo'] = tr[25]
        dic['inDate'] = tr[26]
        dic['inKind'] = tr[27]
        dic['inKindNm'] = tr[28]
        dic['purcYn'] = tr[29]
        dic['inType'] = tr[30]
        dic['inTypeNm'] = tr[31]
        dic['inQty'] = tr[32]
        dic['inAmt'] = tr[33]
        dic['currency'] = tr[34]
        dic['currencyNm'] = tr[35]
        dic['cmLoc'] = tr[36]
        dic['bl'] = tr[37]
        dic['invoice'] = tr[38]
        dic['inWarr'] = tr[39]
        dic['partRank'] = tr[40]
        dic['partRankNm'] = tr[41]
        dic['inNote'] = tr[42]
        dic['outCd'] = tr[43]
        dic['outSeq'] = tr[44]
        dic['outNo'] = tr[45]
        dic['outDate'] = tr[46]
        dic['outKind'] = tr[47]
        dic['outKindNm'] = tr[48]
        dic['sellYn'] = tr[49]
        dic['outType'] = tr[50]
        dic['outTypeNm'] = tr[51]
        dic['requester'] = tr[52]
        dic['sender'] = tr[53]
        dic['outQty'] = tr[54]
        dic['arrAddr'] = tr[55]
        dic['recipient'] = tr[56]
        dic['recipientTel'] = tr[57]
        dic['transpoter'] = tr[58]
        dic['transpoterTel'] = tr[59]
        dic['receiptYn'] = tr[60]
        dic['outNote'] = tr[61]
        dic['lotNo'] = tr[62]
        dic['sn'] = tr[63]
        dic['partCd'] = tr[64]
        dic['partNm'] = tr[65]
        dic['whCd'] = tr[66]
        dic['whNm'] = tr[67]
        dic['loc'] = tr[68]
        dic['curQty'] = tr[69]
        dic['docQty'] = tr[70]
        dic['unit'] = tr[71]
        dic['unitNm'] = tr[72]
        dic['sellCd'] = tr[73]
        dic['sellSeq'] = tr[74]
        dic['sellNo'] = tr[75]
        dic['sellDate'] = tr[76]
        dic['sellState'] = tr[77]
        dic['sellStateNm'] = tr[78]
        dic['psvType'] = tr[79]
        dic['psvTypeNm'] = tr[80]
        dic['serviceYn'] = tr[81]
        dic['sellCustCd'] = tr[82]
        dic['sellCustNm'] = tr[83]
        dic['project'] = tr[84]
        dic['manager'] = tr[85]
        dic['sellUnitAmt'] = tr[86]
        dic['sellTaxAmt'] = tr[87]
        dic['sellAmt'] = tr[88]
        dic['sellNote'] = tr[89]
        dic['stkType'] = tr[90]
        dic['stkTypeNm'] = tr[91]
        dic['tempServiceAmt'] = tr[92]
        dic['tempExcRate'] = tr[93]
        dic['tempWonAmt'] = tr[94]
        dic['wonAmt'] = tr[95]
        dic['profitRate'] = tr[96]
        dic['prjCd'] = tr[97]

        data[index] = dic

    return simplejson.dumps({'sellTemp': data})


@main.route('/api/updStkStockSellTemp', methods=['POST'])
def update_stk_sell_temp():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')
    sellDate = json_data.get('sellDate')
    sellNo = json_data.get('sellNo')
    custCd = json_data.get('custCd')
    prjCd = json_data.get('prjCd')
    manager = json_data.get('manager')
    unitAmt = json_data.get('unitAmt')
    taxAmt = json_data.get('taxAmt')
    sellAmt = json_data.get('sellAmt')
    tempServiceAmt = json_data.get('tempServiceAmt')
    tempExcRate = json_data.get('tempExcRate')
    tempWonAmt = json_data.get('tempWonAmt')
    note = json_data.get('note')
    user = json_data.get('user')

    stkSellMst = StkSell.query.filter_by(
        siteCd=siteCd, sellCd=sellCd, sellSeq=0, state='R').first()

    if stkSellMst is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })
    else:
        stkSellMst.sellDate = sellDate
        stkSellMst.sellNo = sellNo
        stkSellMst.custCd = custCd
        stkSellMst.prjCd = prjCd
        stkSellMst.manager = manager
        stkSellMst.unitAmt = unitAmt
        stkSellMst.taxAmt = taxAmt
        stkSellMst.sellAmt = sellAmt
        stkSellMst.tempServiceAmt = tempServiceAmt
        stkSellMst.tempExcRate = tempExcRate
        stkSellMst.tempWonAmt = tempWonAmt
        stkSellMst.note = note
        stkSellMst.modDate = datetime.now()
        stkSellMst.modUser = user

        db.session.add(stkSellMst)

    stkSellDtl = StkSell.query.filter(
        StkSell.siteCd == siteCd, StkSell.sellCd == sellCd, StkSell.sellSeq != 0, StkSell.state == 'R')

    if stkSellDtl is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })
    else:
        stkSellDtl.update({StkSell.sellDate: sellDate, StkSell.sellNo: sellNo, StkSell.custCd: custCd, StkSell.prjCd: prjCd,
                           StkSell.manager: manager, StkSell.note: note, StkSell.modDate: datetime.now(), StkSell.modUser: user})

    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkSell': stkSellMst.to_json()
    })


@main.route('/api/selStkSellTempDetailService', methods=['POST'])
def select_stk_sell_temp_detail_service():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT '0' AS chk, a.siteCd, d.poCd, d.poNo, \
                    d.poState, fn_get_codename('P0002', d.poState) AS poStateNm, \
                    CONCAT(LEFT(d.poDate, 4), '-', SUBSTRING(d.poDate, 5, 2), '-', RIGHT(d.poDate, 2)) AS poDate, \
                    d.poType1, fn_get_codename('P0003', d.poType1) AS poType1Nm, \
                    d.poType2, fn_get_codename('P0004', d.poType2) AS poType2Nm, \
                    d.poType3, fn_get_codename('P0005', d.poType3) AS poType3Nm, \
                    d.custCd AS poCustCd, fn_get_custname(d.siteCd, d.custCd) AS poCustNm, \
                    d.soNo, d.poQty, d.unitAmt, d.taxAmt, d.purcAmt, \
                    d.posState, fn_get_codename('P0001', d.posState) AS posStateNm, \
                    d.note AS poNote, \
                    c.inCd, c.inSeq, c.inNo, \
                    CONCAT(LEFT(c.inDate, 4), '-', SUBSTRING(c.inDate, 5, 2), '-', RIGHT(c.inDate, 2)) AS inDate, \
                    c.lotNo,	c.sn, \
                    c.inKind, fn_get_codename('W0001', c.inKind) AS inKindNm, \
                    c.purcYn, \
                    c.inType, fn_get_codename('W0002', c.inType) AS inTypeNm, \
                    c.inQty, \
                    c.inAmt, \
                    c.currency, fn_get_codename('S0006', c.currency) AS currencyNm, \
                    c.cmLoc, c.bl, c.invoice, c.inWarr, \
                    c.partRank, fn_get_codename('W0004', c.partRank) AS pratRankNm, \
                    c.note AS inNote, \
                    b.outCd, b.outSeq, b.outNo, \
                    CONCAT(LEFT(b.outDate, 4), '-', SUBSTRING(b.outDate, 5, 2), '-', RIGHT(b.outDate, 2)) AS outDate, \
                    b.outKind, fn_get_codename('W0011', b.outKind) AS outKindNm, \
                    b.sellYn, \
                    b.outType, fn_get_codename('W0012', b.outType) AS outTypeNm, \
                    b.requester, b.sender, b.outQty, b.arrAddr, b.recipient, b.recipientTel, b.transporter, b.transporterTel, b.receiptYn, \
                    b.note AS outNote, \
                    a.lotNo, \
                    a.sn, \
                    a.partCd, e.partNm, a.whCd, f.whNm, a.loc, a.curQty, a.docQty, \
                    a.unit, fn_get_codename('S0005', a.unit) AS unitNm, \
                    g.sellCd, g.sellSeq, g.sellNo, \
                    CONCAT(LEFT(g.sellDate, 4), '-', SUBSTRING(g.sellDate, 5, 2), '-', RIGHT(g.sellDate, 2)) AS sellDate, \
                    g.sellState, fn_get_codename('W0021', g.sellState) AS sellStateNm, \
                    g.psvType, fn_get_codename('W0022', g.psvType) AS psvTypeNm, \
                    g.serviceYn, \
                    g.custCd AS sellCustCd, fn_get_custname(g.siteCd, g.custCd) AS sellCustNm, \
                    case when j.prjCd is null then g.project else j.prjNm end AS project, \
                    g.manager, IFNULL(g.unitAmt, 0.00) AS sellUnitAmt, IFNULL(g.taxAmt, 0.00) AS sellTaxAmt, IFNULL(g.sellAmt, 0.00) AS sellAmt, g.note AS sellNote, \
                    g.prjCd \
            FROM stk_lot a \
            INNER JOIN stk_out b \
            ON a.siteCd = b.siteCd \
            AND a.lotNo = b.lotNo \
            AND b.state = 'R' \
            INNER JOIN stk_in c \
            ON a.siteCd = c.siteCd \
            AND a.lotNo = c.lotNo \
            AND c.state = 'R' \
            LEFT OUTER JOIN pur_order d \
            ON c.siteCd = d.siteCd \
            AND c.poCd = d.poCd \
            AND d.state = 'R' \
            LEFT OUTER JOIN mst_part e \
            ON a.siteCd = e.siteCd \
            AND a.partCd = e.partCd \
            LEFT OUTER JOIN mst_wh f \
            ON a.siteCd = f.siteCd \
            AND a.whCd = f.whCd \
            LEFT OUTER JOIN stk_sell g \
            ON b.siteCd = g.siteCd \
            AND b.outCd = g.outCd \
            AND b.outSeq = g.outSeq \
            AND g.state = 'R' \
            LEFT OUTER JOIN mst_project j \
            ON g.siteCd = j.siteCd \
            AND g.prjCd = j.prjCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.sn IN ( \
                SELECT s3.sn \
                FROM stk_sell s1 \
                INNER JOIN stk_out s2 \
                ON s1.siteCd = s2.siteCd \
                AND s1.outCd = s2.outCd \
                AND s1.outSeq = s2.outSeq \
                AND s2.state = 'R' \
                INNER JOIN stk_lot s3 \
                ON s2.siteCd = s3.siteCd \
                AND s2.lotNo = s3.lotNo \
                AND s3.state = 'R' \
                WHERE s1.sellCd = '" + sellCd + "' \
                AND s1.sellSeq <> 0 \
                AND s1.state = 'R' \
            ) \
            AND b.sellYn = 'N' \
            AND d.poType2 = 'V' \
            AND a.state = 'R';"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poState'] = tr[4]
        dic['poStateNm'] = tr[5]
        dic['poDate'] = tr[6]
        dic['poType1'] = tr[7]
        dic['poType1Nm'] = tr[8]
        dic['poType2'] = tr[9]
        dic['poType2Nm'] = tr[10]
        dic['poType3'] = tr[11]
        dic['poType3Nm'] = tr[12]
        dic['poCustCd'] = tr[13]
        dic['poCustNm'] = tr[14]
        dic['soNo'] = tr[15]
        dic['poQty'] = tr[16]
        dic['unitAmt'] = tr[17]
        dic['taxAmt'] = tr[18]
        dic['purcAmt'] = tr[19]
        dic['posState'] = tr[20]
        dic['posStateNm'] = tr[21]
        dic['poNote'] = tr[22]
        dic['inCd'] = tr[23]
        dic['inSeq'] = tr[24]
        dic['inNo'] = tr[25]
        dic['inDate'] = tr[26]
        dic['lotNo'] = tr[27]
        dic['sn'] = tr[28]
        dic['inKind'] = tr[29]
        dic['inKindNm'] = tr[30]
        dic['purcYn'] = tr[31]
        dic['inType'] = tr[32]
        dic['inTypeNm'] = tr[33]
        dic['inQty'] = tr[34]
        dic['inAmt'] = tr[35]
        dic['currency'] = tr[36]
        dic['currencyNm'] = tr[37]
        dic['cmLoc'] = tr[38]
        dic['bl'] = tr[39]
        dic['invoice'] = tr[40]
        dic['inWarr'] = tr[41]
        dic['partRank'] = tr[42]
        dic['partRankNm'] = tr[43]
        dic['inNote'] = tr[44]
        dic['outCd'] = tr[45]
        dic['outSeq'] = tr[46]
        dic['outNo'] = tr[47]
        dic['outDate'] = tr[48]
        dic['outKind'] = tr[49]
        dic['outKindNm'] = tr[50]
        dic['sellYn'] = tr[51]
        dic['outType'] = tr[52]
        dic['outTypeNm'] = tr[53]
        dic['requester'] = tr[54]
        dic['sender'] = tr[55]
        dic['outQty'] = tr[56]
        dic['arrAddr'] = tr[57]
        dic['recipient'] = tr[58]
        dic['recipientTel'] = tr[59]
        dic['transpoter'] = tr[60]
        dic['transpoterTel'] = tr[61]
        dic['receiptYn'] = tr[62]
        dic['outNote'] = tr[63]
        dic['lotNo'] = tr[64]
        dic['sn'] = tr[65]
        dic['partCd'] = tr[66]
        dic['partNm'] = tr[67]
        dic['whCd'] = tr[68]
        dic['whNm'] = tr[69]
        dic['loc'] = tr[70]
        dic['curQty'] = tr[71]
        dic['docQty'] = tr[72]
        dic['unit'] = tr[73]
        dic['unitNm'] = tr[74]
        dic['sellCd'] = tr[75]
        dic['sellSeq'] = tr[76]
        dic['sellNo'] = tr[77]
        dic['sellDate'] = tr[78]
        dic['sellState'] = tr[79]
        dic['sellStateNm'] = tr[80]
        dic['psvType'] = tr[81]
        dic['psvTypeNm'] = tr[82]
        dic['serviceYn'] = tr[83]
        dic['sellCustCd'] = tr[84]
        dic['sellCustNm'] = tr[85]
        dic['project'] = tr[86]
        dic['manager'] = tr[87]
        dic['sellUnitAmt'] = tr[88]
        dic['sellTaxAmt'] = tr[89]
        dic['sellAmt'] = tr[90]
        dic['sellNote'] = tr[91]
        dic['prjCd'] = tr[92]

        data[index] = dic

    return simplejson.dumps({'sellTemp': data})


@main.route('/api/selStkSellTempDetailServiceSearch', methods=['POST'])
def select_stk_sell_temp_detail_service_search():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    poNo = json_data.get('poNo')
    sn = json_data.get('sn')
    notMultiLotNo = json_data.get('notMultiLotNo')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT '0' AS chk, a.siteCd, d.poCd, d.poNo, \
                    d.poState, fn_get_codename('P0002', d.poState) AS poStateNm, \
                    CONCAT(LEFT(d.poDate, 4), '-', SUBSTRING(d.poDate, 5, 2), '-', RIGHT(d.poDate, 2)) AS poDate, \
                    d.poType1, fn_get_codename('P0003', d.poType1) AS poType1Nm, \
                    d.poType2, fn_get_codename('P0004', d.poType2) AS poType2Nm, \
                    d.poType3, fn_get_codename('P0005', d.poType3) AS poType3Nm, \
                    d.custCd AS poCustCd, fn_get_custname(d.siteCd, d.custCd) AS poCustNm, \
                    d.soNo, d.poQty, d.unitAmt, d.taxAmt, d.purcAmt, \
                    d.posState, fn_get_codename('P0001', d.posState) AS posStateNm, \
                    d.note AS poNote, \
                    c.inCd, c.inSeq, c.inNo, \
                    CONCAT(LEFT(c.inDate, 4), '-', SUBSTRING(c.inDate, 5, 2), '-', RIGHT(c.inDate, 2)) AS inDate, \
                    c.lotNo,	c.sn, \
                    c.inKind, fn_get_codename('W0001', c.inKind) AS inKindNm, \
                    c.purcYn, \
                    c.inType, fn_get_codename('W0002', c.inType) AS inTypeNm, \
                    c.inQty, \
                    c.inAmt, \
                    c.currency, fn_get_codename('S0006', c.currency) AS currencyNm, \
                    c.cmLoc, c.bl, c.invoice, c.inWarr, \
                    c.partRank, fn_get_codename('W0004', c.partRank) AS pratRankNm, \
                    c.note AS inNote, \
                    b.outCd, b.outSeq, b.outNo, \
                    CONCAT(LEFT(b.outDate, 4), '-', SUBSTRING(b.outDate, 5, 2), '-', RIGHT(b.outDate, 2)) AS outDate, \
                    b.outKind, fn_get_codename('W0011', b.outKind) AS outKindNm, \
                    b.sellYn, \
                    b.outType, fn_get_codename('W0012', b.outType) AS outTypeNm, \
                    b.requester, b.sender, b.outQty, b.arrAddr, b.recipient, b.recipientTel, b.transporter, b.transporterTel, b.receiptYn, \
                    b.note AS outNote, \
                    a.lotNo, \
                    a.sn, \
                    a.partCd, e.partNm, a.whCd, f.whNm, a.loc, a.curQty, a.docQty, \
                    a.unit, fn_get_codename('S0005', a.unit) AS unitNm, \
                    g.sellCd, g.sellSeq, g.sellNo, \
                    CONCAT(LEFT(g.sellDate, 4), '-', SUBSTRING(g.sellDate, 5, 2), '-', RIGHT(g.sellDate, 2)) AS sellDate, \
                    g.sellState, fn_get_codename('W0021', g.sellState) AS sellStateNm, \
                    g.psvType, fn_get_codename('W0022', g.psvType) AS psvTypeNm, \
                    g.serviceYn, \
                    g.custCd AS sellCustCd, fn_get_custname(g.siteCd, g.custCd) AS sellCustNm, \
                    case when j.prjCd is null then g.project else j.prjNm end AS project, \
                    g.manager, IFNULL(g.unitAmt, 0.00) AS sellUnitAmt, IFNULL(g.taxAmt, 0.00) AS sellTaxAmt, IFNULL(g.sellAmt, 0.00) AS sellAmt, g.note AS sellNote, \
                    j.prjCd \
            FROM stk_lot a \
            INNER JOIN stk_out b \
            ON a.siteCd = b.siteCd \
            AND a.lotNo = b.lotNo \
            AND b.state = 'R' \
            INNER JOIN stk_in c \
            ON a.siteCd = c.siteCd \
            AND a.lotNo = c.lotNo \
            AND c.state = 'R' \
            LEFT OUTER JOIN pur_order d \
            ON c.siteCd = d.siteCd \
            AND c.poCd = d.poCd \
            AND d.state = 'R' \
            LEFT OUTER JOIN mst_part e \
            ON a.siteCd = e.siteCd \
            AND a.partCd = e.partCd \
            LEFT OUTER JOIN mst_wh f \
            ON a.siteCd = f.siteCd \
            AND a.whCd = f.whCd \
            LEFT OUTER JOIN stk_sell g \
            ON b.siteCd = g.siteCd \
            AND b.outCd = g.outCd \
            AND b.outSeq = g.outSeq \
            AND g.state = 'R' \
            LEFT OUTER JOIN mst_project j \
            ON g.siteCd = j.siteCd \
            AND g.prjCd = j.prjCd \
            WHERE a.siteCd = '" + siteCd + "'"
    if poNo:
        sql += " AND d.poNo LIKE '%" + poNo + "%'"
    if sn:
        sql += " AND a.sn LIKE '%" + sn + "%'"
    if notMultiLotNo:
        sql += " AND a.lotNo NOT IN (" + notMultiLotNo + ")"
    sql += " AND b.sellYn = 'N' \
             AND d.poType2 = 'V' \
             AND a.state = 'R';"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poState'] = tr[4]
        dic['poStateNm'] = tr[5]
        dic['poDate'] = tr[6]
        dic['poType1'] = tr[7]
        dic['poType1Nm'] = tr[8]
        dic['poType2'] = tr[9]
        dic['poType2Nm'] = tr[10]
        dic['poType3'] = tr[11]
        dic['poType3Nm'] = tr[12]
        dic['poCustCd'] = tr[13]
        dic['poCustNm'] = tr[14]
        dic['soNo'] = tr[15]
        dic['poQty'] = tr[16]
        dic['unitAmt'] = tr[17]
        dic['taxAmt'] = tr[18]
        dic['purcAmt'] = tr[19]
        dic['posState'] = tr[20]
        dic['posStateNm'] = tr[21]
        dic['poNote'] = tr[22]
        dic['inCd'] = tr[23]
        dic['inSeq'] = tr[24]
        dic['inNo'] = tr[25]
        dic['inDate'] = tr[26]
        dic['lotNo'] = tr[27]
        dic['sn'] = tr[28]
        dic['inKind'] = tr[29]
        dic['inKindNm'] = tr[30]
        dic['purcYn'] = tr[31]
        dic['inType'] = tr[32]
        dic['inTypeNm'] = tr[33]
        dic['inQty'] = tr[34]
        dic['inAmt'] = tr[35]
        dic['currency'] = tr[36]
        dic['currencyNm'] = tr[37]
        dic['cmLoc'] = tr[38]
        dic['bl'] = tr[39]
        dic['invoice'] = tr[40]
        dic['inWarr'] = tr[41]
        dic['partRank'] = tr[42]
        dic['partRankNm'] = tr[43]
        dic['inNote'] = tr[44]
        dic['outCd'] = tr[45]
        dic['outSeq'] = tr[46]
        dic['outNo'] = tr[47]
        dic['outDate'] = tr[48]
        dic['outKind'] = tr[49]
        dic['outKindNm'] = tr[50]
        dic['sellYn'] = tr[51]
        dic['outType'] = tr[52]
        dic['outTypeNm'] = tr[53]
        dic['requester'] = tr[54]
        dic['sender'] = tr[55]
        dic['outQty'] = tr[56]
        dic['arrAddr'] = tr[57]
        dic['recipient'] = tr[58]
        dic['recipientTel'] = tr[59]
        dic['transpoter'] = tr[60]
        dic['transpoterTel'] = tr[61]
        dic['receiptYn'] = tr[62]
        dic['outNote'] = tr[63]
        dic['lotNo'] = tr[64]
        dic['sn'] = tr[65]
        dic['partCd'] = tr[66]
        dic['partNm'] = tr[67]
        dic['whCd'] = tr[68]
        dic['whNm'] = tr[69]
        dic['loc'] = tr[70]
        dic['curQty'] = tr[71]
        dic['docQty'] = tr[72]
        dic['unit'] = tr[73]
        dic['unitNm'] = tr[74]
        dic['sellCd'] = tr[75]
        dic['sellSeq'] = tr[76]
        dic['sellNo'] = tr[77]
        dic['sellDate'] = tr[78]
        dic['sellState'] = tr[79]
        dic['sellStateNm'] = tr[80]
        dic['psvType'] = tr[81]
        dic['psvTypeNm'] = tr[82]
        dic['serviceYn'] = tr[83]
        dic['sellCustCd'] = tr[84]
        dic['sellCustNm'] = tr[85]
        dic['project'] = tr[86]
        dic['manager'] = tr[87]
        dic['sellUnitAmt'] = tr[88]
        dic['sellTaxAmt'] = tr[89]
        dic['sellAmt'] = tr[90]
        dic['sellNote'] = tr[91]
        dic['prjCd'] = tr[92]

        data[index] = dic

    return simplejson.dumps({'sellTemp': data})


@main.route('/api/regStkStockSellReal', methods=['POST'])
def regist_stk_sell_real():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')
    sellSeq = json_data.get('sellSeq')
    sellDate = json_data.get('sellDate')
    sellNo = json_data.get('sellNo')
    sellState = json_data.get('sellState')
    psvType = json_data.get('psvType')
    serviceYn = json_data.get('serviceYn')
    poCd = json_data.get('poCd')
    custCd = json_data.get('custCd')
    prjCd = json_data.get('prjCd')
    manager = json_data.get('manager')
    unitAmt = json_data.get('unitAmt')
    taxAmt = json_data.get('taxAmt')
    sellAmt = json_data.get('sellAmt')
    currency = json_data.get('currency')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    note = json_data.get('note')
    user = json_data.get('user')

    if not sellSeq:
        sel_sellSeq = StkSell.query.filter(
            StkSell.siteCd == siteCd, StkSell.sellCd == sellCd).order_by(StkSell.sellSeq.desc()).first()
        if sel_sellSeq is not None:
            sellSeq = int(sel_sellSeq.sellSeq) + 1

        if outCd:
            # check stk_out
            out = StkOut.query.filter_by(
                siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
            if out is None:
                return jsonify({
                    'result': {
                        'code': 8606,
                        'msg': '출고정보가 존재하지 않습니다.'
                    }
                })

            lot = StkLot.query.filter_by(
                siteCd=siteCd, lotNo=out.lotNo, state='R').first()
            if lot is None:
                return jsonify({
                    'result': {
                        'code': 8605,
                        'msg': '재고정보가 존재하지 않습니다.'
                    }
                })

        # stk_sell insert
        stkSell = StkSell(siteCd=siteCd,
                          sellCd=sellCd,
                          sellSeq=sellSeq,
                          sellNo=sellNo,
                          sellDate=sellDate,
                          sellState=sellState,
                          psvType=psvType,
                          serviceYn=serviceYn,
                          poCd=poCd,
                          custCd=custCd,
                          prjCd=prjCd,
                          manager=manager,
                          unitAmt=unitAmt,
                          taxAmt=taxAmt,
                          sellAmt=sellAmt,
                          currency=currency,
                          outCd=outCd,
                          outSeq=outSeq,
                          note=note,
                          state='R',
                          regUser=user,
                          regDate=datetime.now(),
                          modUser=None,
                          modDate=None)
        if outCd:
            # stk_lot update
            lot.docQty = int(lot.docQty) - int(out.outQty)
            lot.modUser = user
            lot.modDate = datetime.now()

            # stk_out update
            out.sellYn = 'Y'

        db.session.add(stkSell)

        if outCd:
            db.session.add(lot)
            db.session.add(out)
        db.session.commit()

    else:
        stkSell = StkSell.query.filter_by(
            siteCd=siteCd, sellCd=sellCd, sellSeq=sellSeq, state='R').first()
        stkSell.sellState = sellState
        if sellSeq != '0':
            stkSell.sellDate = sellDate
            stkSell.serviceYn = serviceYn
            stkSell.unitAmt = unitAmt
            stkSell.taxAmt = taxAmt
            stkSell.sellAmt = sellAmt
        stkSell.modUser = user
        stkSell.modDate = datetime.now()

        db.session.add(stkSell)
        db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkSell': stkSell.to_json()
    })


@main.route('/api/selStkSellHist', methods=['POST'])
def select_stk_sell_hist():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    custCd = json_data.get('custCd')
    custText = json_data.get('custText')
    sellNo = json_data.get('sellNo')
    prjCd = json_data.get('prjCd')
    prjText = json_data.get('prjText')
    manager = json_data.get('manager')
    stkType = json_data.get('stkType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT t.*, fn_get_codename('P0001', t.posState1) AS posState1Nm \
           FROM ( \
                SELECT '0' AS chk, a.siteCd, d.poCd, d.poNo, \
                    d.poState, fn_get_codename('P0002', d.poState) AS poStateNm, \
                    /*CONCAT(LEFT(d.poDate, 4), '-', SUBSTRING(d.poDate, 5, 2), '-', RIGHT(d.poDate, 2)) AS poDate,*/ \
                    STR_TO_DATE(d.poDate, '%Y%m%d') AS poDate, \
                    d.poType1, fn_get_codename('P0003', d.poType1) AS poType1Nm, \
                    d.poType2, fn_get_codename('P0004', d.poType2) AS poType2Nm, \
                    d.poType3, fn_get_codename('P0005', d.poType3) AS poType3Nm, \
                    d.custCd AS poCustCd, fn_get_custname(d.siteCd, d.custCd) AS poCustNm, \
                    d.soNo, d.poQty, d.unitAmt, d.taxAmt, d.purcAmt, \
                    d.posState, fn_get_codename('P0001', d.posState) AS posStateNm, \
                    d.note AS poNote, \
                    c.inCd, c.inSeq, c.inNo, \
                    /*CONCAT(LEFT(c.inDate, 4), '-', SUBSTRING(c.inDate, 5, 2), '-', RIGHT(c.inDate, 2)) AS inDate,*/ \
                    STR_TO_DATE(c.inDate, '%Y%m%d') AS inDate, \
                    c.inKind, fn_get_codename('W0001', c.inKind) AS inKindNm, \
                    c.purcYn, \
                    c.inType, fn_get_codename('W0002', c.inType) AS inTypeNm, \
                    c.inQty, \
                    c.inAmt, \
                    c.currency, fn_get_codename('S0006', c.currency) AS currencyNm, \
                    c.cmLoc, c.bl, c.invoice, c.inWarr, \
                    c.partRank, fn_get_codename('W0004', c.partRank) AS pratRankNm, \
                    c.note AS inNote, \
                    b.outCd, b.outSeq, b.outNo, \
                    /*CONCAT(LEFT(b.outDate, 4), '-', SUBSTRING(b.outDate, 5, 2), '-', RIGHT(b.outDate, 2)) AS outDate,*/ \
                    STR_TO_DATE(b.outDate, '%Y%m%d') AS outDate, \
                    b.outKind, fn_get_codename('W0011', b.outKind) AS outKindNm, \
                    b.sellYn, \
                    b.outType, fn_get_codename('W0012', b.outType) AS outTypeNm, \
                    b.requester, b.sender, b.outQty, b.arrAddr, b.recipient, b.recipientTel, b.transporter, b.transporterTel, b.receiptYn, \
                    b.note AS outNote, \
                    a.lotNo, \
                    a.sn, \
                    a.partCd, e.partNm, a.whCd, f.whNm, a.loc, a.curQty, a.docQty, \
                    a.unit, fn_get_codename('S0005', a.unit) AS unitNm, \
                    g.sellCd, g.sellSeq, g.sellNo, \
                    /*CONCAT(LEFT(g.sellDate, 4), '-', SUBSTRING(g.sellDate, 5, 2), '-', RIGHT(g.sellDate, 2)) AS sellDate,*/ \
                    STR_TO_DATE(g.sellDate, '%Y%m%d') AS sellDate, \
                    g.sellState, fn_get_codename('W0021', g.sellState) AS sellStateNm, \
                    g.psvType, fn_get_codename('W0022', g.psvType) AS psvTypeNm, \
                    g.serviceYn, \
                    g.custCd AS sellCustCd, fn_get_custname(g.siteCd, g.custCd) AS sellCustNm, \
                    case when j.prjCd is null then g.project else j.prjNm end AS project, \
                    g.manager, IFNULL(g.unitAmt, 0.00) AS sellUnitAmt, IFNULL(g.taxAmt, 0.00) AS sellTaxAmt, IFNULL(g.sellAmt, 0.00) AS sellAmt, g.note AS sellNote, \
                    a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm, \
                    i.spa, \
                    /*CASE WHEN i.posDate is null THEN '' ELSE CONCAT(LEFT(i.posDate, 4), '-', SUBSTRING(i.posDate, 5, 2), '-', RIGHT(i.posDate, 2)) END AS posDate,*/ \
                    STR_TO_DATE(i.posDate, '%Y%m%d') AS posDate, \
                    i.posQty, i.dc, i.reseller, i.endUser, i.netPos, i.am, i.partner, i.jda, i.vertical, i.year, i.quater, i.week, \
                    i.cmCd, \
                    /*CASE WHEN i.cmDate is null THEN '' ELSE CONCAT(LEFT(i.cmDate, 4), '-', SUBSTRING(i.cmDate, 5, 2), '-', RIGHT(i.cmDate, 2)) END AS cmDate,*/ \
                    STR_TO_DATE(i.cmDate, '%Y%m%d') AS cmDate, \
                    i.cmNo, i.rebAmt, i.remAmt, i.excRate, i.rebWonAmt, i.costWonAmt, \
                    IFNULL(c.inAmt, 0) - IFNULL(i.rebWonAmt, 0) AS goodsAmt, \
                    /*IFNULL(( \
                        SELECT CASE WHEN posState = 'D' THEN null ELSE posState END \
                        FROM pos_pos_log \
                        WHERE siteCd = c.siteCd \
                        AND poCd = c.poCd \
                        AND lotNo = c.lotNo \
                        ORDER BY regDate DESC LIMIT 1 \
                    ), d.posState) AS posState1*/ \
                    a.posState AS posState1, g.prjCd \
            FROM stk_lot a \
            INNER JOIN stk_out b \
            ON a.siteCd = b.siteCd \
            AND a.lotNo = b.lotNo \
            AND b.state = 'R' \
            INNER JOIN stk_in c \
            ON a.siteCd = c.siteCd \
            AND a.lotNo = c.lotNo \
            AND c.state = 'R' \
            LEFT OUTER JOIN pur_order d \
            ON c.siteCd = d.siteCd \
            AND c.poCd = d.poCd \
            AND d.state = 'R' \
            LEFT OUTER JOIN mst_part e \
            ON a.siteCd = e.siteCd \
            AND a.partCd = e.partCd \
            LEFT OUTER JOIN mst_wh f \
            ON a.siteCd = f.siteCd \
            AND a.whCd = f.whCd \
            INNER JOIN stk_sell g \
            ON b.siteCd = g.siteCd \
            AND b.outCd = g.outCd \
            AND b.outSeq = g.outSeq \
            AND g.state = 'R' \
            LEFT OUTER JOIN mst_cust h \
            ON g.siteCd = h.siteCd \
            AND g.custCd = h.custCd \
            LEFT OUTER JOIN ( \
                SELECT i1.*, i2.cmCd, i2.cmState, i2.cmDate, i2.cmNo, i2.rebAmt, i2.remAmt, i2.excRate, i2.rebWonAmt, i2.costWonAmt \
                FROM pos_pos i1 \
                LEFT OUTER  JOIN pos_cm i2 \
                ON i1.siteCd = i2.siteCd \
                AND i1.posCd = i2.posCd \
                AND i2.state = 'R' \
            ) i \
            ON a.siteCd = i.siteCd \
            AND a.lotNo = i.lotNo \
            AND c.poCd = i.poCd \
            AND i.state = 'R' \
            LEFT OUTER JOIN mst_project j \
            ON g.siteCd = j.siteCd \
            AND g.prjCd = j.prjCd \
            WHERE g.siteCd = '" + siteCd + "' \
            AND g.sellDate between '" + fDate + "' AND '" + tDate + "' "
    if sellNo is not None:
        sql += " AND g.sellNo LIKE CONCAT('%', '" + sellNo + "', '%')"
    if custCd is not None:
        sql += " AND g.custCd = '" + custCd + "'"
    if custText is not None and custText != '':
        sql += " AND ( g.custCd LIKE CONCAT('%', '" + custText + \
            "', '%') OR h.custNm LIKE CONCAT('%', '" + custText + "', '%') )"
    if prjCd is not None:
        sql += " AND g.prjCd = '" + prjCd + "'"
    if prjText is not None and prjText != '':
        sql += " AND ( g.prjCd LIKE CONCAT('%', '" + prjText + \
            "', '%') OR j.prjNm LIKE CONCAT('%', '" + prjText + "', '%') )"
    if manager is not None:
        sql += " AND g.manager like '%" + manager + "%' "
    if stkType is not None:
        sql += " AND a.stkType = '" + stkType + "' "

    # if psvTypeMulti:
    #     sql += "AND g.psvType in (" + psvTypeMulti + ")"

    sql += " AND g.sellSeq <> 0 \
            AND a.state = 'R' \
            ) t \
            ORDER BY sellCd desc, sn desc;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['siteCd'] = tr[1]
        dic['poCd'] = tr[2]
        dic['poNo'] = tr[3]
        dic['poState'] = tr[4]
        dic['poStateNm'] = tr[5]
        dic['poDate'] = tr[6]
        dic['poType1'] = tr[7]
        dic['poType1Nm'] = tr[8]
        dic['poType2'] = tr[9]
        dic['poType2Nm'] = tr[10]
        dic['poType3'] = tr[11]
        dic['poType3Nm'] = tr[12]
        dic['poCustCd'] = tr[13]
        dic['poCustNm'] = tr[14]
        dic['soNo'] = tr[15]
        dic['poQty'] = tr[16]
        dic['unitAmt'] = tr[17]
        dic['taxAmt'] = tr[18]
        dic['purcAmt'] = tr[19]
        dic['posState'] = tr[20]
        dic['posStateNm'] = tr[21]
        dic['poNote'] = tr[22]
        dic['inCd'] = tr[23]
        dic['inSeq'] = tr[24]
        dic['inNo'] = tr[25]
        dic['inDate'] = tr[26]
        dic['inKind'] = tr[27]
        dic['inKindNm'] = tr[28]
        dic['purcYn'] = tr[29]
        dic['inType'] = tr[30]
        dic['inTypeNm'] = tr[31]
        dic['inQty'] = tr[32]
        dic['inAmt'] = tr[33]
        dic['currency'] = tr[34]
        dic['currencyNm'] = tr[35]
        dic['cmLoc'] = tr[36]
        dic['bl'] = tr[37]
        dic['invoice'] = tr[38]
        dic['inWarr'] = tr[39]
        dic['partRank'] = tr[40]
        dic['partRankNm'] = tr[41]
        dic['inNote'] = tr[42]
        dic['outCd'] = tr[43]
        dic['outSeq'] = tr[44]
        dic['outNo'] = tr[45]
        dic['outDate'] = tr[46]
        dic['outKind'] = tr[47]
        dic['outKindNm'] = tr[48]
        dic['sellYn'] = tr[49]
        dic['outType'] = tr[50]
        dic['outTypeNm'] = tr[51]
        dic['requester'] = tr[52]
        dic['sender'] = tr[53]
        dic['outQty'] = tr[54]
        dic['arrAddr'] = tr[55]
        dic['recipient'] = tr[56]
        dic['recipientTel'] = tr[57]
        dic['transpoter'] = tr[58]
        dic['transpoterTel'] = tr[59]
        dic['receiptYn'] = tr[60]
        dic['outNote'] = tr[61]
        dic['lotNo'] = tr[62]
        dic['sn'] = tr[63]
        dic['partCd'] = tr[64]
        dic['partNm'] = tr[65]
        dic['whCd'] = tr[66]
        dic['whNm'] = tr[67]
        dic['loc'] = tr[68]
        dic['curQty'] = tr[69]
        dic['docQty'] = tr[70]
        dic['unit'] = tr[71]
        dic['unitNm'] = tr[72]
        dic['sellCd'] = tr[73]
        dic['sellSeq'] = tr[74]
        dic['sellNo'] = tr[75]
        dic['sellDate'] = tr[76]
        dic['sellState'] = tr[77]
        dic['sellStateNm'] = tr[78]
        dic['psvType'] = tr[79]
        dic['psvTypeNm'] = tr[80]
        dic['serviceYn'] = tr[81]
        dic['sellCustCd'] = tr[82]
        dic['sellCustNm'] = tr[83]
        dic['project'] = tr[84]
        dic['manager'] = tr[85]
        dic['sellUnitAmt'] = tr[86]
        dic['sellTaxAmt'] = tr[87]
        dic['sellAmt'] = tr[88]
        dic['sellNote'] = tr[89]
        dic['stkType'] = tr[90]
        dic['stkTypeNm'] = tr[91]
        dic['spa'] = tr[92]
        dic['posDate'] = tr[93]
        dic['posQty'] = tr[94]
        dic['dc'] = tr[95]
        dic['reseller'] = tr[96]
        dic['endUser'] = tr[97]
        dic['netPos'] = tr[98]
        dic['am'] = tr[99]
        dic['partner'] = tr[100]
        dic['jda'] = tr[101]
        dic['vertical'] = tr[102]
        dic['year'] = tr[103]
        dic['quater'] = tr[104]
        dic['week'] = tr[105]
        dic['cmCd'] = tr[106]
        dic['cmDate'] = tr[107]
        dic['cmNo'] = tr[108]
        dic['rebAmt'] = tr[109]
        dic['remAmt'] = tr[110]
        dic['excRate'] = tr[111]
        dic['rebWonAmt'] = tr[112]
        dic['costWonAmt'] = tr[113]
        dic['goodsAmt'] = tr[114]
        dic['posState1'] = tr[115]
        dic['prjCd'] = tr[116]
        dic['posState1Nm'] = tr[117]

        data[index] = dic

    return simplejson.dumps({'sellHist': data}, default=jsonhandler.date_handler)


@main.route('/api/updStkStockSell', methods=['POST'])
def update_stk_sell():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    sellCd = json_data.get('sellCd')
    sellSeq = json_data.get('sellSeq')
    sellDate = json_data.get('sellDate')
    sellNo = json_data.get('sellNo')
    sellState = json_data.get('sellState')
    psvType = json_data.get('psvType')
    serviceYn = json_data.get('serviceYn')
    poCd = json_data.get('poCd')
    custCd = json_data.get('custCd')
    prjCd = json_data.get('prjCd')
    manager = json_data.get('manager')
    unitAmt = json_data.get('unitAmt')
    taxAmt = json_data.get('taxAmt')
    sellAmt = json_data.get('sellAmt')
    currency = json_data.get('currency')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    data = StkSell.query.filter_by(
        siteCd=siteCd, sellCd=sellCd, sellSeq=sellSeq, state='R').first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state == 'D':
        out = StkOut.query.filter_by(
            siteCd=siteCd, outCd=data.outCd, outSeq=data.outSeq, state='R').first()
        if out is None:
            return jsonify({
                'result': {
                    'code': 8606,
                    'msg': '출고정보가 존재하지 않습니다.'
                }
            })

        lot = StkLot.query.filter_by(
            siteCd=siteCd, lotNo=out.lotNo, state='R').first()
        if lot is None:
            return jsonify({
                'result': {
                    'code': 8603,
                    'msg': '재고정보가 존재하지 않습니다.'
                }
            })

        others = StkSell.query.filter(StkSell.siteCd == siteCd, StkSell.sellCd ==
                                      sellCd, StkSell.sellSeq != sellSeq, StkSell.state == 'R').all()
        if len(others) == 1:
            for o in others:
                if o.sellSeq == 0:
                    o.modUser = user
                    o.modDate = datetime.now()
                    o.state = state or data.state
                    db.session.add(o)
                    break

        lot.docQty = int(lot.docQty) + int(out.outQty)
        lot.modUser = user
        lot.modDate = datetime.now()
        db.session.add(lot)

        out.sellYn = 'N'
        out.modUser = user
        out.modDate = datetime.now()
        db.session.add(out)

        data.modUser = user
        data.modDate = datetime.now()
        data.state = state or data.state
        db.session.add(data)

    else:
        data.sellDate = sellDate or data.sellDate
        data.sellNo = sellNo or data.sellNo
        data.sellState = sellState or data.sellState
        data.psvType = psvType or data.psvType
        data.serviceYn = serviceYn or data.serviceYn
        data.poCd = poCd or data.poCd
        data.custCd = custCd or data.custCd
        data.prjCd = prjCd or data.prjCd
        data.manager = manager or data.manager
        data.unitAmt = unitAmt or data.unitAmt
        data.taxAmt = taxAmt or data.taxAmt
        data.sellAmt = sellAmt or data.sellAmt
        data.currency = currency or data.currency
        data.outCd = outCd or data.outCd
        data.outSeq = outSeq or data.outSeq
        data.note = note or data.note
        data.modUser = user
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


@main.route('/api/selStkSellHistSpa', methods=['POST'])
def select_stk_sell_hist_spa():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    spa = json_data.get('spa')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT t.*, fn_get_codename('P0001', t.posState) AS posStateNm \
            FROM ( \
                SELECT a.posCd, \
                        /*IFNULL(( \
                                SELECT CASE WHEN posState = 'D' THEN null ELSE posState END \
                                FROM pos_pos_log \
                                WHERE siteCd = a.siteCd \
                                AND poCd = a.poCd \
                                AND lotNo = a.lotNo \
                                ORDER BY regDate DESC LIMIT 1 \
                        ), a.posState) AS posState,*/ \
                        c.posState AS posState, \
                        a.spa, \
                        CASE WHEN a.posDate is null THEN '' ELSE CONCAT(LEFT(a.posDate, 4), '-', SUBSTRING(a.posDate, 5, 2), '-', RIGHT(a.posDate, 2)) END AS posDate, \
                        a.posQty, a.dc, \
                        a.reseller, fn_get_custname(a.siteCd, a.reseller) AS resellerNm, \
                        a.endUser, fn_get_custname(a.siteCd, a.endUser) AS endUserNm, \
                        a.netPos, a.am, a.partner, a.jda, a.vertical, a.year, a.quater, a.week, a.poCd, a.lotNo, c.sn, \
                        e.cmCd, \
                        e.cmState, fn_get_codename('P0006', e.cmState) AS cmStateNm, \
                        CASE WHEN e.cmDate is null THEN '' ELSE CONCAT(LEFT(e.cmDate, 4), '-', SUBSTRING(e.cmDate, 5, 2), '-', RIGHT(e.cmDate, 2)) END AS cmDate, \
                        e.cmNo, e.rebAmt, e.remAmt, e.excRate, e.rebWonAmt, e.costWonAmt, \
                        IFNULL(b.inAmt, 0) - IFNULL(e.rebWonAmt, 0) AS goodsAmt, \
                        d.poNo \
                FROM pos_pos a \
                INNER JOIN stk_in b \
                ON a.siteCd = b.siteCd \
                AND a.poCd = b.poCd \
                AND a.lotNo = b.lotNo \
                INNER JOIN stk_lot c \
                ON b.siteCd = c.siteCd \
                AND b.lotNo = c.lotNo \
                INNER JOIN pur_order d \
                ON b.siteCd = d.siteCd \
                AND b.poCd = d.poCd \
                LEFT OUTER JOIN pos_cm e \
                ON a.siteCd = e.siteCd \
                AND a.posCd = e.posCd \
                AND e.state = 'R' \
                WHERE a.siteCd = '" + siteCd + "' \
                AND a.spa = '" + spa + "' \
                AND a.state = 'R' \
                AND b.state = 'R' \
                AND c.state = 'R' \
                AND d.state = 'R' \
            ) t \
            ORDER BY posCd;"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['posCd'] = tr[0]
        dic['posState'] = tr[1]
        dic['spa'] = tr[2]
        dic['posDate'] = tr[3]
        dic['posQty'] = tr[4]
        dic['dc'] = tr[5]
        dic['reseller'] = tr[6]
        dic['resellerNm'] = tr[7]
        dic['endUser'] = tr[8]
        dic['endUserNm'] = tr[9]
        dic['netPos'] = tr[10]
        dic['am'] = tr[11]
        dic['partner'] = tr[12]
        dic['jda'] = tr[13]
        dic['vertical'] = tr[14]
        dic['year'] = tr[15]
        dic['quater'] = tr[16]
        dic['week'] = tr[17]
        dic['poCd'] = tr[18]
        dic['lotNo'] = tr[19]
        dic['sn'] = tr[20]
        dic['cmCd'] = tr[21]
        dic['cmState'] = tr[22]
        dic['cmStateNm'] = tr[23]
        dic['cmDate'] = tr[24]
        dic['cmNo'] = tr[25]
        dic['rebAmt'] = tr[26]
        dic['remAmt'] = tr[27]
        dic['excRate'] = tr[28]
        dic['rebWonAmt'] = tr[29]
        dic['costWonAmt'] = tr[30]
        dic['goodsAmt'] = tr[31]
        dic['poNo'] = tr[32]
        dic['posStateNm'] = tr[33]

        data[index] = dic

    return simplejson.dumps({'sellHistSpa': data})


@main.route('/api/selStkStockLogistic', methods=['POST'])
def select_stk_stock_logistic():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    poNo = json_data.get('poNo')
    sn = json_data.get('sn')
    bl = json_data.get('bl')
    whCd = json_data.get('whCd')
    loc = json_data.get('loc')
    stkType = json_data.get('stkType')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT '0' AS chk, a.whCd, f.WhNm, \
                d.poType1, fn_get_codename('P0003', d.potype1) AS poType1Nm, \
                d.poType2, fn_get_codename('P0004', d.potype2) AS poType2Nm, \
                d.poType3, fn_get_codename('P0005', d.potype3) AS poType3Nm, \
                e.partKind, fn_get_codename('C0003', e.partKind) AS partKindNm, \
                e.partType3 AS partCategory, fn_get_codename('C0006', e.partType3) AS partCategoryNm, \
                a.partCd, e.partNm, \
                e.manufacturer, fn_get_custname(e.siteCd, e.manufacturer) AS manufacturerNm, \
                d.poNo, \
                b.inKind, fn_get_codename('W0001', b.inKind) AS inKindNm, \
                b.inType, fn_get_codename('W0002', b.inType) AS inTypeNm, \
                concat(left(b.inDate, 4), '-', SUBSTRING(b.inDate, 5, 2), '-', RIGHT(b.inDate, 2) ) AS inDate, \
                b.inNo, b.inCd, \
                IFNULL(SUM(b.inQty), 0.00) AS inQty, IFNULL(SUM(c.outQty), 0.00) AS outQty, \
                IFNULL(SUM(b.inQty), 0.00) - IFNULL(SUM(c.outQty), 0.00) AS stkQty, IFNULL(SUM(a.curQty), 0.00) AS curQty, \
                a.unit, fn_get_codename('S0005', a.unit) AS unitNm, \
                a.loc, g.minorNm as locNm, \
                b.inWarr, fn_get_codename('W0003', b.inWarr) AS inWarrNm, \
                b.partRank, fn_get_codename('W0004', b.inWarr) AS partRankNm, \
                b.bl, \
                a.stkType, fn_get_codename('W0023', a.stkType) AS stkTypeNm \
            FROM stk_lot a \
            INNER JOIN stk_in b \
            ON a.siteCd = b.siteCd \
            AND a.lotNo = b.lotNo \
            AND b.state = 'R' \
            LEFT OUTER JOIN stk_out c \
            ON a.siteCd = c.siteCd \
            AND a.lotNo = c.lotNo \
            AND c.state = 'R' \
            LEFT OUTER JOIN pur_order d \
            ON b.siteCd = d.siteCd \
            AND b.poCd = d.poCd \
            AND d.state = 'R' \
            LEFT OUTER JOIN mst_part e \
            ON a.siteCd = e.siteCd \
            AND a.partCd = e.partCd \
            LEFT OUTER JOIN mst_wh f \
            ON a.siteCd = f.siteCd \
            AND a.whCd = f.whCd \
            LEFT OUTER JOIN sys_minor g \
            ON g.majorCd = 'C0008' \
            AND a.loc = g.minorCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND b.inDate BETWEEN '" + fDate + "' AND '" + tDate + "' \
            AND a.state = 'R' "
    if partCd is not None:
        sql += " AND a.partCd = '" + partCd + "' "
    if partText is not None:
        sql += " AND ( a.partCd LIKE CONCAT('%', '" + partText + \
            "', '%') OR e.partNm LIKE CONCAT('%', '" + partText + "', '%') ) "
    if poNo is not None:
        sql += " AND d.poNo LIKE CONCAT('%', '" + poNo + "', '%') "
    if sn is not None:
        sql += " AND a.sn LIKE CONCAT('%', '" + sn + "', '%') "
    if bl is not None:
        sql += " AND b.bl LIKE CONCAT('%', '" + bl + "', '%') "
    if whCd is not None:
        sql += " AND a.whCd = '" + whCd + "' "
    if stkType is not None:
        sql += " AND a.stkType = '" + stkType + "' "
    if loc is not None:
        sql += " AND g.minorNm LIKE CONCAT('%', '" + loc + "', '%') "
    sql += "GROUP BY a.whCd, f.WhNm, a.stkType, d.poType1, d.poType2, d.poType3, a.partCd, e.manufacturer, \
                        d.poNo, b.inType, b.inDate, b.inNo, b.inCd, a.unit, a.loc, b.inWarr, b.partRank, b.bl \
            ORDER BY e.partNm, a.whCd, b.inDate, b.inNo, b.inCd; "

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['whCd'] = tr[1]
        dic['whNm'] = tr[2]
        dic['poType1'] = tr[3]
        dic['poType1Nm'] = tr[4]
        dic['poType2'] = tr[5]
        dic['poType2Nm'] = tr[6]
        dic['poType3'] = tr[7]
        dic['poType3Nm'] = tr[8]
        dic['partKind'] = tr[9]
        dic['partKindNm'] = tr[10]
        dic['partCategory'] = tr[11]
        dic['partCategoryNm'] = tr[12]
        dic['partCd'] = tr[13]
        dic['partNm'] = tr[14]
        dic['manufacturer'] = tr[15]
        dic['manufacturerNm'] = tr[16]
        dic['poNo'] = tr[17]
        dic['inKind'] = tr[18]
        dic['inKindNm'] = tr[19]
        dic['inType'] = tr[20]
        dic['inTypeNm'] = tr[21]
        dic['inDate'] = tr[22]
        dic['inNo'] = tr[23]
        dic['inCd'] = tr[24]
        dic['inQty'] = tr[25]
        dic['outQty'] = tr[26]
        dic['stkQty'] = tr[27]
        dic['curQty'] = tr[28]
        dic['unit'] = tr[29]
        dic['unitNm'] = tr[30]
        dic['loc'] = tr[31]
        dic['locNm'] = tr[32]
        dic['inWarr'] = tr[33]
        dic['inWarrNm'] = tr[34]
        dic['partRank'] = tr[35]
        dic['partRankNm'] = tr[36]
        dic['bl'] = tr[37]
        dic['stkType'] = tr[38]
        dic['stkTypeNm'] = tr[39]

        data[index] = dic

    return simplejson.dumps({'stock': data})


@main.route('/api/selStkStdPrice', methods=['POST'])
def select_stk_std_price():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    stdDate = json_data.get('stdDate')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    stkType = json_data.get('stkType')

    stkTypeSql1 = ""
    stkTypeSql2 = ""
    if stkType is not None and stkType != '':
        stkTypeSql1 = " AND stkType = '" + stkType + "' "
        stkTypeSql2 = " AND b.stkType = '" + stkType + "' "

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = "SELECT * \
            FROM ( \
                SELECT '0' AS chk, s.partCd, p.partNm, SUM(inAmt) AS inAmt, SUM(inQty) AS inQty, SUM(outQty) AS outQty, \
                    /*(SELECT SUM(docQty) FROM stk_lot x WHERE x.siteCd = t.siteCd AND x.partCd = t.partCd AND x.whCd = 'WH0001' AND x.state = 'R') AS lotQty,*/ \
                    ROUND(SUM(inAmt) / SUM(inQty), 2) AS stdUnitAmt, \
                    SUM(inQty) - SUM(outQty) AS stkQty, \
                    ROUND((SUM(inAmt) / SUM(inQty)) * (SUM(inQty) - SUM(outQty)), 2) AS stkAmt, \
                    SUM(inAmtZeroCnt) as inAmtZeroCnt, \
                    CASE WHEN SUM(inAmtZeroCnt) > 0 THEN CONCAT('입고단가가 입력되지 않은 SN이 (', ROUND(SUM(inAmtZeroCnt)), '건) 존재 합니다.') ELSE '' END AS note \
                FROM ( \
                    SELECT siteCd, partCd, SUM(inAmt) AS inAmt, SUM(inQty) AS inQty, SUM(CASE WHEN inAmt = 0 THEN 1 ELSE 0 END) AS inAmtZeroCnt,  0.00 outQty \
                    FROM stk_in \
                    WHERE siteCd = '" + siteCd + "' \
                    AND whCd = 'WH0001'" + stkTypeSql1 + " \
                    AND state = 'R' \
                    AND inDate <= '" + stdDate + "' \
                    /*AND inAmt > 0*/ \
                    GROUP BY partCd \
                    \
                    UNION all \
                    \
                    SELECT b.siteCd, b.partCd, 0.00 AS inAmt, 0.00 AS inQty, 0 inAmtZeroCnt, SUM(a.outQty) AS outQty \
                    FROM stk_out a \
                    INNER JOIN stk_lot b \
                    ON a.siteCd = b.siteCd \
                    AND a.lotNo = b.lotNo \
                    INNER JOIN stk_sell c \
                    ON a.siteCd = c.siteCd \
                    AND a.outCd = c.outCd \
                    AND a.outSeq = c.outSeq \
                    WHERE a.siteCd = '" + siteCd + "' \
                    AND a.whCd = 'WH0001'" + stkTypeSql2 + " \
                    AND a.sellYn = 'Y' \
                    AND a.state = 'R' \
                    AND b.state = 'R' \
                    AND c.state = 'R' \
                    AND c.sellDate <= '" + stdDate + "' \
                    GROUP BY b.siteCd, b.partCd \
                ) s \
                LEFT OUTER JOIN mst_part p \
                ON s.siteCd = p.siteCd \
                AND s.partCd = p.partCd \
                GROUP BY s.partCd \
            ) t \
            WHERE 1 = 1 "
    if partCd is not None:
        sql += " AND partCd = '" + partCd + "'"
    if partText is not None:
        sql += " AND ( partCd LIKE CONCAT('%', '" + partText + \
            "', '%') OR partNm LIKE CONCAT('%', '" + partText + "', '%') )"
    sql += " ORDER BY partNm; "

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['partCd'] = tr[1]
        dic['partNm'] = tr[2]
        dic['inAmt'] = tr[3]
        dic['inQty'] = tr[4]
        dic['outQty'] = tr[5]
        dic['stdUnitAmt'] = tr[6]
        dic['stkQty'] = tr[7]
        dic['stkAmt'] = tr[8]
        dic['inAmtZeroCnt'] = tr[9]
        dic['note'] = tr[10]

        data[index] = dic

    return simplejson.dumps({'stdPrice': data})


@main.route('/api/regStkStockReserve', methods=['POST'])
def insert_stk_stock_reserve():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    roCd = json_data.get('roCd')
    resvDate = json_data.get('resvDate')
    resvUser = json_data.get('resvUser')
    lotNo = json_data.get('lotNo')
    note = json_data.get('note')
    user = json_data.get('user')

    # check stk_lot
    lot = StkLot.query.filter_by(siteCd=siteCd, lotNo=lotNo, state='R').first()
    if lot is None:
        return jsonify({
            'result': {
                'code': 8605,
                'msg': '재고가 존재하지 않습니다.'
            }
        })
    else:
        if lot.curQty <= 0:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고가 존재하지 않습니다.'
                }
            })

    # check pre_stk_reserve_out
    pre_roInfoes = StkReserveOut.query.filter_by(
        siteCd=siteCd, lotNo=lotNo, state='R')

    # check stk_reserve_out
    if not roCd:
        findKey_roCd = 'RO' + datetime.now().strftime('%y%m%d')
        seq_roCd = 1
        sel_roCd = StkReserveOut.query.filter(StkReserveOut.siteCd == siteCd, StkReserveOut.roCd.like(
            findKey_roCd + '%')).order_by(StkReserveOut.roCd.desc()).first()
        if sel_roCd is not None:
            seq_roCd = int(sel_roCd.roCd[-6:]) + 1
        roCd = findKey_roCd + (6 - len(str(seq_roCd))) * '0' + str(seq_roCd)

    roSeq = 1
    sel_roSeq = StkReserveOut.query.filter(
        StkReserveOut.siteCd == siteCd, StkReserveOut.roCd == roCd).order_by(StkReserveOut.roSeq.desc()).first()
    if sel_roSeq is not None:
        roSeq = int(sel_roSeq.roSeq) + 1

    # pre_stk_reserve_out update
    if pre_roInfoes is not None:
        pre_roInfoes.update(
            {StkReserveOut.state: 'N', StkReserveOut.modUser: user, StkReserveOut.modDate: datetime.now()})

    # stk_reserve_out insert
    stkReserveOut = StkReserveOut(
        siteCd=siteCd,
        roCd=roCd,
        roSeq=roSeq,
        resvDate=resvDate,
        resvUser=resvUser,
        lotNo=lotNo,
        note=note,
        state='R',
        regUser=user,
        regDate=datetime.now(),
        modUser=None,
        modDate=None)

    db.session.add(stkReserveOut)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkReserveOut': stkReserveOut.to_json()
    })


@main.route('/api/updStkStockReserve', methods=['POST'])
def update_stk_stock_reserve():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    roCd = json_data.get('roCd')
    roSeq = json_data.get('roSeq')
    resvDate = json_data.get('resvDate')
    resvUser = json_data.get('resvUser')
    lotNo = json_data.get('lotNo')
    state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')

    # check stk_reserve_out
    data = StkReserveOut.query.filter_by(
        siteCd=siteCd, roCd=roCd, roSeq=roSeq).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        data.resvDate = resvDate
        data.resvUer = resvUser
        data.lotNo = lotNo
        data.note = note
    else:
        data.state = state

    data.modUser = user
    data.modDate = datetime.now()

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkReserveOut': data.to_json()
    })


@main.route('/api/selStkOutReq', methods=['POST'])
def select_stk_out_req():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    custCd = json_data.get('custCd')
    custText = json_data.get('custText')
    reqState = json_data.get('reqState')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT '0' AS chk, \
                    a.reqCd, \
                    a.reqState, \
                    fn_get_codename('W0013', a.reqState) AS reqStateNm, \
                    CONCAT(LEFT(a.reqDate, 4), '-', SUBSTRING(a.reqDate, 5, 2), '-', RIGHT(a.reqDate, 2)) AS reqDate, \
                    a.reqUser, \
                    a.sender, \
                    a.senderPhone, \
                    a.senderFax, \
                    a.shipCustCd, \
                    c.custNm AS shipCustNm, \
                    a.shipContact, \
                    a.shipPhone, \
                    a.shipAddress, \
                    a.receiver, \
                    a.note, \
                    b.reqSeq, \
                    b.partCd, \
                    fn_get_partname(b.siteCd, b.partCd) AS partNm, \
                    b.qty, \
                    b.unit, \
                    fn_get_codename('S0005', b.unit) AS unitNm, \
                    b.note AS dtlNote \
            FROM stk_out_req a \
            INNER JOIN stk_out_req_dtl b \
            ON a.siteCd = b.siteCd \
            AND a.reqCd = b.reqCd \
            AND a.state = 'R' \
            AND b.state = 'R' \
            LEFT OUTER JOIN mst_cust c \
            ON a.siteCd = c.siteCd \
            AND a.shipCustCd = c.custCd \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.reqDate BETWEEN '" + fDate + "' AND '" + tDate + "' "
    if custCd is not None:
        sql += " AND a.shipCustCd = '" + custCd + "' "
    if custText is not None:
        sql += " AND ( a.shipCustCd LIKE CONCAT('%', '" + custText + \
            "', '%') OR c.custNm LIKE CONCAT('%', '" + custText + "', '%') ) "
    if reqState is not None:
        sql += " AND a.reqState = '" + reqState + "' "
    sql += " ORDER BY a.reqCd DESC, b.reqSeq ASC"

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['reqCd'] = tr[1]
        dic['reqState'] = tr[2]
        dic['reqStateNm'] = tr[3]
        dic['reqDate'] = tr[4]
        dic['reqUser'] = tr[5]
        dic['sender'] = tr[6]
        dic['senderPhone'] = tr[7]
        dic['senderFax'] = tr[8]
        dic['shipCustCd'] = tr[9]
        dic['shipCustNm'] = tr[10]
        dic['shipContact'] = tr[11]
        dic['shipPhone'] = tr[12]
        dic['shipAddress'] = tr[13]
        dic['receiver'] = tr[14]
        dic['note'] = tr[15]
        dic['reqSeq'] = tr[16]
        dic['partCd'] = tr[17]
        dic['partNm'] = tr[18]
        dic['qty'] = tr[19]
        dic['unit'] = tr[20]
        dic['unitNm'] = tr[21]
        dic['dtlNote'] = tr[22]

        data[index] = dic

    return simplejson.dumps({'stkOutReq': data})


@main.route('/api/insStkOutReq', methods=['POST'])
def insert_stk_out_req():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqDate = json_data.get('reqDate')
    reqUser = json_data.get('reqUser')
    sender = json_data.get('sender')
    senderPhone = json_data.get('senderPhone')
    senderFax = json_data.get('senderFax')
    shipCustCd = json_data.get('shipCustCd')
    shipContact = json_data.get('shipContact')
    shipPhone = json_data.get('shipPhone')
    shipAddress = json_data.get('shipAddress')
    receiver = json_data.get('receiver')
    note = json_data.get('note')
    user = json_data.get('user')

    # check stk_out_req
    findKey_reqCd = 'RQ' + reqDate[-6:]
    seq_reqCd = 1
    sel_reqCd = StkOutReq.query.filter(StkOutReq.siteCd == siteCd, StkOutReq.reqCd.like(
        findKey_reqCd + '%')).order_by(StkOutReq.reqCd.desc()).first()
    if sel_reqCd is not None:
        seq_reqCd = int(sel_reqCd.reqCd[-6:]) + 1
    reqCd = findKey_reqCd + (6 - len(str(seq_reqCd))) * '0' + str(seq_reqCd)

    # stk_out_req insert
    stkOutReq = StkOutReq(siteCd=siteCd,
                          reqCd=reqCd,
                          reqDate=reqDate,
                          reqState='A',
                          reqUser=reqUser,
                          sender=sender,
                          senderPhone=senderPhone,
                          senderFax=senderFax,
                          shipCustCd=shipCustCd,
                          shipContact=shipContact,
                          shipPhone=shipPhone,
                          shipAddress=shipAddress,
                          receiver=receiver,
                          note=note,
                          state='R',
                          regUser=user,
                          regDate=datetime.now(),
                          modUser=None,
                          modDate=None)

    db.session.add(stkOutReq)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutReq': stkOutReq.to_json()
    })


@main.route('/api/updStkOutReq', methods=['POST'])
def update_stk_out_req():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')
    reqState = json_data.get('reqState')
    reqDate = json_data.get('reqDate')
    reqUser = json_data.get('reqUser')
    sender = json_data.get('sender')
    senderPhone = json_data.get('senderPhone')
    senderFax = json_data.get('senderFax')
    shipCustCd = json_data.get('shipCustCd')
    shipContact = json_data.get('shipContact')
    shipPhone = json_data.get('shipPhone')
    shipAddress = json_data.get('shipAddress')
    receiver = json_data.get('receiver')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    # check stk_out_req
    data = StkOutReq.query.filter_by(siteCd=siteCd, reqCd=reqCd).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        if reqState != 'B':
            data.reqDate = reqDate
            data.reqUser = reqUser
            data.sender = sender
            data.senderPhone = senderPhone
            data.senderFax = senderFax
            data.shipCustCd = shipCustCd
            data.shipContact = shipContact
            data.shipPhone = shipPhone
            data.shipAddress = shipAddress
            data.receiver = receiver
            data.note = note
        else:
            data.reqState = reqState
    else:
        data.state = state

    data.modDate = datetime.now()
    data.modUser = user

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutReq': data.to_json()
    })


@main.route('/api/insStkOutReqDtl', methods=['POST'])
def insert_stk_out_req_dtl():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')
    reqSeq = json_data.get('reqSeq')
    partCd = json_data.get('partCd')
    qty = json_data.get('qty')
    unit = json_data.get('unit')
    note = json_data.get('note')
    user = json_data.get('user')

    # stk_outReq check
    data = StkOutReqDtl.query.filter_by(
        siteCd=siteCd, reqCd=reqCd, reqSeq=reqSeq).first()

    if data is None:
        # stk_out_req insert
        stkOutReqDtl = StkOutReqDtl(siteCd=siteCd,
                                    reqCd=reqCd,
                                    reqSeq=reqSeq,
                                    partCd=partCd,
                                    qty=qty,
                                    unit=unit,
                                    note=note,
                                    state='R',
                                    regUser=user,
                                    regDate=datetime.now(),
                                    modUser=None,
                                    modDate=None)
        db.session.add(stkOutReqDtl)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg': gettext('1000')
            },
            'stkOutReqDtl': stkOutReqDtl.to_json()
        })
    else:
        data.partCd = partCd
        data.qty = qty
        data.unit = unit
        data.note = note
        data.state = 'R'
        data.modUser = user
        data.modDate = datetime.now()
        db.session.add(data)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg': gettext('1000')
            },
            'stkOutReqDtl': data.to_json()
        })


@main.route('/api/updStkOutReqDtl', methods=['POST'])
def update_stk_out_req_dtl():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')
    reqSeq = json_data.get('reqSeq')
    partCd = json_data.get('partCd')
    qty = json_data.get('qty')
    unit = json_data.get('unit')
    note = json_data.get('note')
    state = json_data.get('state')
    user = json_data.get('user')

    # check stk_out_req_dtl
    data = StkOutReqDtl.query.filter_by(
        siteCd=siteCd, reqCd=reqCd, reqSeq=reqSeq).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        data.partCd = partCd
        data.qty = qty
        data.unit = unit
        data.note = note
    else:
        data.state = state

    data.modDate = datetime.now()
    data.modUser = user

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutReqDtl': data.to_json()
    })


@main.route('/api/selStkOutReqSn', methods=['POST'])
def select_stk_out_req_sn():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = " SELECT '1' AS chk, \
                    a.reqCd, \
                    a.snSeq, \
                    a.poCd, \
                    a.poNo, \
                    a.partCd, \
                    e.partNm, \
                    a.lotNo, \
                    a.sn, \
                    a.qty, \
                    a.unit, \
                    a.loc, \
                    a.awb, \
                    a.note \
            FROM stk_out_req_sn a \
            INNER JOIN stk_out_req b \
            ON a.siteCd = b.siteCd \
            AND a.reqCd = b.reqCd \
            AND b.state = 'R' \
            LEFT OUTER JOIN stk_lot c \
            ON a.siteCd = c.siteCd \
            AND a.lotNo = c.lotNo \
            AND c.state = 'R' \
            LEFT OUTER JOIN pur_order d \
            ON a.siteCd = d.siteCd \
            AND a.poCd = d.poCd \
            AND d.state = 'R' \
            LEFT OUTER JOIN mst_part e \
            ON a.siteCd = e.siteCd \
            AND a.partCd = e.partCd \
            AND e.state = 'R' \
            WHERE a.siteCd = '" + siteCd + "' \
            AND a.reqCd = '" + reqCd + "' \
            AND a.state = 'R' \
            ORDER BY a.snSeq "

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['chk'] = tr[0]
        dic['reqCd'] = tr[1]
        dic['snSeq'] = tr[2]
        dic['poCd'] = tr[3]
        dic['poNo'] = tr[4]
        dic['partCd'] = tr[5]
        dic['partNm'] = tr[6]
        dic['lotNo'] = tr[7]
        dic['sn'] = tr[8]
        dic['qty'] = tr[9]
        dic['unit'] = tr[10]
        dic['loc'] = tr[11]
        dic['awb'] = tr[12]
        dic['note'] = tr[13]

        data[index] = dic

    return simplejson.dumps({'stkOutReqSn': data})


@main.route('/api/insStkOutReqSn', methods=['POST'])
def insert_stk_out_req_sn():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')
    snSeq = json_data.get('snSeq')
    poCd = json_data.get('poCd')
    poNo = json_data.get('poNo')
    partCd = json_data.get('partCd')
    lotNo = json_data.get('lotNo')
    sn = json_data.get('sn')
    qty = json_data.get('qty')
    unit = json_data.get('unit')
    loc = json_data.get('loc')
    awb = json_data.get('awb')
    note = json_data.get('note')
    user = json_data.get('user')

    # stk_outReq check
    data = StkOutReqSn.query.filter_by(
        siteCd=siteCd, reqCd=reqCd, snSeq=snSeq).first()

    if data is None:
        # stk_out_req insert
        stkOutReqSn = StkOutReqSn(siteCd=siteCd,
                                  reqCd=reqCd,
                                  snSeq=snSeq,
                                  poCd=poCd,
                                  poNo=poNo,
                                  partCd=partCd,
                                  lotNo=lotNo,
                                  sn=sn,
                                  qty=qty,
                                  unit=unit,
                                  loc=loc,
                                  awb=awb,
                                  note=note,
                                  state='R',
                                  regUser=user,
                                  regDate=datetime.now(),
                                  modUser=None,
                                  modDate=None)
        db.session.add(stkOutReqSn)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg': gettext('1000')
            },
            'stkOutReqSn': stkOutReqSn.to_json()
        })
    else:
        data.poCd = poCd
        data.poNo = poNo
        data.partCd = partCd
        data.lotNo = lotNo
        data.sn = sn
        data.qty = qty
        data.unit = unit
        data.loc = loc
        data.awb = awb
        data.note = note
        data.state = 'R'
        data.modUser = user
        data.modDate = datetime.now()
        db.session.add(data)
        db.session.commit()

        return jsonify({
            'result': {
                'code': 1000,
                'msg': gettext('1000')
            },
            'stkOutReqSn': data.to_json()
        })


@main.route('/api/updStkOutReqSn', methods=['POST'])
def update_stk_out_req_sn():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    reqCd = json_data.get('reqCd')
    snSeq = json_data.get('snSeq')
    poCd = json_data.get('poCd')
    poNo = json_data.get('poNo')
    partCd = json_data.get('partCd')
    lotNo = json_data.get('lotNo')
    sn = json_data.get('sn')
    qty = json_data.get('qty')
    unit = json_data.get('unit')
    loc = json_data.get('loc')
    awb = json_data.get('awb')
    note = json_data.get('note')
    user = json_data.get('user')
    state = json_data.get('state')

    # check stk_out_req_dtl
    data = StkOutReqSn.query.filter_by(
        siteCd=siteCd, reqCd=reqCd, snSeq=snSeq).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        data.poCd = poCd
        data.poNo = poNo
        data.partCd = partCd
        data.lotNo = lotNo
        data.sn = sn
        data.qty = qty
        data.unit = unit
        data.loc = loc
        data.awb = awb
        data.note = note
    else:
        data.state = state

    data.modDate = datetime.now()
    data.modUser = user

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutReqSn': data.to_json()
    })


@main.route('/api/insStkStockOutEtc', methods=['POST'])
def insert_stk_out_etc():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    outEtcCd = json_data.get('outEtcCd')
    outEtcDate = json_data.get('outEtcDate')
    outEtcNo = json_data.get('outEtcNo')
    poCd = json_data.get('poCd')
    outEtcRemark = json_data.get('outEtcRemark')
    outEtcNote = json_data.get('outEtcNote')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    user = json_data.get('user')

    if outCd:
        # check stk_out
        out = StkOut.query.filter_by(
            siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
        if out is None:
            return jsonify({
                'result': {
                    'code': 8606,
                    'msg': '출고정보가 존재하지 않습니다.'
                }
            })

        lot = StkLot.query.filter_by(
            siteCd=siteCd, lotNo=out.lotNo, state='R').first()
        if lot is None:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고정보가 존재하지 않습니다.'
                }
            })

    # check stk_out_etc
    if not outEtcCd:
        findKey_outEtcCd = 'ET' + outEtcDate[-6:]
        seq_outEtcCd = 1
        sel_outEtcCd = StkOutEtc.query.filter(StkOutEtc.siteCd == siteCd, StkOutEtc.outEtcCd.like(
            findKey_outEtcCd + '%')).order_by(StkOutEtc.outEtcCd.desc()).first()
        if sel_outEtcCd is not None:
            seq_outEtcCd = int(sel_outEtcCd.outEtcCd[-6:]) + 1
        outEtcCd = findKey_outEtcCd + \
            (6 - len(str(seq_outEtcCd))) * '0' + str(seq_outEtcCd)

    outEtcSeq = 1

    sel_outEtcSeq = StkOutEtc.query.filter(
        StkOutEtc.siteCd == siteCd, StkOutEtc.outEtcCd == outEtcCd).order_by(StkOutEtc.outEtcSeq.desc()).first()
    if sel_outEtcSeq is not None:
        outEtcSeq = int(sel_outEtcSeq.outEtcSeq) + 1

    # stk_out_etc insert
    stkOutEtc = StkOutEtc(siteCd=siteCd,
                          outEtcCd=outEtcCd,
                          outEtcSeq=outEtcSeq,
                          outEtcNo=outEtcNo,
                          outEtcDate=outEtcDate,
                          poCd=poCd,
                          outCd=outCd,
                          outSeq=outSeq,
                          remark=outEtcRemark,
                          note=outEtcNote,
                          state='R',
                          regUser=user,
                          regDate=datetime.now(),
                          modUser=None,
                          modDate=None)
    if outCd:
        # stk_lot update
        lot.docQty = int(lot.docQty) - int(out.outQty)
        lot.modUser = user
        lot.modDate = datetime.now()

        # stk_out update
        out.outKind = 'E'
        out.modUser = user
        out.modDate = datetime.now()

    db.session.add(stkOutEtc)

    if outCd:
        db.session.add(lot)
        db.session.add(out)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutEtc': stkOutEtc.to_json()
    })


@main.route('/api/updStkStockOutEtc', methods=['POST'])
def update_stk_out_etc():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    outEtcCd = json_data.get('outEtcCd')
    outEtcSeq = json_data.get('outEtcSeq')
    outEtcDate = json_data.get('outEtcDate')
    outEtcNo = json_data.get('outEtcNo')
    poCd = json_data.get('poCd')
    outEtcRemark = json_data.get('outEtcRemark')
    outEtcNote = json_data.get('outEtcNote')
    outCd = json_data.get('outCd')
    outSeq = json_data.get('outSeq')
    user = json_data.get('user')
    state = json_data.get('state')

    # check stk_out_etc
    data = StkOutEtc.query.filter_by(
        siteCd=siteCd, outEtcCd=outEtcCd, outEtcSeq=outEtcSeq).first()
    if data is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg': gettext('8504')
            }
        })

    if state != 'D':
        data.outEtcDate = outEtcDate
        data.outEtcNo = outEtcNo
        data.poCd = poCd
        data.remark = outEtcRemark
        data.note = outEtcNote
    else:
        # check stk_out
        out = StkOut.query.filter_by(
            siteCd=siteCd, outCd=outCd, outSeq=outSeq, state='R').first()
        if out is None:
            return jsonify({
                'result': {
                    'code': 8606,
                    'msg': '출고정보가 존재하지 않습니다.'
                }
            })

        lot = StkLot.query.filter_by(
            siteCd=siteCd, lotNo=out.lotNo, state='R').first()
        if lot is None:
            return jsonify({
                'result': {
                    'code': 8605,
                    'msg': '재고정보가 존재하지 않습니다.'
                }
            })

        data.state = state
        out.outKind = 'G'
        out.modDate = datetime.now()
        out.modUser = user
        lot.docQty = lot.docQty + out.outQty
        lot.modDate = datetime.now()
        lot.modUser = user

        db.session.add(out)
        db.session.add(lot)

    data.modDate = datetime.now()
    data.modUser = user

    db.session.add(data)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg': gettext('1000')
        },
        'stkOutReqDtl': data.to_json()
    })
