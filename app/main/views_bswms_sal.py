# -- coding: utf-8 -- 

import datetime
import os

import config
import pymysql
from app import db, get_locale
from app.main.awsutil import awsS3
from app.main.cipherutil import CipherAgent
from app.models_bswms import *
#from app.models_bswms3 import *
from dateutil import parser
from flask import app, current_app, flash, json, jsonify, request, url_for
from flask_babel import gettext
from sqlalchemy import func, literal
from sqlalchemy.orm import aliased
from werkzeug.utils import redirect, secure_filename


from . import main


# LYK_DEMO

# Demo 조회
@main.route('/api/selSalDemo', methods=['POST'])
def select_sal_demo():    
    # json_data = request.get_json()
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')
    partText = json_data.get('partText')
    sn = json_data.get('sn')
    demoState = json_data.get('demoState')
    start = json_data.get('start')
    end = json_data.get('end')
    rentUser = json_data.get('rentUser')
    rentCust = json_data.get('rentCust')
    rentCustText = json_data.get('rentCustText')
    # chkPartCd = json_data.get('chkPartCd')
    # chkRentCust = json_data.get('chkRentCust')
    state = 'R'
    print("JSON = ",json_data)
   
    search_query = "AND a.siteCd = '{siteCd}'".format_map({'siteCd':siteCd})
    if demoState != '':
        search_query += "AND a.demoState = '{demoState}'".format_map({'demoState':demoState})
    if partCd != '':
        search_query += "AND a.partCd = '{partCd}'".format_map({'partCd':partCd})
    elif partText != '':
        search_query += "AND (a.partCd LIKE CONCAT('%','{partText}','%')) OR b.partNm LIKE CONCAT('%', '{partText}', '%')".format_map({'partText':partText})
    
    if rentCust != '':
        search_query += "AND c.rentCust = '{rentCust}'".format_map({'rentCust':rentCust})
    elif rentCustText != '':
        search_query += "AND (c.rentCust LIKE CONCAT('%', '{rentCustText}', '%') OR d.custNm LIKE CONCAT ('%', '{rentCustText}', '%'))".format_map({'rentCustText': rentCustText})
    if sn != '':
        search_query += "AND a.sn LIKE CONCAT('%', '{sn}', '%')".format_map({'sn':sn})
    if rentUser != '':
        search_query += "AND c.rentUser LIKE CONCAT('%', '{rentUser}', '%')".format_map({'rentUser':rentUser})
    
    if start != '' and end != '':
        search_query += "AND a.indate BETWEEN '{start}' AND  '{end}'".format_map({'start': start, 'end':end})
    

    print("SEARCH_QUERY = ", search_query)
    

    conn = pymysql.connect(host=db.engine.url.host,

                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)
    
    curs = conn.cursor()

    sql = """ 	
        SELECT a.*, 
            fn_get_codename('S0004',a.demoState) AS demoStateNm,
            b.partNm,
            b.partType3, fn_get_codename('C0006', b.partType3) AS partType3Nm,
            c.rentUser,
            c.rentDate,
            c.rentCust, fn_get_custname(a.siteCd, c.rentCust) AS rentCustNm,
            c.rentManager,
            c.phone,
            c.address,
            c.estRetDate,
            c.rcvDate,
            c.rcvUser,
            c.rcvYN,
            c.demoSeq ,
            d.custNm,
            e.rdCd,
            e.rdSeq,
            e.resvDate,
            e.resvUser,
            e.note as resvNote
        FROM sal_demo AS a
        INNER JOIN mst_part AS b
        ON a.partCd = b.partCd
        AND a.siteCd = b.siteCd
        AND a.state = 'R'
        AND b.state = 'R'
        
        LEFT JOIN sal_demo_rent AS c
        ON c.siteCd = a.siteCd
        AND c.demoCd = a.demoCd
        AND c.demoState = a.demoState
        AND c.state = 'R'
        AND c.rcvYN = 'N'

        LEFT JOIN mst_cust AS d
        ON a.siteCd = d.siteCd
        AND c.rentCust = d.custCd
        AND d.state = 'R'

        LEFT OUTER JOIN sal_reserve_demo e
        ON a.siteCd = e.siteCd
        AND a.demoCd = e.demoCd
        AND e.state = 'R'
        
	    WHERE 1=1
        {search_query}

        ORDER BY demoCd DESC
    
    """.format_map({'search_query':search_query})

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, demoData in enumerate(data):
        dicDemo = dict()
        dicDemo['demoCd'] = demoData[1]
        dicDemo['demoState'] = demoData[2]
        dicDemo['partCd'] = demoData[3]
        dicDemo['inDate'] = demoData[4]
        dicDemo['sn'] = demoData[5]
        dicDemo['note'] = demoData[6]
        dicDemo['demoStateNm'] = demoData[12]
        dicDemo['partNm'] = demoData[13]
        dicDemo['partType3'] = demoData[14]
        dicDemo['partType3Nm'] = demoData[15]
        dicDemo['rentUser'] = demoData[16]
        dicDemo['rentDate'] = demoData[17]
        dicDemo['rentCust'] = demoData[18]
        dicDemo['rentCustNm'] = demoData[19]
        dicDemo['rentManager'] = demoData[20]
        dicDemo['phone'] = demoData[21]
        dicDemo['address'] = demoData[22]
        dicDemo['estRetDate'] = demoData[23]
        dicDemo['rcvDate'] = demoData[24]
        dicDemo['rcvUser'] = demoData[25]
        dicDemo['rcvYN'] = demoData[26]
        dicDemo['demoSeq'] = demoData[27]
        dicDemo['custNm'] = demoData[28]
        dicDemo['rdCd'] = demoData[29]
        dicDemo['rdSeq'] = demoData[30]
        dicDemo['resvDate'] = demoData[31]
        dicDemo['resvUser'] = demoData[32]
        dicDemo['resvNote'] = demoData[33]        

        data[index] = dicDemo
    return jsonify({
        'demoMnge':data})

    
    #cp = SalDemo.query.filter(SalDemo.siteCd.like('%' + siteCd + '%'), SalDemo.partCd.like('%' + partCd + '%'), SalDemo.sn.like('%' + sn + '%'), SalDemo.demoState.like('%' + demoState + '%'),  SalDemo.inDate >= start,SalDemo.inDate <= end, SalDemo.state.like('%' + state + '%')).all()
    #return jsonify({
    #    'Demo': [c.to_json() for c in cp]
    #}) 


