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
# from app.main.awsutil import awsS3

from . import main

@main.route('/api/selAnlStockInout', methods=['POST'])
def select_anl_stock_inout():
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')    
    fDate = json_data.get('fDate')
    tDate = json_data.get('tDate')
    stkType = json_data.get('stkType')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    stkMethod = json_data.get('stkMethod')
    
    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    # sql = "SELECT t.partCd, t.partNm, \
    #             CONCAT(left(t.inDate, 4), '-', SUBSTRING(t.inDate, 5, 2), '-', RIGHT(t.inDate, 2) ) AS inDate, \
    #             preInQty, preInAmt, preOutQty, preOutAmt, \
    #             preInQty - preOutQty AS preStkQty, preInAmt - preOutAmt AS preStkAmt, \
    #             gerInQty, gerInAmt, etcInQty, etcInAmt, \
    #             gerOutQty, gerOutAmt, etcOutQty, etcOutAmt, \
    #             gerInQty + etcInQty AS totInQty, \
    #             gerInAmt + etcInAmt AS totInAmt, \
    #             gerOutQty + etcOutQty AS totOutQty, \
    #             gerOutAmt + etcOutAmt AS totOutAmt, \
    #             preInQty - preOutQty + gerInQty + etcInQty - gerOutQty - etcOutQty AS totStkQty, \
    #             preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt AS totStkAmt, \
    #             CASE WHEN firStkAmt > 0 THEN firStkAmt ELSE preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt END AS tarStkAmt, \
    #             TIMESTAMPDIFF(DAY, t.inDate, '" + tDate + "') AS agingDay, \
    #             CASE WHEN TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') >= 5 THEN 5 ELSE TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') END AS agingYear, \
    #             CONVERT((CASE WHEN TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') >= 5 THEN 5 ELSE TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') END * \
    #                 CASE WHEN firStkAmt > 0 THEN firStkAmt ELSE (preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt) END) / 5, DECIMAL(14,2)) AS lossAmt, \
    #             IFNULL(firStkAmt, 0) AS firStkAmt, \
    #             IFNULL(firStkAmt, 0) - (preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt) AS adjStkAmt, \
    #             (CONVERT((CASE WHEN TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') >= 5 THEN 5 ELSE TIMESTAMPDIFF(YEAR, t.inDate, '" + tDate + "') END * \
    #                 CASE WHEN firStkAmt > 0 THEN firStkAmt ELSE (preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt) END) / 5, DECIMAL(14,2))) \
    #                 - (IFNULL(firStkAmt, 0) - (preInAmt - preOutAmt + gerInAmt + etcInAmt - gerOutAmt - etcOutAmt)) AS lossMinusAdjAmt \
    #     FROM ( \
    #     SELECT partCd, partNm, inDate, \
    #             SUM(case when inDate < '" + fDate + "' then IFNULL(inQty, 0) ELSE 0 END) AS  preInQty, \
    #             SUM(case when inDate < '" + fDate + "' then IFNULL(goodsAmt, 0) ELSE 0 END) AS preInAmt, \
    #             SUM(case when outDate < '" + fDate + "' then IFNULL(outQty, 0) ELSE 0 END) AS preOutQty, \
    #             SUM(case when outDate < '" + fDate + "' then IFNULL(goodsAmt, 0) ELSE 0 END) AS preOutAmt, \
    #             SUM(case when inDate >= '" + fDate + "' then case when inKind = 'G' then IFNULL(inQty, 0) ELSE 0 END ELSE 0 END) AS gerInQty, \
    #             SUM(case when inDate >= '" + fDate + "' then case when inKind = 'G' then CONVERT(IFNULL(goodsAmt, 0) * IFNULL(inQty, 0), DECIMAL(14,2)) ELSE 0 END ELSE 0 END) AS gerInAmt, \
    #             SUM(case when inDate >= '" + fDate + "' then case when inKind = 'E' then IFNULL(inQty, 0) ELSE 0 END ELSE 0 END) AS etcInQty, \
    #             SUM(case when inDate >= '" + fDate + "' then case when inKind = 'E' then CONVERT(IFNULL(goodsAmt, 0) * IFNULL(inQty, 0), DECIMAL(14,2)) ELSE 0 END ELSE 0 END) AS etcInAmt, \
    #             SUM(case when outDate >= '" + fDate + "' then case when outKind = 'G' then IFNULL(outQty, 0) ELSE 0 END ELSE 0 END) AS gerOutQty, \
    #             SUM(case when outDate >= '" + fDate + "' then case when outKind = 'G' then CONVERT(IFNULL(goodsAmt, 0) * IFNULL(outQty, 0), DECIMAL(14,2)) ELSE 0 END ELSE 0 END) AS gerOutAmt, \
    #             SUM(case when outDate >= '" + fDate + "' then case when outKind = 'E' then IFNULL(outQty, 0) ELSE 0 END ELSE 0 END) AS etcOutQty, \
    #             SUM(case when outDate >= '" + fDate + "' then case when outKind = 'E' then CONVERT(IFNULL(goodsAmt, 0) * IFNULL(outQty, 0), DECIMAL(14,2)) ELSE 0 END ELSE 0 END) AS etcOutAmt \
    #     FROM ( \
    #         SELECT   x.siteCd, x.inCd, x.inSeq, x.lotNo, \
    #                     x.partCd, p.partNm, x.rank, x.inDate, x.inKind, x.inQty, x.inAmt, x.rebWonAmt, x.goodsAmt, \
    #                     y.outCd, y.outSeq, \
    #                     y.outDate, y.outKind, y.sellYn, y.outQty \
    #         FROM ( \
    #             SELECT r1.*, \
    #                     CASE @grp WHEN CONCAT(siteCd, partCd) THEN @rank := @rank + 1 ELSE @rank := 1 END AS rank, \
    #                 @grp := CONCAT(siteCd, partCd) AS grp \
    #             FROM ( \
    #                 SELECT a.siteCd, a.inCd, a.inSeq, a.lotNo, a.partCd, a.inDate, a.inQty, a.inAmt, \
    #                         b.rebWonAmt, CASE WHEN IFNULL(a.inAmt, 0) - IFNULL(b.rebWonAmt, 0) < 0 then 0 ELSE IFNULL(a.inAmt, 0) - IFNULL(b.rebWonAmt, 0) end AS goodsAmt, \
    #                         a.inKind \
    #                 FROM stk_in a \
    #                 LEFT OUTER JOIN ( \
    #                     SELECT a2.*, a1.poCd, a1.lotNo \
    #                     FROM pos_pos a1 \
    #                     INNER JOIN pos_cm a2 \
    #                     ON a1.siteCd = a2.siteCd \
    #                     AND a1.posCd = a2.posCd \
    #                     AND a1.state = 'R' \
    #                     AND a2.state = 'R' \
    #                 ) b \
    #                 ON a.siteCd = b.siteCd \
    #                 AND a.poCd = b.poCd \
    #                 AND a.lotNo = b.lotNo \
    #                 WHERE a.siteCd = '" + siteCd + "' \
    #                 AND a.inDate <= '" + tDate + "' \
    #                 AND a.whCd = 'WH0001' \
    #                 AND a.stkType = '" + stkType + "' \
    #                 AND a.state = 'R' \
    #             ) r1, (SELECT @grp := '', @rank := 0) r2 \
    #             ORDER BY siteCd, partCd, inDate, inCd, inSeq \
    #         ) x \
    #         LEFT OUTER JOIN ( \
    #             SELECT r1.*, \
    #                     CASE @grp WHEN concat(siteCd, partCd) THEN @rank := @rank + 1 ELSE @rank := 1 END AS rank, \
    #                 @grp := concat(siteCd, partCd) AS grp \
    #             FROM ( \
    #                 SELECT a.siteCd, a.outCd, a.outSeq, b.partCd, case when c.sellCd IS NULL then a.outDate ELSE c.sellDate END AS outDate, a.outQty, a.outKind, a.sellYn, b.lotNo \
    #                 FROM stk_out a \
    #                 INNER JOIN stk_lot b \
    #                 ON a.siteCd = b.siteCd \
    #                 AND a.lotNo = b.lotNo \
    #                 LEFT OUTER JOIN stk_sell c \
    #                 ON a.siteCd = c.siteCd \
    #                 AND a.outCd = c.outCd \
    #                 AND a.outSeq = c.outSeq \
    #                 AND c.state = 'R' \
    #                 WHERE a.siteCd = '" + siteCd + "' \
    #                 AND a.outDate <= '" + tDate + "' \
    #                 AND ((a.outKind = 'G' AND a.sellYn = 'Y') OR (a.outKind = 'E')) \
    #                 AND b.stkType = '" + stkType + "' \
    #                 AND a.state = 'R' \
    #                 AND b.state = 'R' \
    #             ) r1, (SELECT @grp := '', @rank := 0) r2 \
    #             ORDER BY partCd, outDate, outCd, outSeq \
    #         ) y "

    # if stkMethod == "FIFO":
    #     sql += " \
    #         ON x.siteCd = y.siteCd \
    #         AND x.partCd = y.partCd \
    #         AND x.rank = y.rank "
    # else:
    #     sql += " \
    #         ON x.siteCd = y.siteCd \
    #         AND x.lotNo = y.lotNo "
        
    # sql += " \
    #         LEFT OUTER JOIN mst_part p \
    #         ON x.siteCd = p.siteCd \
    #         AND x.partCd = p.partCd \
    #         WHERE 1 = 1 "

    # if partCd is not None:
    #     sql += " AND x.partCd = '" + partCd + "'"
    # if partText is not None:
    #     sql += " AND ( x.partCd LIKE CONCAT('%', '" + partText + "', '%') OR p.partNm LIKE CONCAT('%', '" + partText + "', '%') ) " 
    
    # sql += " \
    #         ) t1 \
    #         GROUP BY partCd, inDate \
    #     ) t \
    #     LEFT OUTER JOIN ( \
    #         SELECT siteCd, partCd, inDate, sum(stkAmt) as firStkAmt \
    #         FROM mst_std_stock \
    #         WHERE siteCd = '" + siteCd + "' \
    #         AND stkType = '" + stkType + "' \
    #         AND state = 'R' \
    #         GROUP BY partCd, inDate \
    #     ) z \
    #     ON t.partCd = z.partCd \
    #     AND t.inDate = z.inDate \
    #     ORDER BY t.partNm, t.inDate \
    # ;"
    
    # curs.execute(sql)

    args = [siteCd, stkType, fDate, tDate, partCd, partText, stkMethod]
    curs.callproc('proc_selAnlStockInOut', args)

    data = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(data):
        dic = dict()
        dic['partCd'] = tr[0]
        dic['partNm'] = tr[1]
        dic['inDate'] = tr[2]
        dic['preInQty'] = tr[3]
        dic['preInAmt'] = tr[4]
        dic['preOutQty'] = tr[5]
        dic['preOutAmt'] = tr[6]
        dic['preStkQty'] = tr[7]
        dic['preStkAmt'] = tr[8]
        dic['gerInQty'] = tr[9]
        dic['gerInAmt'] = tr[10]
        dic['etcInQty'] = tr[11]
        dic['etcInAmt'] = tr[12]
        dic['gerOutQty'] = tr[13]
        dic['gerOutAmt'] = tr[14]
        dic['etcOutQty'] = tr[15]
        dic['etcOutAmt'] = tr[16]
        dic['totInQty'] = tr[17]
        dic['totInAmt'] = tr[18]
        dic['totOutQty'] = tr[19]
        dic['totOutAmt'] = tr[20]
        dic['totStkQty'] = tr[21]
        dic['totStkAmt'] = tr[22]
        dic['tarStkAmt'] = tr[23]
        dic['agingDay'] = tr[24]
        dic['agingYear'] = tr[25]
        dic['lossAmt'] = tr[26]
        dic['firStkAmt'] = tr[27]
        dic['adjStkAmt'] = tr[28]
        dic['lossMinusAdjAmt'] = tr[29]

        data[index] = dic

    # return jsonify({'stock': data})    
    return simplejson.dumps({'inout': data})