@main.route('/api/chkSalDemo', methods=['POST'])
def check_sal_demo():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    partCd = json_data.get('partCd')
    inDate = json_data.get('inDate')
    demoState = json_data.get('demoState')
    sn = json_data.get('sn')
    print("JSON_DATA :", json_data)
    
    alCust = aliased(MstCust)

    chk = db.session.query(
                            SalDemoRent.siteCd, \
                            SalDemoRent.demoCd, \
                            SalDemoRent.demoSeq, \
                            SalDemoRent.rentUser, \
                            SalDemoRent.rentDate, \
                            SalDemoRent.rentCust, alCust.custNm.label('custNm'), \
                            SalDemoRent.rentManager, \
                            SalDemoRent.phone, \
                            SalDemoRent.address, \
                            SalDemoRent.estRetDate, \
                            SalDemoRent.rcvDate, \
                            SalDemoRent.rcvUser, \
                            SalDemoRent.rcvYN  \
                            )\
                    .filter(SalDemoRent.siteCd == siteCd, SalDemoRent.demoCd == demoCd, SalDemoRent.state == 'R') \
                    .join(alCust, SalDemoRent.rentCust == alCust.custCd ) \
                    .filter(alCust.state == 'R') \
                    .order_by(SalDemoRent.demoSeq.desc()).first()

    #chk = SalDemoRent.query.filter(SalDemoRent.siteCd == siteCd, SalDemoRent.demoCd == demoCd, SalDemoRent.state == 'R').order_by(SalDemoRent.demoSeq.desc()).first()
    print("CHECK : ", chk)
    if chk is None and (demoState == "Y" or demoState == "T" or demoState == "A"):
        return jsonify({
            'result': {
                'code': 8601,
                'msg': 'DemoRent정보가 존재하지 않습니다. '
            }
        })
    elif chk is None:
        return jsonify({
        
            'demoRentData': None
            
        })

    elif chk is not None:

        return jsonify({
            #'demoRentData': chk.to_json()
            'demoRentData': {
                'siteCd': chk[0],
                'demoCd': chk[1],
                'demoSeq': str(chk[2]),
                'rentUser': chk[3],
                'rentDate': chk[4],
                'rentCust': chk[5],
                'rentCustNm':chk[6], 
                'rentManager': chk[7],
                'phone': chk[8],
                'address': chk[9],
                'estRetDate': chk[10],
                'rcvDate': chk[11],
                'rcvUser': chk[12],
                'rcvYN': chk[13]
                
            }
        })


# Demo 렌트 대여 정보 취득
@main.route('/api/infSalDemo', methods=['POST'])
def information_sal_demo():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    partCd = json_data.get('partCd')
    inDate = json_data.get('inDate')
    demoState = json_data.get('demoState')
    sn = json_data.get('sn')
    print("JSON_DATA :", json_data)

    rcvYN = ""

    search_query = "AND a.siteCd = '" + siteCd + "'"

    if demoCd != '':
        search_query += "AND a.demoCd = '" + demoCd + "'"
    

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    sql = """
    SELECT a.siteCd, a.demoCd,a.demoState, b.rentCust, b.rentUser, b.phone,b.address,b.rentDate,b.demoSeq,b.estRetDate,b.rcvUser,b.rcvDate, b.rentManager,c.custNm
	FROM sal_demo AS a
	INNER JOIN sal_demo_rent AS b
	ON a.demoCd = b.demoCd
	AND a.siteCd = b.siteCd
	AND a.state = 'R'
	AND b.state = 'R'
	INNER JOIN mst_cust AS c
	ON b.rentCust = c.custCd
	AND b.siteCd = c.siteCd
	AND b.state = 'R'
	AND c.state = 'R'
    WHERE 1=1
    {search_query}
    """.format_map({'search_query':search_query})

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, infData in enumerate(data):
        dic = dict()
        dic['siteCd'] = infData[0]
        dic['demoCd'] = infData[1]
        dic['demoState'] = infData[2]
        dic['rentCust'] = infData[3]
        dic['rentUser'] = infData[4]
        dic['phone'] = infData[5]
        dic['address'] = infData[6]
        dic['rentDate'] = infData[7]
        dic['demoSeq'] = infData[8]
        dic['estRetDate'] = infData[9]
        dic['rcvUser'] = infData[10]
        dic['rcvDate'] = infData[11]
        dic['rentManager'] = infData[12]
        dic['custNm'] = infData[13]

        data[index] = dic
    
    print("DATA = ",data)



    if data is None and (demoState == "Y" or demoState == "T" or demoState == "A"):
        return jsonify({
            'result': {
                'code': 8501,
                'msg' : gettext('8501')
            }
        })
    elif data is None:
        return jsonify(
        {
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demoRentData': 
        {
            'siteCd': "",
            'demoCd': "",
            'demoSeq': "",
            'demoState': "",
            'rentDate': "",
            'rentUser': "",
            'rentCust': "",
            'rentManager': "",
            'phone': "",
            'address': "",
            'estRetDate': "",
            'rcvDate': "",
            'rcvUser': "",
            'rcvYN': "",
            'custNm':""
            
            
        }
    })
    elif data is not None:
        return jsonify(
        {
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demoRentData': data
    })



    """
    if demoState == "C":
        rcvYN = "Y"
    else:
        rcvYN = "N"
    """

    """
    demoRentData = SalDemoRent.query.filter_by(demoCd = demoCd).first()
    
    print("RENT DATA : ", demoRentData)
    #demoRentData = SalDemo.query.filter_by(demoCd = demoCd, partCd= partCd, state='R').first()

    
    if demoRentData is None and (demoState == "Y" or demoState == "T" or demoState == "A"):
        
        return jsonify({
            'result': {
                'code': 8501,
                'msg' : gettext('8501')
            }
        })

    
    print("IN")
    if demoRentData is not None:
        return jsonify(
        {
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
            'demoRentData': demoRentData.to_json()
    })
    else:
      return jsonify(
        {
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
            'demoRentData': 
            {
                 'siteCd': "",
                'demoCd': "",
                'demoSeq': "",
                'demoState': "",
                'r entDate': "",
                'rentUser': "",
                'rentCust': "",
                'rentManager': "",
                'phone': "",
                'address': "",
                'estRetDate': "",
                'rcvDate': "",
                'rcvUser': "",
                'rcvYN': "",
                'state': "",
                'regUser': ""
                
            }
    }) 
    """
    



# Demo 추가
@main.route('/api/insSalDemo', methods=['POST'])
def insert_sal_demo():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    #demoCd = json_data.get('demoCd')
    #demoState = json_data.get('demoState')
    partCd = json_data.get('partCd')
    inDate = json_data.get('inDate')
    sn = json_data.get('sn')
    #state = json_data.get('state')
    note = json_data.get('note')
    user = json_data.get('user')
    print("JSON_DATA = ", json_data)
    """
    chk = SalDemo.query.filter_by(siteCd = siteCd).first()
    if chk is not None:
        return jsonify({
            'result': {
                'code': 8503,
                # 'msg' : 'It is already registered data.'
                'msg' : gettext('8503')
            }            
        })
   """ 
    inDate = inDate.replace("-","")
    inDate = inDate[:8]

    findKey = 'DM' + inDate[-6:]
    seq  =1
    sel = SalDemo.query.filter(SalDemo.siteCd == siteCd, SalDemo.demoCd.like(findKey + '%')).order_by(SalDemo.demoCd.desc()).first()
    if sel is not None:
        seq = int(sel.demoCd[-6:]) + 1    
    demoCd = findKey + (6 - len(str(seq))) * '0' + str(seq)

    print('DEMOCD : ', demoCd)
    
    # demoCd = "D"+inDate
    # print("DEMOCD = ",demoCd)
    # #demoSeq = SalDemo.query.filter_by(demoCd = demoCd+"%").all()
    # demoSeq = SalDemo.query.filter(SalDemo.demoCd.like('%'+ demoCd + '%')).all()
    # #SysSite.query.filter(SysSite.siteCd.like('%' + siteCd + '%'), SysSite.siteNm.like('%' + siteNm + '%'), SysSite.state=='R').all()
    
    # print("DEMOSEQ = ",demoSeq)
    # seq = 0
    # if not demoSeq:
    #     seq = 0
    # else:
    #     seq = len(demoSeq)
    # demoCd = demoCd + '-' + str(seq)

    demo = SalDemo( siteCd=siteCd,
                    demoCd=demoCd,
                    demoState="C",
                    partCd=partCd,
                    inDate=inDate,
                    sn=sn,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)
    
    db.session.add(demo)
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demo': demo.to_json()
    })


#Demo 대여
@main.route('/api/renSalDemo', methods = ['POST'])
def select_sal_rent_demo():
    json_data = json.loads(request.data, strict=False)
    print("JSON_DATA = ", json_data)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    rentCust = json_data.get('rentCust')
    rentUser = json_data.get('rentUser')
    rentManager = json_data.get('rentManager')
    phone = json_data.get('phone')
    address = json_data.get('address')
    demoState = json_data.get('demoState')
    rentDate = json_data.get('rentDate')
    estRetDate = json_data.get('estRetDate')
    
    user = json_data.get('user')

    print("RENTDATE = ",rentDate)

    rentDate = rentDate.replace("-","")
    print("RENTDATE = ",rentDate)
    estRetDate = estRetDate.replace("-","")
    print("estRetDate = ",estRetDate)
    rentDate = rentDate[:8]
    estRetDate = estRetDate[:8]
    print("RENTDATE = ",rentDate)
    print("estRetDate = ",estRetDate)
    demo = SalDemo.query.filter_by( demoCd = demoCd).first()
    if demo is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    print("DEMO = ",demo)
    demo.demoState = demoState or demo.demoState
    demo.modUser = user or demo.modUser
    demo.modDate = datetime.now()
    db.session.add(demo)
    db.session.commit()

    # rentSize = SalDemoRent.query.all()
    # size=0
    # print("RENTSIZE = ",rentSize)
    # if not rentSize:
    #     size = 0
    # else:
    #     size = len(rentSize) 

    size = 1
    sel_demoSeq = SalDemoRent.query.filter(SalDemoRent.siteCd == siteCd, SalDemoRent.demoCd == demoCd).order_by(SalDemoRent.demoSeq.desc()).first()
    if sel_demoSeq is not None:
        size = int(sel_demoSeq.demoSeq) + 1
    
    print("SIZE = ",size)
    demoRent = SalDemoRent(siteCd=siteCd,
                              rentCust = rentCust,
                              demoCd = demoCd,
                              rentManager=rentManager,
                              rentUser = rentUser,
                              phone=phone,
                              address=address,
                              demoState=demoState,
                              rentDate=rentDate,
                              estRetDate=estRetDate,
                              demoSeq=size,
                              state='R',
                              rcvYN = 'N',
                              regUser=user,
                              regDate=datetime.now(),
                              modUser=None,
                              modDate=None
                              )
    db.session.add(demoRent)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demoRent': demoRent.to_json()
    })


# Demo 수정
@main.route('/api/updSalDemo', methods=['POST'])
def modify_sal_demo():    
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    partCd = json_data.get('partCd')
    inDate = json_data.get('inDate')
    sn = json_data.get('sn')
    note = json_data.get('note')
    demoState = json_data.get('demoState')
    rentCust = json_data.get('rentCust')
    rentUser = json_data.get('rentUser')
    rentManager = json_data.get('rentManager')
    phone = json_data.get('phone')
    address = json_data.get('address')
    rentDate = json_data.get('rentDate')
    estRetDate = json_data.get('estRetDate')
    rcvYN = json_data.get('rcvYN')
    rcvDate = json_data.get('rcvDate')
    rcvUser = json_data.get('rcvUser')
    demoSeq = json_data.get('demoSeq')


    user = json_data.get('user')
    print("JSON = ",json_data)

    inDate = inDate.replace("-","")
    inDate = inDate[:8]
    rentDate = rentDate.replace("-","")
    rentDate = rentDate[:8]
    estRetDate = estRetDate.replace("-","")
    estRetDate = estRetDate[:8]
    

    print('STATE : rcvUser len [{len1}] || demoSeq [{seq}] || rcvYN [{YN}]'.format_map({'len1': len(rcvUser), 'seq':demoSeq, 'YN':rcvYN} ))
    

    #if (len(rcvUser) == 0 and len(demoSeq) != 0) or rcvYN == "N": # 반납 관련하여 체크 해제 및 이름을 지웠을때
    if (rcvYN == 'N' or rcvUser == '') and demoSeq != '' :  #반납여부 체스 해제 또는 반납자명을 지웠을때
    #if (rcvYN == 'N' and demoSeq != '') or (rcvUser == '' and demoSeq != '') :  # 반납여부 체스 해제 또는 반납자명을 지웠을때
        print('Return to RentState : DemState [{state}] '.format_map({'state':demoState}))
        if demoState == "C":
            demoMnge = SalDemo.query.filter_by( demoCd = demoCd).first()
            demoRent = SalDemoRent.query.filter_by(demoSeq = demoSeq, demoCd = demoCd).first()

            demoMnge.siteCd = siteCd or demoMnge.siteCd
            demoMnge.demoState = demoRent.demoState
            demoMnge.partCd = partCd or demoMnge.partCd
            demoMnge.inDate = inDate or demoMnge.inDate
            demoMnge.sn = sn or demoMnge.sn
            demoMnge.note = note or demoMnge.note
            
            demoMnge.modUser = user or demoMnge.modUser
            demoMnge.modDate = datetime.now()

            db.session.add(demoMnge)
            db.session.commit()

            demoRent.rentCust = rentCust or demoRent.rentCust
            demoRent.rentUser = rentUser or demoRent.rentUser
            demoRent.rentManager = rentManager or demoRent.rentManager
            demoRent.phone = phone or demoRent.phone
            demoRent.address = address or demoRent.address
            demoRent.rentDate = rentDate or demoRent.rentDate
            demoRent.estRetDate = estRetDate or demoRent.estRetDate
            demoRent.rcvYN = "N"
            #demoRent.rcvDate = rcvDate or demoRent.rcvDate
            #demoRent.rcvUser = rcvUser or demoRent.rcvUser
            demoRent.rcvDate = ""
            demoRent.rcvUser = ""
            demoRent.modUser = user or demoRent.modUser
            demoRent.modDate = datetime.now()
            db.session.add(demoRent)
            db.session.commit()


            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                },
                'demoMnge': demoMnge.to_json(),
                'demoRent': demoRent.to_json()
            })
            """
            return jsonify({
                'result': {
                    'code': 8503,
                    # 'msg' : 'It is already registered data.'
                    'msg': gettext('8503')
                }
            })
            """ 
    
    elif rcvYN == 'N' and demoSeq == '': #추가하고 대여를 안했을때 
        print('Did not rent demo ')
        demoMnge = SalDemo.query.filter_by( demoCd = demoCd).first()
    
        print("DEMO = ",demoMnge)
        if demoMnge is None:
            return jsonify({
                'result': {
                    'code': 8504,
                    
                    'msg' : gettext('8504')
                }            
            })
        print('DEMO : ',demoMnge)
        print('json_data : ',json_data)
        
        demoMnge.siteCd = siteCd or demoMnge.siteCd
        
        demoMnge.demoState = demoState or demoMnge.demoState

        
        demoMnge.partCd = partCd or demoMnge.partCd
        demoMnge.inDate = inDate or demoMnge.inDate
        demoMnge.sn = sn or demoMnge.sn
        demoMnge.note = note or demoMnge.note
        
        demoMnge.modUser = user or demoMnge.modUser
        demoMnge.modDate = datetime.now()

        print('demoCd : ',demoMnge.demoCd)
        print('demoState : ',demoMnge.partCd)
        print('inDate :',demoMnge.partCd)
        print('sn : ',demoMnge.sn)
       

        db.session.add(demoMnge)
        db.session.commit()
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'demo': demoMnge.to_json()
        })

    rcvDate = rcvDate.replace("-","")
    rcvDate = rcvDate[:8]

    demoMnge = SalDemo.query.filter_by( demoCd = demoCd).first()
    demoRent = SalDemoRent.query.filter_by(demoSeq = demoSeq, demoCd = demoCd).first()
    print("demoMnge = ",demoMnge)
    print("demoRent = ",demoRent)
    if demoMnge is None or demoRent is None :
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    print('Total Modify')
    demoMnge.siteCd = siteCd or demoMnge.siteCd
    
    demoMnge.demoState = demoState or demoMnge.demoState
    demoMnge.partCd = partCd or demoMnge.partCd
    demoMnge.inDate = inDate or demoMnge.inDate
    demoMnge.sn = sn or demoMnge.sn
    demoMnge.note = note or demoMnge.note
   
    demoMnge.modUser = user or demoMnge.modUser
    demoMnge.modDate = datetime.now()
    db.session.add(demoMnge)
    db.session.commit()

    if demoState != "C":
        demoRent.demoState = demoState or demoRent.demoState
    
    demoRent.rentCust = rentCust or demoRent.rentCust
    demoRent.rentUser = rentUser or demoRent.rentUser
    demoRent.rentManager = rentManager or demoRent.rentManager
    demoRent.phone = phone or demoRent.phone
    demoRent.address = address or demoRent.address
    demoRent.rentDate = rentDate or demoRent.rentDate
    demoRent.estRetDate = estRetDate or demoRent.estRetDate
    demoRent.rcvYN = rcvYN or demoRent.rcvYN
    demoRent.rcvDate = rcvDate or demoRent.rcvDate
    demoRent.rcvUser = rcvUser or demoRent.rcvUser
    demoRent.modUser = user or demoRent.modUser
    demoRent.modDate = datetime.now()
    db.session.add(demoRent)
    db.session.commit()

    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demoMnge': demoMnge.to_json(),
        'demoRent': demoRent.to_json()
    })


#Demo 반납
@main.route('/api/rcvSalDemo', methods=['POST'])
def receive_sal_demo():
    json_data = json.loads(request.data, strict=False)
    demoSeq = json_data.get('demoSeq')
    demoCd = json_data.get('demoCd')
    rcvDate = json_data.get('rcvDate')
    rcvUser = json_data.get('rcvUser')
    rcvYN = json_data.get('rcvYN')
    user = json_data.get('user')

    print("JSON_DATA : ", json_data)
    demoInOutData = SalDemoRent.query.filter_by(demoCd=demoCd, demoSeq= demoSeq , state="R", rcvYN="N").first()
    if demoInOutData is None:
        return jsonify({
            'result': {
                'code': 8504,
                
                'msg' : gettext('8504')
            }            
        })

    # if rcvYN == "True":
    #     rcvYN = "Y"
    # else :
    #     rcvYN = "N"
    rcvDate = rcvDate.replace("-","")
    rcvDate = rcvDate[:8]
    
    demoInOutData.rcvDate = rcvDate or demoInOutData.rcvDate
    demoInOutData.rcvUser = rcvUser or demoInOutData.rcvUser
    demoInOutData.rcvYN = rcvYN or demoInOutData.rcvYN
    demoInOutData.modUser = user or demoInOutData.modUser
    demoInOutData.modDate = datetime.now()

    db.session.add(demoInOutData)
    db.session.commit()

    demoMnge= SalDemo.query.filter_by(demoCd=demoCd).first()
    if demoMnge is None:
        return jsonify({
            'result': {
                'code': 8504,
                'msg' : gettext('8504')
            }            
        })
    demoMnge.demoState = "C" or demoMnge.demoState
    demoMnge.modUser = user or demoMnge.modUser
    demoMnge.modDate = datetime.now()

    db.session.add(demoMnge)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demo': demoInOutData.to_json()
    })

#데모 삭제
@main.route('/api/delSalDemo', methods=['POST'])
def delete_sal_demo():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    inDate = json_data.get('inDate')
    demoState = json_data.get('demoState')
    user = json_data.get('user')
    print("JSON_DATA : ", json_data)

    inDate = inDate.replace("-","")
    inDate = inDate[:8]

    demoDel = SalDemo.query.filter_by(demoCd=demoCd, inDate=inDate , state="R").first()
    if demoDel is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            } 
        })
    print("DEMODEL : ", demoDel)
    demoDel.state = "D" or demoDel.state
    demoDel.modUser = user or  demoDel.modUser
    demoDel.modDate = datetime.now()

    db.session.add(demoDel)
    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'demo': demoDel.to_json()
    })


#데모 대여 기록 조회
@main.route('/api/selSalRentDemo', methods=['POST'])
def select_sal_rent_demo_mnge():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    demoCd = json_data.get('demoCd')
    demoState = json_data.get('demoState')
    rentUser = json_data.get('rentUser')
    rcvYN = json_data.get('rcvYN')
    dateCategory = json_data.get('dtCtg')
    start = json_data.get('start')
    end = json_data.get('end')
    sn = json_data.get('sn')
 

    print("JSON_DATA : ", json_data)

    search_query = "AND a.siteCd = '" + siteCd + "'"

    if demoCd != '':
        search_query += "AND a.demoCd LIKE '%" + demoCd + "%'"
    if demoState != '':
        search_query += "AND b.demoState = '" + demoState + "'"
    if rentUser != '':
        search_query += "AND b.rentUser LIKE '%" + rentUser + "%'"
    if rcvYN != '':
        search_query += "AND b.rcvYN = '" + rcvYN + "'"
    if sn != '':
        search_query += "AND a.sn LIKE '%" + sn + "%'"
    

    if dateCategory != '':
        if dateCategory == 'R':
            search_query += "AND b.rentDate BETWEEN '" + start + "' AND  '"+ end + "'"
             
        elif dateCategory == 'V':
            search_query += "AND b.rcvDate BETWEEN '" + start + "' AND  '"+ end + "'"
    
    print("SEARCH_QUERY = ", search_query)
    

    conn = pymysql.connect(host=db.engine.url.host,

                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)
    
    curs = conn.cursor()

    sql = """ 
    SELECT a.demoCd,
           a.partCd, 
           a.inDate,
           a.sn,
           b.demoSeq,
           b.demoState,  fn_get_codename('S0004', b.demoState) AS demoStateNm,
           b.rentUser,
           b.rentDate,
           b.rentCust,
           b.rentManager,
           b.phone,
           b.address,
           b.estRetDate,
           b.rcvDate,
           b.rcvUser,
           b.rcvYN,
           c.partNm,
           c.partType3, fn_get_codename('C0006', c.partType3) AS partType3Nm,
           d.custNm
        #    e.userNm
    FROM sal_demo AS a
	INNER JOIN sal_demo_rent AS b
	ON a.demoCd = b.demoCd
	AND a.siteCd = b.siteCd
	AND a.state = 'R'
	AND b.state = 'R'
	
	INNER JOIN mst_part AS c
	ON a.partCd = c.partCd
	AND a.siteCd = c.siteCd
	AND a.state = 'R'
	AND c.state = 'R'

    INNER JOIN mst_cust AS d
	ON b.rentCust = d.custCd
	AND b.siteCd = d.siteCd
	AND b.state = 'R'
	AND d.state = 'R'

    # INNER JOIN sys_user AS e
	# ON b.rcvUser = e.userCd
	# AND b.siteCd = e.siteCd
	# AND e.state = 'R'

	WHERE 1=1
    {search_query}
    ORDER BY demoCd DESC, demoSeq DESC
    """.format_map({'search_query':search_query})

    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    for index, demoData in enumerate(data):
        dicDemo = dict()
        dicDemo['demoCd'] = demoData[0]
        dicDemo['partCd'] = demoData[1]
        dicDemo['inDate'] = demoData[2]
        dicDemo['sn'] = demoData[3]
        dicDemo['demoSeq'] = demoData[4]
        dicDemo['demoState'] = demoData[5]
        dicDemo['demoStateNm'] = demoData[6]
        dicDemo['rentUser'] = demoData[7]
        dicDemo['rentDate'] = demoData[8]
        dicDemo['rentCust'] = demoData[9]
        dicDemo['rentManager'] = demoData[10]
        dicDemo['phone'] = demoData[11]
        dicDemo['address'] = demoData[12]
        dicDemo['estRetDate'] = demoData[13]
        dicDemo['rcvDate'] = demoData[14]
        dicDemo['rcvUser'] = demoData[15]
        dicDemo['rcvYN'] = demoData[16]
        dicDemo['partNm'] = demoData[17]
        dicDemo['partType3'] = demoData[18]
        dicDemo['partType3Nm'] = demoData[19]
        dicDemo['custNm'] = demoData[20]
        # dicDemo['rcvUserNm'] = demoData[21]

        data[index] = dicDemo
    return jsonify({
        'demoRentMnge':data})

@main.route('/api/regSalDemoReserve', methods=['POST'])
def regist_sal_demo_reserve():    
    json_data = json.loads(request.data, strict=False)    
    siteCd = json_data.get('siteCd')
    rdCd = json_data.get('rdCd')
    resvDate = json_data.get('resvDate')
    resvUser = json_data.get('resvUser')    
    demoCd = json_data.get('demoCd')    
    note = json_data.get('note')
    user = json_data.get('user')    

    # check pre_sal_reserve_demo
    pre_rdInfoes = SalReserveDemo.query.filter_by(siteCd = siteCd, demoCd = demoCd, state = 'R')

    # check sal_reserve_demo
    if not rdCd:    
        findKey_rdCd = 'RD' + datetime.now().strftime('%y%m%d')
        seq_rdCd = 1
        sel_rdCd = SalReserveDemo.query.filter(SalReserveDemo.siteCd == siteCd, SalReserveDemo.rdCd.like(findKey_rdCd + '%')).order_by(SalReserveDemo.rdCd.desc()).first()
        if sel_rdCd is not None:
            seq_rdCd = int(sel_rdCd.rdCd[-6:]) + 1
        rdCd = findKey_rdCd + (6 - len(str(seq_rdCd))) * '0' + str(seq_rdCd)

    rdSeq = 1
    sel_rdSeq = SalReserveDemo.query.filter(SalReserveDemo.siteCd == siteCd, SalReserveDemo.rdCd == rdCd).order_by(SalReserveDemo.rdSeq.desc()).first()
    if sel_rdSeq is not None:
        rdSeq = int(sel_rdSeq.rdSeq) + 1

    # pre_sal_reserve_demo update
    if pre_rdInfoes is not None:
        pre_rdInfoes.update({SalReserveDemo.state: 'N', SalReserveDemo.modUser: user, SalReserveDemo.modDate: datetime.now()})

    # sal_reserve_demo insert
    salReserveDemo = SalReserveDemo(
                    siteCd=siteCd,
                    rdCd=rdCd,
                    rdSeq=rdSeq,
                    resvDate=resvDate,
                    resvUser=resvUser,
                    demoCd=demoCd,
                    note=note,
                    state='R',
                    regUser=user,
                    regDate=datetime.now(),
                    modUser=None,
                    modDate=None)    
    
    db.session.add(salReserveDemo) 
    db.session.commit()
    
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'salReserveDemo': salReserveDemo.to_json()
    })

# Service 조회
@main.route('/api/selSalSvc', methods=['POST'])
def select_service():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')
    poNo = json_data.get('poNo')
    start = json_data.get('start')
    end = json_data.get('end')
    dtCategory = json_data.get('dtCategory')
    partText = json_data.get('partText')
    sn = json_data.get('sn')
    print('JSON_DATA : ', json_data)

    conn = pymysql.connect(host=db.engine.url.host,
                            user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    search_query = "AND c.siteCd = '" + siteCd + "'"

    if partCd != '':
        search_query += "AND c.partCd = '{partCd}'".format_map({'partCd':partCd})
    elif partText != '':
        search_query += "AND (c.partCd LIKE CONCAT ('%','{partText}','%')) OR (d.partNm LIKE CONCAT ('%','{partText}','%'))".format_map({'partText':partText})
    if poNo != '':
        search_query += "AND c.poNo LIKE CONCAT('%','{poNo}','%')".format_map({'poNo':poNo})
    if sn != '':
        search_query += "AND c.sn LIKE CONCAT ('%','{sn}','%')".format_map({'sn':sn})

    if dtCategory == 'S':
        search_query += "AND c.svcStDate >= '{start}'".format_map({'start':start})
        search_query += "AND c.svcEdDate <= '{end}'".format_map({'end':end})
    elif dtCategory == 'P':
        search_query += "AND c.poDate BETWEEN '{start}' AND  '{end}'".format_map({'start':start, 'end':end})
    elif dtCategory == 'I':
        search_query += "AND c.inDate BETWEEN '{start}' AND  '{end}'".format_map({'start':start, 'end':end})
    
    print("SEARCH_QUERY : ", search_query)
    # sql = """
    # SELECT c.*, d.partNm
    # FROM (
    #     SELECT a.siteCd, 
    #             a.partCd,
    #             a.poType2, fn_get_codename('P0004', a.poType2) AS poType2Nm,
    #             a.poCd,
    #             a.poNo,
    #             a.poDate,
    #             a.svcStDate,
    #             a.svcEdDate,
    #             b.sn
    #     FROM pur_order AS a 
    #     LEFT JOIN stk_in AS b
    #     ON a.siteCd = b.siteCd
    #     AND a.poCd = b.poCd
    #     AND a.partCd = b.partCd
    #     AND a.state = 'R'
    #     AND b.state = 'R'
    # ) AS c
    # INNER JOIN mst_part AS d
    # ON c.siteCd = d.siteCd
    # AND c.partCd = d.partCd
    # AND d.state = 'R'
    # WHERE 1=1
    # AND c.poType2 = 'V'
    # {search_query}
    # ORDER BY poCd DESC
    # """.format_map({'search_query':search_query})

    sql = """
    SELECT c.*,
		d.partType1, fn_get_codename('C0004', d.partType1) AS partType1Nm,
		d.partNm	
	FROM (
		SELECT
				a.siteCd, 
				a.partCd,
				a.inCd,
				a.inNo,
				a.inDate,
				a.lotNo,
				a.sn,
				a.poCd,
				a.inQty,
				a.svcStDate,
				a.svcEdDate,
				b.poNo,
				b.soNo,
				b.poDate
		FROM stk_in AS a
		LEFT JOIN pur_order AS b
		ON a.siteCd = b.siteCd
		AND a.poCd = b.poCd
		AND a.state = 'R'
		AND b.state = 'R'
	) AS c
	INNER JOIN mst_part AS d
	ON c.siteCd = d.siteCd
	AND c.partCd = d.partCd
	AND d.state = 'R'	
	
	WHERE 
    d.partType1 = 'V'
	{search_query}
	ORDER BY inCd DESC , svcStDate DESC
    """.format_map({'search_query':search_query})


    curs.execute(sql)
    data = list(curs.fetchall())
    conn.close()

    # for index, dt in enumerate(data):
    #     dic = dict()
    #     dic['siteCd'] = dt[0]
    #     dic['partCd'] = dt[1]
    #     dic['poType2'] = dt[2]
    #     dic['poType2Nm'] = dt[3]
    #     dic['poCd'] = dt[4]
    #     dic['poNo'] = dt[5]
    #     dic['poDate'] = dt[6]
    #     dic['svcStDate'] = dt[7]
    #     dic['svcEdDate'] = dt[8]
    #     dic['sn'] = dt[9]
    #     dic['partNm'] = dt[10]

    #     data[index] = dic

    for index, dt in enumerate(data):
        dic = dict()
        dic['siteCd'] = dt[0]
        dic['partCd'] = dt[1]
        dic['inCd'] = dt[2]
        dic['inNo'] = dt[3]
        dic['inDate'] = dt[4]
        dic['lotNo'] = dt[5]
        dic['sn'] = dt[6]
        dic['poCd'] = dt[7]
        dic['inQty'] = dt[8]
        dic['svcStDate'] = dt[9]
        dic['svcEdDate'] = dt[10]
        dic['poNo'] = dt[11]
        dic['soNo'] = dt[12]
        dic['poDate'] = dt[13]
        dic['partType1'] = dt[14]
        dic['partType1Nm'] = dt[15]
        dic['partNm'] = dt[16]


        data[index] = dic

    print('DATA : ', data)
    return jsonify({'serviceMnge':data})


#Service 기간 입력
@main.route('/api/insSalSvc', methods=['POST'])
def modify_Sal_Service():
    json_data = json.loads(request.data, strict=False)
    siteCd = json_data.get('siteCd')
    partCd = json_data.get('partCd')
    sn = json_data.get('sn')
    poCd = json_data.get('poCd')
    poNo = json_data.get('poNo')
    poDate = json_data.get('poDate')
    inCd = json_data.get('inCd')
    lotNo = json_data.get('lotNo')
    inDate = json_data.get('inDate')
    svcStDate = json_data.get('svcStDate')
    svcEdDate = json_data.get('svcEdDate')

    print("JSON_DATA : ", json_data)

    poDate = poDate.replace("-","")
    poDate = poDate[:8]
    svcStDate = svcStDate.replace("-","")
    svcStDate = svcStDate[:8]
    svcEdDate = svcEdDate.replace("-","")
    svcEdDate = svcEdDate[:8]
    inDate = inDate.replace("-","")
    inDate = inDate[:8]


    # svc = PurOrder.query.filter_by(siteCd = siteCd, poCd = poCd ,poNo = poNo, poDate = poDate).first()
    svc = StkIn.query.filter_by(siteCd = siteCd, poCd = poCd, lotNo = lotNo).first()
    if svc is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    svc.svcStDate = svcStDate or svc.svcStDate
    svc.svcEdDate = svcEdDate or svc.svcEdDate

    db.session.add(svc)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
    })

    # conn = pymysql.connect(host=db.engine.url.host,
    #                         user=db.engine.url.username,
    #                        password=db.engine.url.password,
    #                        db=db.engine.url.database,
    #                        charset=db.engine.url.query['charset'],
    #                        port=db.engine.url.port)

    # curs = conn.cursor()


    # search_query = ""

    # if siteCd != '':
    #     search_query += "AND siteCd = '" + siteCd + "'"
    # if poNo != '':
    #     search_query += "AND poNo = '" + poNo + "'"
    # if poDate != '':
    #     search_query += "AND poDate = '" + poDate + "'"
                                  
    # sql = """
    # UPDATE pur_order SET svcStDate  = '{svcStDate}', svcEdDate = '{svcEdDate}'
    # WHERE 1=1
    # {search_query}
    # """.format_map({'svcStDate':svcStDate, 'svcEdDate':svcEdDate, 'search_query':search_query})


    # curs.execute(sql)
    # data = list(curs.fetchall())
    # print("DATA : ",data)
    # conn.close()

    


    # print("SQL : ",sql)

    # return jsonify({
    #     'result': {
    #         'code': 1000,
    #         'msg' : gettext('1000')
    #     }
    # })

    

           


