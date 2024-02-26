# -- coding: utf-8 -- 

import os

from flask import jsonify, request, flash, url_for, app, current_app, json
from werkzeug.utils import secure_filename, redirect

import config
import datetime
from app import db, get_locale
from app.models_bstnt import *
from app.main.cipherutil import *
from dateutil import parser
from sqlalchemy import func, literal
from sqlalchemy.orm import aliased
from flask_babel import gettext
import pymysql
from app.main.awsutil import awsS3

from . import main

@main.route('/api/s3SelBucket', methods=['GET','POST'])
def s3SelBucket():
    try:        
        buckets = awsS3.select_bucket_list()

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'bucketList': buckets
        })

    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/s3SelObject', methods=['POST'])
def s3SelObject():
    try:   
        json_data = request.get_json()
        bucket_name = json_data.get('bucket')
        prefix = json_data.get('prefix')
        includeChild = json_data.get('includeChild') if json_data.get('includeChild') else "N"
        objects = awsS3.select_object_list(bucket_name, prefix, includeChild)

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'objectList': objects
        })
       
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/s3SelExists', methods=['POST'])
def s3SelExists():
    try:   
        json_data = request.get_json()
        bucket_name = json_data.get('bucket')
        prefix = json_data.get('prefix')      
        exists = 'True' if awsS3.exists(bucket_name, prefix) else 'False'

        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'exists': exists
        })
       
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/s3InsBucket', methods=['POST'])
def s3InsBucket():
    try:
        json_data = request.get_json()
        bucket_name = json_data.get('bucket')
        result = awsS3.create_bucket(bucket_name)

        if result == True:            
            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                }
            })
        else:
            return jsonify({
                'result': {
                    'code': 9999,
                    'msg' : 'error'
                }
            })
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/s3InsFile', methods=['POST'])
def s3InsFile():
    try:   
        json_data = request.get_json()
        file_name = json_data.get('fileName')
        bucket_name = json_data.get('bucket')
        upload_file_name = json_data.get('uploadName')
        rst = awsS3.upload_file(file_name, bucket_name, upload_file_name)

        if rst:
            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                }
            })
        else:
            return jsonify({
                'result': {
                    'code': 9999,
                    'msg' : 'error'
                }
            })
       
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/s3DelFile', methods=['POST'])
def s3DelFile():
    try:   
        json_data = request.get_json()        
        bucket_name = json_data.get('bucket')
        file_name = json_data.get('fileName')
        rst = awsS3.delete_file(bucket_name, file_name)

        if rst:
            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                }
            })
        else:
            return jsonify({
                'result': {
                    'code': 9999,
                    'msg' : 'error'
                }
            })
       
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 9999,
                'msg' : 'error',
                'msg2': str(e)
            }
        })

@main.route('/api/chkDb', methods=['GET'])
def testdb():
    try:
        # db.session.query("1").from_statement("select 1").all()
        db.session.query("1").from_statement(db.text("SELECT 1")).first()
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            }
        })
    except Exception as e:        
        return jsonify({
            'result': {
                'code': 3100,
                'msg' : gettext('3100'),
                'msg2': str(e)
            }
        })
        

@main.route('/api/selCompany', methods=['POST'])
def select_customer():
    cp = TdCompany.query.all()    
    return jsonify({
        'company': [c.to_json() for c in cp]
    })

@main.route('/api/decodingBase64AndDecrypt', methods=['POST'])
def decodingBase64AndDecrypt():
    json_data = request.get_json()
    value = json_data.get('value')
    cipher = CipherAgent()    
    data = cipher.decodingBase64AndDecrypt(value)
    return data

@main.route('/api/encryptAndEncodingBase64', methods=['POST'])
def encryptAndEncodingBase64():
    json_data = request.get_json()
    value = json_data.get('value')
    cipher = CipherAgent()
    data = cipher.encryptAndEncodingBase64(value)
    return data

@main.route('/api/decrypt', methods=['POST'])
def decrypt():
    json_data = request.get_json()
    value = json_data.get('value')
    cipher = CipherAgent()
    data_temp = base64.b64decode(value)
    data = cipher.decrypt(data_temp)
    return data

@main.route('/api/encrypt', methods=['POST'])
def encrypt():
    json_data = request.get_json()
    value = json_data.get('value')
    cipher = CipherAgent()    
    data_temp = cipher.encrypt(value)
    data = base64.encodestring(data_temp)
    return data

@main.route('/api/decryptNoPadding', methods=['POST'])
def decryptNoPadding():
    json_data = request.get_json()
    value = json_data.get('value')
    
    # if value.find('?d=') != -1:
    #     webkeyvalue = value.split('?d=', 1)[1]
    #     webkeyvalue = webkeyvalue.replace(' ', '')
    #     webkeyvalue = webkeyvalue.replace('%2B', '+')
    #     webkeyvalue = webkeyvalue.replace('%2F', '/')
    #     webkeyvalue = webkeyvalue.replace('%25', '%')
    #     webkeyvalue = webkeyvalue.replace('%3D%3D', '==')

    value = value.replace(' ', '')
    value = value.replace('%2B', '+')
    value = value.replace('%2F', '/')
    value = value.replace('%25', '%')
    value = value.replace('%3D%3D', '==')

    cipher = CipherAgent(ENCRYPTION_KEY_SQR_WEB, ENCRYPTION_KEY_SQR_IV)
    data_temp = base64.b64decode(value)
    data = cipher.decryptNoPadding(data_temp)
    
    return data

@main.route('/api/encryptNoPadding', methods=['POST'])
def encryptNoPadding():
    # json_data = request.get_json()
    # value = json_data.get('value')
    # cipher = CipherAgent()
    # data_temp = cipher.encryptNoPadding(value)
    # data = base64.encodestring(data_temp)
    # return data

    json_data = request.get_json()
    value = json_data.get('value')
    cipher = CipherAgent(ENCRYPTION_KEY_SQR_WEB, ENCRYPTION_KEY_SQR_IV)
    data_temp = cipher.encryptNoPadding(value)
    data = base64.encodestring(data_temp)
    return data

@main.route('/api/login', methods=['POST'])
def login():
    lang = get_locale()
    json_data = request.get_json()
    login_id = json_data.get('id')
    login_password = json_data.get('password')
    # clinet_type = json_data.get('clientType')
    # if clinet_type == 'B':
        # # mobile logic check    

    cp = TdAccount.query.filter_by(id=login_id,state='Registered').first()    

    if cp is None:
        return jsonify({
            'result': {
                'code': 8501,
                # 'msg' : 'ID does not exist.'
                'msg' : gettext('8501')
            }
        })

    password_encoding = CipherAgent().encryptAndEncodingBase64(login_password)    

    if cp.pwd == password_encoding:
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'user': cp.to_json_simple(lang)
        })
    else:
        return jsonify({
            'result': {
                'code': 8502,
                # 'msg' : 'Password is incorrect.'
                'msg' : gettext('8502')
            }
        })

@main.route('/api/selRetailer', methods=['POST'])
def select_retalier():    
    json_data = request.get_json()
    companyCode = json_data.get('companyCode')
    cp =  TdRetailer.query.filter_by(companyCode = companyCode, state = 'Registered')
    if json_data.get('rtid'):
        cp = cp.filter_by(rtid = json_data.get('rtid'))
    return jsonify({
        'retailer': [c.to_json() for c in cp]
    })

@main.route('/api/selLine', methods=['POST'])
def select_line():
    json_data = request.get_json()
    rtid = json_data.get('rtid')
    cp = TdLine.query.filter_by(rtid = rtid, state = 'Registered')
    return jsonify({
        'line': [c.to_json() for c in cp]
    })

@main.route('/api/selHolotag', methods=['POST'])
def select_holotag():
    json_data = request.get_json()
    companyCode = json_data.get('companyCode')
    cp = TdHolotag.query.filter_by(companyCode = companyCode, state = 'Registered')    
    return jsonify({
        'holotag': [c.to_json() for c in cp]
    })

@main.route('/api/selLogisticbox', methods=['POST'])
def select_logisticbox():
    json_data = request.get_json()    
    companyCode = json_data.get('companyCode')
    rtid = json_data.get('rtid')
    lineCode = json_data.get('lineCode')
    parentBoxId = json_data.get('parentBoxId')
    palletId = json_data.get('palletId')
    boxType = json_data.get('boxType')
    scanYn = json_data.get('scanYn')
    palletPackYn = json_data.get('palletPackYn')
    palletScanYn = json_data.get('palletScanYn')
    packYn = json_data.get('packYn')    
    lastLineCode = json_data.get('lastLineCode')
    lastRtid = json_data.get('lastRtid')
    lastParentBoxId = json_data.get('lastParentBoxId')
    lastPalletId = json_data.get('lastPalletId')
    if json_data.get('sDate') is not None:
        sDate = parser.parse(json_data.get('sDate'))
    if json_data.get('eDate') is not None:
        eDate = parser.parse(json_data.get('eDate'))

    if rtid and lineCode:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, rtid = rtid, lineCode = lineCode)    
    elif lastRtid and lastLineCode:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, lastRtid = lastRtid, lastLineCode = lastLineCode)
    elif parentBoxId:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, parentBoxId = parentBoxId)
    elif palletId:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, palletId = palletId)
    elif lastParentBoxId:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, lastParentBoxId = lastParentBoxId)
    elif lastPalletId:
        cp = TdLogisticBox.query.filter_by(companyCode = companyCode, lastPalletId = lastPalletId)

    if json_data.get('sDate') or json_data.get('eDate'):
        cp = cp.filter(TdLogisticBox.dtRegistered >= sDate, TdLogisticBox.dtRegistered <= eDate)
    if boxType:
        cp = cp.filter_by(boxType = boxType)
    if packYn:
        cp = cp.filter_by(packYn = packYn)
    if scanYn:
        cp = cp.filter_by(scanYn = scanYn)
    if palletPackYn:
        cp = cp.filter_by(palletPackYn = palletPackYn)
    if palletScanYn:
        cp = cp.filter_by(palletScanYn = palletScanYn)
    if palletId or palletScanYn == 'Y':
        cp = cp.order_by(TdLogisticBox.dtPalletScan.desc(), TdLogisticBox.boxId.desc())
    else:
        if json_data.get('sDate') or json_data.get('eDate'):
            cp = cp.order_by(TdLogisticBox.dtRegistered.desc(), TdLogisticBox.boxId.desc())[0:1000]
        else:
            cp = cp.order_by(TdLogisticBox.dtScan.desc(), TdLogisticBox.boxId.desc())[0:1000]

    return jsonify({
        'logisticbox': [c.to_json() for c in cp]
    })

@main.route('/api/selLogistictag', methods=['POST'])
def select_logistictag():
    json_data = request.get_json()
    companyCode = json_data.get('companyCode')
    rtid = json_data.get('rtid')
    lineCode = json_data.get('lineCode')
    boxId = json_data.get('boxId')
    scanYn = json_data.get('scanYn')
    packYn = json_data.get('packYn')
    lastLineCode = json_data.get('lastLineCode')
    lastRtid = json_data.get('lastRtid')
    lastBoxId = json_data.get('lastBoxId')
    if json_data.get('sDate') is not None:
        sDate = parser.parse(json_data.get('sDate'))
    if json_data.get('eDate') is not None:
        eDate = parser.parse(json_data.get('eDate'))
    
    if rtid and lineCode:
        cp = TdLogisticTag.query.filter_by(companyCode = companyCode, rtid = rtid, lineCode = lineCode, scanYn = scanYn, packYn = packYn)    
        if boxId:
            cp = cp.filter_by(boxId = boxId)
        if lastBoxId:
            cp = cp.filter_by(lastBoxId = lastBoxId)
    elif lastRtid and lastLineCode:
        cp = TdLogisticTag.query.filter_by(companyCode = companyCode, lastRtid = lastRtid, lastLineCode = lastLineCode, scanYn = scanYn, packYn = packYn)
        if boxId:
            cp = cp.filter_by(boxId = boxId)
        if lastBoxId:
            cp = cp.filter_by(lastBoxId = lastBoxId)
    elif json_data.get('sDate') or json_data.get('eDate'):
        cp = cp.filter(TdLogisticTag.dtRegistered >= sDate, TdLogisticTag.dtRegistered <= eDate)

    cp = cp.order_by(TdLogisticTag.dtScan.desc(), TdLogisticTag.tagId.desc())

    return jsonify({
        'logistictag': [c.to_json() for c in cp]
    })

@main.route('/api/selLogisticpallet', methods=['POST'])
def select_logisticpallet():
    json_data = request.get_json()    
    companyCode = json_data.get('companyCode')
    rtid = json_data.get('rtid')
    lineCode = json_data.get('lineCode')
    scanYn = json_data.get('scanYn')
    lastLineCode = json_data.get('lastLineCode')
    lastRtid = json_data.get('lastRtid')
    if json_data.get('sDate') is not None:
        sDate = parser.parse(json_data.get('sDate'))
    if json_data.get('eDate') is not None:
        eDate = parser.parse(json_data.get('eDate'))

    if rtid and lineCode:
        cp = TdLogisticPallet.query.filter_by(companyCode = companyCode, rtid = rtid, lineCode = lineCode)    
    elif lastRtid and lastLineCode:
        cp = TdLogisticPallet.query.filter_by(companyCode = companyCode, lastRtid = lastRtid, lastLineCode = lastLineCode)

    if json_data.get('sDate') or json_data.get('eDate'):
        cp = cp.filter(TdLogisticPallet.dtRegistered >= sDate, TdLogisticPallet.dtRegistered <= eDate)
    if scanYn:
        cp = cp.filter_by(scanYn = scanYn)
    
    cp = cp.order_by(TdLogisticPallet.dtRegistered.desc(), TdLogisticPallet.palletId.desc())[0:1000]

    return jsonify({
        'logisticpallet': [c.to_json() for c in cp]
    })

@main.route('/api/selLogisticinout', methods=['POST'])
def select_logisticinout():
    json_data = request.get_json()    
    companyCode = json_data.get('companyCode')
    ioRtid = json_data.get('ioRtid')
    ioType = json_data.get('ioType')
    sDate = json_data.get('sDate')
    eDate = json_data.get('eDate')
    ioId = json_data.get('ioId')
    ioSeq = json_data.get('ioSeq')
    scanType = json_data.get('scanType')
    clientType = json_data.get('clientType')
    scanId = json_data.get('scanId')

    if scanId:       
        cp = ThLogisticInout.query.filter_by(companyCode = companyCode, scanId = scanId)
        if ioType:
            cp = cp.filter_by(ioType = ioType)
        if ioRtid:
            cp = cp.filter_by(ioRtid = ioRtid)
        cp = cp.order_by(ThLogisticInout.dtRegistered.asc(), ThLogisticInout.ioId.asc())        
    else:
        if ioId:
            cp = ThLogisticInout.query.filter_by(companyCode = companyCode, ioId = ioId)    
        elif ioRtid and ioType and sDate and eDate:
            sDate = sDate[:4] + '-' + sDate[4:6] + '-' + sDate[-2:] + ' 00:00:00'
            eDate = eDate[:4] + '-' + eDate[4:6] + '-' + eDate[-2:] + ' 23:59:59'
            cp = ThLogisticInout.query.filter(ThLogisticInout.companyCode == companyCode, ThLogisticInout.ioRtid == ioRtid \
                                            , ThLogisticInout.ioType == ioType, ThLogisticInout.dtRegistered >= sDate, ThLogisticInout.dtRegistered <= eDate)
        if ioSeq:
            cp = cp.filter_by(ioSeq = ioSeq)
        if scanType:
            cp = cp.filter_by(scanType = scanType)
        if clientType:
            cp = cp.filter_by(clientType = clientType)        
        cp = cp.order_by(ThLogisticInout.dtRegistered.desc())[0:1000]

    return jsonify({
        'logisticinout': [c.to_json() for c in cp]
    })

@main.route('/api/chkPackingScan', methods=['POST'])
def check_packingscan():
    json_data = request.get_json()
    scanData = json_data.get('scanData')
    procType = json_data.get('procType')
    rtid = json_data.get('rtid')
    boxType = scanData[:1]
    chk = None

    if boxType in ('S', 'M', 'L'):
        chk = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), boxId = scanData, boxType = boxType).first()    
    elif boxType == 'P':
        chk = TdLogisticPallet.query.filter_by(companyCode = json_data.get('companyCode'), palletId = scanData, boxType = boxType).first()
    else:
        boxType = 'T'
        scanData = scanData.replace(' ', '')
        scanData = scanData.replace('%2B', '+')
        scanData = scanData.replace('%2F', '/')
        scanData = scanData.replace('%25', '%')
        scanData = scanData.replace('%3D%3D', '==')
        chk = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), scanId = scanData).first()

    if len(scanData) < 10:
        return jsonify({
                'result': {
                    'code': 8507,
                    # 'msg' : 'It is not a type of barcode that can be packaged.'
                    'msg' : gettext('8507')
                }
            })
    
    if procType == 'S':        
        if boxType in ('S', 'M', 'L', 'P'):
            return jsonify({
                'result': {
                    'code': 8507,
                    # 'msg' : 'It is not a type of barcode that can be packaged.'
                    'msg' : gettext('8507')
                }
            })

        if chk is not None:            
            if chk.packYn == 'Y':
                return jsonify({
                    'result': {
                        'code': 8505,
                        # 'msg' : 'It is already packed.'
                        'msg' : gettext('8505')
                    }
                })
            
            if chk.scanYn == 'Y':
                return jsonify({
                    'result': {
                        'code': 8506,
                        # 'msg' : 'It is already scanned.'
                        'msg' : gettext('8506')
                    }
                })
        
        if chk is None:
            return jsonify({
                'result': {
                    'code': 1000,
                    'msg' : gettext('1000')
                }
            })
    else:

        if (rtid is not None) and (chk is not None):
            if chk.lastRtid != rtid:
                return jsonify({
                    'result': {
                        'code': 8508,
                        # 'msg' : 'Inventory does not exist'
                        'msg' : gettext('8508')
                    }
                })

        if procType == 'M' and boxType != 'S':
            return jsonify({
                    'result': {
                        'code': 8507,
                        # 'msg' : 'It is not a type of barcode that can be packaged.'
                        'msg' : gettext('8507')
                    }
                })
        
        if procType == 'L' and boxType != 'M':
            return jsonify({
                    'result': {
                        'code': 8507,
                        # 'msg' : 'It is not a type of barcode that can be packaged.'
                        'msg' : gettext('8507')
                    }
                })

        if procType == 'P' and boxType not in ('S', 'M', 'L'):
            return jsonify({
                    'result': {
                        'code': 8507,
                        # 'msg' : 'It is not a type of barcode that can be packaged.'
                        'msg' : gettext('8507')
                    }
                })

        if chk is None:
            return jsonify({
                'result': {
                    'code': 8504,
                    # 'msg' : 'It is nonexistent data.'
                    'msg' : gettext('8504')
                }
            })        
        
        if procType == 'P':
            if chk.palletPackYn == 'Y':
                return jsonify({
                    'result': {
                        'code': 8505,
                        # 'msg' : 'It is already packed.'
                        'msg' : gettext('8505')
                    }
                })

            if chk.palletScanYn == 'Y' or (chk.scanYn == 'Y' and chk.packYn == 'N'):
                return jsonify({
                    'result': {
                        'code': 8506,
                        # 'msg' : 'It is already scanned.'
                        'msg' : gettext('8506')
                    }
                })
        else:
            if chk.palletPackYn == 'Y' or chk.packYn == 'Y':
                return jsonify({
                    'result': {
                        'code': 8505,
                        # 'msg' : 'It is already packed.'
                        'msg' : gettext('8505')
                    }
                })

            if chk.palletScanYn == 'Y' or chk.scanYn == 'Y':
                return jsonify({
                    'result': {
                        'code': 8506,
                        # 'msg' : 'It is already scanned.'
                        'msg' : gettext('8506')
                    }
                })
        
        return jsonify({
            'result': {
                'code': 1000,
                'msg' : gettext('1000')
            },
            'check': chk.to_json()
        })

@main.route('/api/insLogistictag', methods=['POST'])
def insert_logistictag():
    json_data = request.get_json()

    scanId = json_data.get('scanId')
    scanId = scanId.replace(' ', '')
    scanId = scanId.replace('%2B', '+')
    scanId = scanId.replace('%2F', '/')
    scanId = scanId.replace('%25', '%')
    scanId = scanId.replace('%3D%3D', '==')

    chk = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), scanId = scanId).first()
    if chk is not None:
        return jsonify({
            'result': {
                'code': 8503,
                # 'msg' : 'It is already registered data.'
                'msg' : gettext('8503')
            }            
        })
    
    holotag = TdHolotag.query.filter_by(companyCode = json_data.get('companyCode'), code = json_data.get('tagCode')).first()

    findKey = 'T' + json_data.get('lineCode')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 1
    sel = TdLogisticTag.query.filter(TdLogisticTag.companyCode == json_data.get('companyCode'), TdLogisticTag.tagId.like(findKey + '%')).order_by(TdLogisticTag.tagId.desc()).first()
    if sel is not None:
        seq = int(sel.tagId[-6:]) + 1
    
    tagId = findKey + (6 - len(str(seq))) * '0' + str(seq)

    tag = TdLogisticTag(companyCode=json_data.get('companyCode'),
                        rtid=json_data.get('rtid'),
                        lineCode=json_data.get('lineCode'),
                        tagId=tagId,
                        tagCode=json_data.get('tagCode'),
                        scanYn='Y',
                        dtScan=datetime.now(),
                        packYn='N',
                        scanId=scanId,
                        random=None,
                        boxId=None,
                        tagQty=holotag.tagStdQty,
                        lastLineCode=json_data.get('lineCode'),
                        lastRtid=json_data.get('rtid'),                        
                        registrant=json_data.get('registrant'),
                        dtRegistered=datetime.now(),
                        modifier=None,
                        dtModified=None)
    
    db.session.add(tag)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logistictag': tag.to_json()
    })

@main.route('/api/updLogistictag', methods=['POST'])
def update_logistictag():
    json_data = request.get_json()

    tag = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), tagId = json_data.get('tagId')).first()
    if tag is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    tag.companyCode=json_data.get('companyCode') or tag.companyCode
    tag.rtid=json_data.get('rtid') or tag.rtid
    tag.lineCode=json_data.get('lineCode') or tag.lineCode
    tag.tagCode=json_data.get('tagCode') or tag.tagCode
    tag.packYn=json_data.get('packYn') or tag.packYn
    tag.scanId=json_data.get('scanId') or tag.scanId
    tag.random=json_data.get('random') or tag.random
    tag.boxId=json_data.get('boxId') or tag.boxId
    tag.tagQty=json_data.get('tagQty') or tag.tagQty
    tag.lastLineCode=json_data.get('lastLineCode') or tag.lastLineCode
    tag.lastRtid=json_data.get('lastRtid') or tag.lastRtid
    tag.lastBoxId=json_data.get('lastBoxId') or tag.lastBoxId
    tag.modifier=json_data.get('modifier') or tag.modifier
    tag.dtModified=datetime.now()

    db.session.add(tag)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logistictag': tag.to_json()
    })

@main.route('/api/delLogistictag', methods=['POST'])
def delete_logistictag():
    json_data = request.get_json()

    tag = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), tagId = json_data.get('tagId')).first()
    if tag is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })    

    db.session.delete(tag)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logistictag': tag.to_json()
    })

@main.route('/api/insLogisticbox', methods=['POST'])
def insert_logisticbox():
    # json_data = request.get_json()                    # 제어문자(\t \r \n) 파싱 안됨...
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    
    findKey = json_data.get('boxType') + json_data.get('lineCode')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 1
    sel = TdLogisticBox.query.filter(TdLogisticBox.companyCode == json_data.get('companyCode'), TdLogisticBox.boxId.like(findKey + '%')).order_by(TdLogisticBox.boxId.desc()).first()
    if sel is not None:
        seq = int(sel.boxId[-6:]) + 1
    
    boxId = findKey + (6 - len(str(seq))) * '0' + str(seq)
    packQty = 0
    box = TdLogisticBox(boxId=boxId,
                        parentBoxId=json_data.get('parentBoxId'),
                        companyCode=json_data.get('companyCode'),
                        rtid=json_data.get('rtid'),
                        lineCode=json_data.get('lineCode'),
                        boxType=json_data.get('boxType'),
                        dispTagCode=json_data.get('dispTagCode'),
                        dispTagName=json_data.get('dispTagName'),
                        dispProdDate=json_data.get('dispProdDate'),
                        dispLotNo=json_data.get('dispLotNo'),
                        dispQty=json_data.get('dispQty'),
                        dispRemark=json_data.get('dispRemark'),
                        tagCode=json_data.get('tagCode'),
                        packYn='N',
                        palletId=None,
                        lastLineCode=json_data.get('lineCode'),
                        lastRtid=json_data.get('rtid'),
                        registrant=json_data.get('registrant'),
                        dtRegistered=datetime.now(),
                        modifier=None,
                        dtModified=None)
    db.session.add(box)

    json_data_tag = json_data.get('logistictag')
    if json_data_tag is not None:
        for t in json_data_tag:            
            ctag = TdLogisticTag.query.filter_by(tagId = t['tagId']).first()
            if ctag is not None:
                ctag.boxId = boxId
                ctag.packYn = 'Y'
                ctag.lastBoxId= boxId
                ctag.modifier = json_data.get('registrant')
                ctag.dtModified = datetime.now()
                db.session.add(ctag)

        packQty = packQty + len(json_data_tag)

    json_data_box = json_data.get('logisticbox')
    if json_data_box is not None:
        for t in json_data_box:            
            cbox = TdLogisticBox.query.filter_by(boxId = t['boxId']).first()
            if cbox is not None:
                cbox.parentBoxId = boxId
                cbox.packYn = 'Y'
                cbox.lastParentBoxId = boxId
                cbox.modifier = json_data.get('registrant')
                cbox.dtModified = datetime.now()
                db.session.add(cbox)        
        
        packQty = packQty + len(json_data_box)        

    box.packQty = packQty

    db.session.commit()

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        }
        ,
        'logisticbox': box.to_json()
    })

@main.route('/api/updLogisticbox', methods=['POST'])
def update_logisticbox():
    json_data = request.get_json()

    box = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), boxId = json_data.get('boxId')).first()
    if box is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
 
    box.boxType=json_data.get('boxType') or box.boxType
    box.scanYn=json_data.get('scanYn') or box.scanYn
    if json_data.get('scanYn') == "Y":
        box.dtScan=datetime.now()
    elif json_data.get('scanYn') == "N":
        box.dtScan=None
    box.palletScanYn=json_data.get('palletScanYn') or box.palletScanYn
    if json_data.get('palletScanYn') == "Y":
        box.dtPalletScan=datetime.now()
    elif json_data.get('palletScanYn') == "N":
        box.dtPalletScan=None 
    box.lastLineCode=json_data.get('lastLineCode') or box.lastLineCode 
    box.modifier=json_data.get('modifier') or box.modifier
    box.dtModified=datetime.now()

    db.session.add(box)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticbox': box.to_json()
    })

@main.route('/api/delLogisticbox', methods=['POST'])
def delete_logisticbox():
    json_data = request.get_json()

    box = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), boxId = json_data.get('boxId')).first()
    if box is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })    

    db.session.delete(box)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logistictag': box.to_json()
    })

@main.route('/api/insLogisticpallet', methods=['POST'])
def insert_logisticpallet():
    lang = get_locale()
    # json_data = request.get_json()                    # 제어문자(\t \r \n) 파싱 안됨...
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...

    if lang == 'ko':
        sqlLangIdx = 1
    elif lang == 'en':
        sqlLangIdx = 2
    else:
        sqlLangIdx = 3
    
    findKey = 'P' + json_data.get('lineCode')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 1
    sel = TdLogisticPallet.query.filter(TdLogisticPallet.companyCode == json_data.get('companyCode'), TdLogisticPallet.palletId.like(findKey + '%')).order_by(TdLogisticPallet.palletId.desc()).first()
    if sel is not None:
        seq = int(sel.palletId[-6:]) + 1
    
    palletId = findKey + (6 - len(str(seq))) * '0' + str(seq)

    plt = TdLogisticPallet(palletId=palletId,
                           companyCode=json_data.get('companyCode'),
                           rtid=json_data.get('rtid'),
                           lineCode=json_data.get('lineCode'),
                           dispProdDate=json_data.get('dispProdDate'),
                           dispLotNo=json_data.get('dispLotNo'),
                           dispRemark=json_data.get('dispRemark'),
                           lastLineCode=json_data.get('lineCode'),
                           lastRtid=json_data.get('rtid'),
                           registrant=json_data.get('registrant'),
                           dtRegistered=datetime.now(),
                           modifier=None,
                           dtModified=None)
    db.session.add(plt)

    chkcnt = 0
    tagCode = None
    json_data_box = json_data.get('logisticbox')
    if json_data_box is not None:
        for t in json_data_box:                        
            cbox = TdLogisticBox.query.filter_by(boxId = t['boxId']).first()
            if cbox is not None:
                if chkcnt == 0:
                    plt.tagCode = cbox.tagCode

                cbox.palletId = palletId
                cbox.palletPackYn = 'Y' 
                cbox.lastPalletId = palletId               
                cbox.modifier = json_data.get('registrant')
                cbox.dtModified = datetime.now()
                db.session.add(cbox)
                chkcnt += 1
    
    # detail = db.session.query(TdLogisticBox.tagCode, TdHolotag.name_kr, TdHolotag.name_en, TdHolotag.name_zh, func.count(TdLogisticBox.tagCode)).group_by(TdLogisticBox.tagCode) \
    #                         .filter_by(companyCode = json_data.get('companyCode'), palletId = palletId) \
    #                         .order_by(TdLogisticBox.tagCode.asc())

    detail = db.session.query(TdLogisticBox.tagCode, TdHolotag.name_kr, TdHolotag.name_en, TdHolotag.name_zh, func.count(TdLogisticBox.tagCode)) \
                        .filter(TdLogisticBox.companyCode == TdHolotag.companyCode) \
                        .filter(TdLogisticBox.tagCode == TdHolotag.code) \
                        .filter_by(companyCode = json_data.get('companyCode'), palletId = palletId) \
                        .group_by(TdLogisticBox.tagCode) \
                        .order_by(TdLogisticBox.tagCode.asc())


    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticpallet': plt.to_json(),
        'logisticpalletdetail': [{'tagCode': c[0],'tagName': c[sqlLangIdx],'packQty': c[4]} for c in detail]
    })

@main.route('/api/updLogisticpallet', methods=['POST'])
def update_logisticpallet():
    json_data = request.get_json()

    plt = TdLogisticPallet.query.filter_by(companyCode = json_data.get('companyCode'), palletId = json_data.get('palletId')).first()
    if plt is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    
    plt.companyCode=json_data.get('companyCode') or plt.companyCode
    plt.rtid=json_data.get('rtid') or plt.rtid
    plt.lineCode=json_data.get('lineCode') or plt.lineCode
    plt.dispProdDate=json_data.get('dispProdDate') or plt.dispProdDate
    plt.dispLotNo=json_data.get('dispLotNo') or plt.dispLotNo
    plt.dispRemark=json_data.get('dispRemark') or plt.dispRemark
    plt.lastLineCode=json_data.get('lastLineCode') or plt.lastLineCode
    plt.lastRtid=json_data.get('lastRtid') or plt.lastRtid    
    plt.modifier=json_data.get('modifier') or plt.modifier
    plt.dtModified=datetime.now()

    db.session.add(plt)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticpallet': plt.to_json()
    })    

@main.route('/api/delLogisticpallet', methods=['POST'])
def delete_logisticpallet():
    json_data = request.get_json()

    plt = TdLogisticPallet.query.filter_by(companyCode = json_data.get('companyCode'), palletId = json_data.get('palletId')).first()
    if plt is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    boxs = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), palletId = json_data.get('palletId'))
    if boxs:
        boxs.update({TdLogisticBox.lastRtid: TdLogisticBox.rtid, TdLogisticBox.palletScanYn: 'N', \
            TdLogisticBox.palletPackYn: 'N', TdLogisticBox.dtPalletScan: None, TdLogisticBox.palletId: None, TdLogisticBox.lastPalletId: None, TdLogisticBox.dtModified: datetime.now()})    

    db.session.delete(plt)
    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticpallet': plt.to_json()
    })

@main.route('/api/insLogisticinout', methods=['POST'])
def insert_logisticinout():    
    # json_data = request.get_json()                    # 제어문자(\t \r \n) 파싱 안됨...
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    clientType = json_data.get('clientType')
    ioType = json_data.get('ioType')
    scanId = json_data.get('scanId')
    ioFlag = None
    ioQty = 0
    scanFlag = scanId[:1]
    lastRtid = None

    if ioType == 'OUT':
        ioFlag = 'OT'
    elif ioType == 'IN':
        ioFlag = 'IN'

    if scanFlag in ('S', 'M', 'L'):
        chk = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), boxId = scanId).first()            
    elif scanFlag == 'P':
        chk = TdLogisticPallet.query.filter_by(companyCode = json_data.get('companyCode'), palletId = scanId).first()
    else:
        scanFlag = 'T'
        scanId = scanId.replace(' ', '')
        scanId = scanId.replace('%2B', '+')
        scanId = scanId.replace('%2F', '/')
        scanId = scanId.replace('%25', '%')
        scanId = scanId.replace('%3D%3D', '==')
        chk = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), scanId = scanId).first()

    if chk is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })
    else:
        if scanFlag in ('S', 'M', 'L'):
            if (chk.scanYn == 'Y' and chk.packYn == 'N') or (chk.palletScanYn == 'Y' and chk.palletPackYn == 'N'):
                return jsonify({
                    'result': {
                        'code': 8510,
                        # 'msg' : 'This box is being packed.'
                        'msg' : gettext('8510')
                    }
                })
        elif scanFlag == 'T':
            if (chk.scanYn == 'Y' and chk.packYn == 'N'):
                return jsonify({
                    'result': {
                        'code': 8511,
                        # 'msg' : 'This tag is being packed.'
                        'msg' : gettext('8511')
                    }
                })              

    if ioFlag == 'OT':
        lastRtid = None
        if chk.lastRtid != json_data.get('ioRtid'):
            return jsonify({
                'result': {
                    'code': 8508,
                    # 'msg' : 'Inventory does not exist'
                    'msg' : gettext('8508')
                }
            })
    
    if ioFlag == 'IN':
        lastRtid = json_data.get('ioRtid')
        if chk.lastRtid is not None:
            if chk.lastRtid == json_data.get('ioRtid'):
                return jsonify({
                    'result': {
                        'code': 8509,
                        # 'msg' : 'Inventory already exists.'
                        'msg' : gettext('8509')
                    }
                })
            else:
                return jsonify({
                'result': {
                    'code': 8508,
                    # 'msg' : 'Inventory does not exist'
                    'msg' : gettext('8508')
                }
            })
    
    findKey = ioFlag + json_data.get('ioRtid')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 1
    sel = ThLogisticInout.query.filter(ThLogisticInout.companyCode == json_data.get('companyCode'), ThLogisticInout.ioId.like(findKey + '%')).order_by(ThLogisticInout.ioId.desc()).first()
    if sel is not None:
        seq = int(sel.ioId[-8:]) + 1
    
    ioId = findKey + (8 - len(str(seq))) * '0' + str(seq)

    inout = ThLogisticInout(companyCode=json_data.get('companyCode'),
                           ioType=json_data.get('ioType'),
                           ioDate=datetime.now().strftime('%Y%m%d'),
                           ioId=ioId,
                           ioSeq=1,
                           scanId=json_data.get('scanId'),                           
                           ioRtid=json_data.get('ioRtid'),
                           scanType=scanFlag,
                           clientType=json_data.get('clientType'),
                           deviceID=json_data.get('deviceID'),
                           osType=json_data.get('osType'),                         
                           registrant=json_data.get('registrant'),
                           dtRegistered=datetime.now(),
                           modifier=None,
                           dtModified=None)

    if scanFlag in ('S', 'M', 'L'):
        inout.boxId = scanId
    elif scanFlag == 'P':
        inout.palletId = scanId
    elif scanFlag == 'T':
        inout.tagId = chk.tagId

    if clientType == 'L':
        rt = TdRetailer.query.filter_by(companyCode = json_data.get('companyCode'), rtid = json_data.get('ioRtid')).first()        
        if rt:
            inout.latitude = rt.latitude
            inout.longitude = rt.longitude 

    # # # hierarchy = db.session.query(TdLogisticBox, literal(0).label('level'))\
    # # #                         .filter(TdLogisticBox.parentBoxId == scanId)\
    # # #                         .cte(name="hierarchy", recursive=True)           
    # # # parent = aliased(hierarchy, name="p")
    # # # children = aliased(TdLogisticBox, name="c")
    # # # hierarchy = hierarchy.union_all(db.session.query(children,(parent.c.level + 1).label("level")).filter(children.parentBoxId == parent.c.boxId))
    # # # result = db.session.query(TdLogisticBox, hierarchy.c.level)\
    # # #         .select_entity_from(hierarchy).all()

    detail = None
    if scanFlag == 'P':
        chk.lastRtid = lastRtid
        chk.modifier = json_data.get('registrant')
        chk.dtModified = datetime.now()

        cbox1s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastPalletId = scanId)
        if cbox1s is not None:
            cbox1s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('registrant'), TdLogisticBox.dtModified: datetime.now()})
            for cbox1 in cbox1s:

                cbox2s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox1.boxId)
                if cbox2s is not None:
                    cbox2s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('registrant'), TdLogisticBox.dtModified: datetime.now()})
                    for cbox2 in cbox2s:

                        cbox3s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox2.boxId)                        
                        if cbox3s is not None:
                            cbox3s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('registrant'), TdLogisticBox.dtModified: datetime.now()})
                            for cbox3 in cbox3s:

                                ctag4s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox3.boxId)
                                if ctag4s is not None:
                                    ioQty = ioQty + ctag4s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

                        ctag3s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox2.boxId)
                        if ctag3s is not None:
                            ioQty = ioQty + ctag3s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

                ctag2s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox1.boxId)
                if ctag2s is not None:
                    ioQty = ioQty + ctag2s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

        inout.ioQty =  ioQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)        

    if scanFlag in ('S', 'M', 'L'):
        chk.lastRtid = lastRtid
        # if ioFlag == 'OT':
        chk.lastParentBoxId = None
        chk.lastPalletId = None
        chk.modifier = json_data.get('registrant')
        chk.dtModified = datetime.now()
        
        cbox2s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = scanId)        
        if cbox2s is not None:
            cbox2s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('registrant'), TdLogisticBox.dtModified: datetime.now()})
            for cbox2 in cbox2s:

                cbox3s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox2.boxId)
                if cbox3s is not None:
                    cbox3s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('registrant'), TdLogisticBox.dtModified: datetime.now()})
                    for cbox3 in cbox3s:                        

                        ctag4s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox3.boxId)
                        if ctag4s is not None:
                            ioQty = ioQty + ctag4s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

                ctag3s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox2.boxId)
                if ctag3s is not None:
                    ioQty = ioQty + ctag3s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

        ctag2s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = scanId)
        if ctag2s is not None:
            ioQty = ioQty + ctag2s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('registrant'), TdLogisticTag.dtModified: datetime.now()})

        inout.ioQty =  ioQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)

    if scanFlag == 'T':
        chk.lastRtid = lastRtid
        # if ioFlag == 'OT':
        chk.lastBoxId = None
        chk.modifier = json_data.get('registrant')
        chk.dtModified = datetime.now()        
        inout.ioQty =  chk.tagQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)

    db.session.add(inout)

    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticinout': inout.to_json()
    })

@main.route('/api/insAppLogisticinout', methods=['POST'])
def insert_applogisticinout():
    lang = get_locale()
    osType = None
    header = request.headers.get('BSRD-INFO')
    if header:
        headers = header.split(';')
        osType = headers[1]

    # json_data = request.get_json()                    # 제어문자(\t \r \n) 파싱 안됨...
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    clientType = json_data.get('clientType')
    ioType = json_data.get('ioType')
    scanId = json_data.get('scanId')
    gps = json_data.get('gps')    
    ioFlag = None
    ioQty = 0
    scanFlag = scanId[:1]
    lastRtid = None

    tagCode = None
    tagName = None

    if ioType == 'OUT':
        ioFlag = 'OT'
    elif ioType == 'IN':
        ioFlag = 'IN'

    if scanFlag in ('S', 'M', 'L'):
        chk = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), boxId = scanId).first()            
    elif scanFlag == 'P':
        chk = TdLogisticPallet.query.filter_by(companyCode = json_data.get('companyCode'), palletId = scanId).first()
    else:
        scanFlag = 'T'
        scanId = scanId.replace(' ', '')
        scanId = scanId.replace('%2B', '+')
        scanId = scanId.replace('%2F', '/')
        scanId = scanId.replace('%25', '%')
        scanId = scanId.replace('%3D%3D', '==')
        chk = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), scanId = scanId).first()

    if chk is None:
        return jsonify({
            'result': {
                'code': 8504,
                # 'msg' : 'It is nonexistent data.'
                'msg' : gettext('8504')
            }            
        })

    if ioFlag == 'OT':
        lastRtid = None
        if chk.lastRtid != json_data.get('retailerId'):
            return jsonify({
                'result': {
                    'code': 8508,
                    # 'msg' : 'Inventory does not exist'
                    'msg' : gettext('8508')
                }
            })
    
    if ioFlag == 'IN':
        lastRtid = json_data.get('retailerId')
        if chk.lastRtid is not None:
            if chk.lastRtid == json_data.get('retailerId'):
                return jsonify({
                    'result': {
                        'code': 8509,
                        # 'msg' : '이미 재고가 존재 합니다.'
                        'msg' : gettext('8509')
                    }
                })
            else:
                return jsonify({
                'result': {
                    'code': 8508,
                    # 'msg' : 'Inventory does not exist'
                    'msg' : gettext('8508')
                }
            })
    
    findKey = ioFlag + json_data.get('retailerId')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 1
    sel = ThLogisticInout.query.filter(ThLogisticInout.companyCode == json_data.get('companyCode'), ThLogisticInout.ioId.like(findKey + '%')).order_by(ThLogisticInout.ioId.desc()).first()
    if sel is not None:
        seq = int(sel.ioId[-8:]) + 1
    
    ioId = findKey + (8 - len(str(seq))) * '0' + str(seq)

    inout = ThLogisticInout(companyCode=json_data.get('companyCode'),
                           ioType=json_data.get('ioType'),
                           ioDate=datetime.now().strftime('%Y%m%d'),
                           ioId=ioId,
                           ioSeq=1,
                           scanId=json_data.get('scanId'),                           
                           ioRtid=json_data.get('retailerId'),
                           scanType=scanFlag,
                           clientType=json_data.get('clientType'),
                           deviceID=json_data.get('pushToken'),
                           osType=osType,                         
                           registrant=json_data.get('userId'),
                           dtRegistered=datetime.now(),
                           modifier=None,
                           dtModified=None)

    if scanFlag in ('S', 'M', 'L'):
        inout.boxId = scanId
    elif scanFlag == 'P':
        inout.palletId = scanId
    elif scanFlag == 'T':
        inout.tagId = chk.tagId

    if clientType == 'L':
        rt = TdRetailer.query.filter_by(companyCode = json_data.get('companyCode'), rtid = json_data.get('retailerId')).first()        
        if rt:
            inout.latitude = rt.latitude
            inout.longitude = rt.longitude
    else:
        try:
            if gps is not None:
                cipher = CipherAgent()                
                inout.latitude = cipher.encryptAndEncodingBase64(str(gps.get('latitude')))
                inout.longitude = cipher.encryptAndEncodingBase64(str(gps.get('longitude')))
        except:
            pass
    
    if scanFlag == 'P':
        chk.lastRtid = lastRtid
        chk.modifier = json_data.get('userId')
        chk.dtModified = datetime.now()

        cbox1s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastPalletId = scanId)
        if cbox1s is not None:
            cbox1s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('userId'), TdLogisticBox.dtModified: datetime.now()})
            for cbox1 in cbox1s:

                cbox2s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox1.boxId)
                if cbox2s is not None:
                    cbox2s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('userId'), TdLogisticBox.dtModified: datetime.now()})
                    for cbox2 in cbox2s:

                        cbox3s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox2.boxId)                        
                        if cbox3s is not None:
                            cbox3s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('userId'), TdLogisticBox.dtModified: datetime.now()})
                            for cbox3 in cbox3s:

                                ctag4s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox3.boxId)
                                if ctag4s is not None:
                                    ioQty = ioQty + ctag4s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

                        ctag3s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox2.boxId)
                        if ctag3s is not None:
                            ioQty = ioQty + ctag3s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

                ctag2s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox1.boxId)
                if ctag2s is not None:
                    ioQty = ioQty + ctag2s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

        inout.ioQty =  ioQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)        

    if scanFlag in ('S', 'M', 'L'):
        chk.lastRtid = lastRtid
        chk.lastParentBoxId = None
        chk.lastPalletId = None
        chk.modifier = json_data.get('userId')
        chk.dtModified = datetime.now()

        cbox2s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = scanId)        
        if cbox2s is not None:
            cbox2s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('userId'), TdLogisticBox.dtModified: datetime.now()})            
            for cbox2 in cbox2s:

                cbox3s = TdLogisticBox.query.filter_by(companyCode = json_data.get('companyCode'), lastParentBoxId = cbox2.boxId)
                if cbox3s is not None:
                    cbox3s.update({TdLogisticBox.lastRtid: lastRtid, TdLogisticBox.modifier: json_data.get('userId'), TdLogisticBox.dtModified: datetime.now()})
                    for cbox3 in cbox3s:                        

                        ctag4s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox3.boxId)
                        if ctag4s is not None:
                            ioQty = ioQty + ctag4s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

                ctag3s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = cbox2.boxId)
                if ctag3s is not None:
                    ioQty = ioQty + ctag3s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

        ctag2s = TdLogisticTag.query.filter_by(companyCode = json_data.get('companyCode'), lastBoxId = scanId)
        if ctag2s is not None:
            ioQty = ioQty + ctag2s.update({TdLogisticTag.lastRtid: lastRtid, TdLogisticTag.modifier: json_data.get('userId'), TdLogisticTag.dtModified: datetime.now()})

        inout.ioQty =  ioQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)

    if scanFlag == 'T':
        chk.lastRtid = lastRtid
        chk.lastBoxId = None
        chk.modifier = json_data.get('userId')
        chk.dtModified = datetime.now()
        inout.ioQty =  chk.tagQty
        inout.tagCode = chk.tagCode
        db.session.add(chk)

    db.session.add(inout)

    tagCode = chk.tagCode
    holotag = TdHolotag.query.filter_by(companyCode = json_data.get('companyCode'), code = tagCode).first()
    if lang == 'ko':
        tagName = holotag.name_kr
    elif lang == 'en':
        tagName = holotag.name_en
    else:
        tagName = holotag.name_zh

    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logisticinout': inout.to_json_app(tagName)
    })

@main.route('/api/selLogisticTracking', methods=['POST', 'GET'])
def select_LogisticTracking():
    lang = get_locale()
    json_data = request.get_json()

    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    scanId = json_data.get('scanId')    
    scanFlag = scanId[:1]
    
    if lang == 'ko':
        sqlLangName = 'name_kr'
    elif lang == 'en':
        sqlLangName = 'name_en'
    else:
        sqlLangName = 'name_zh'

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    if scanFlag in ('S', 'M', 'L'):
        sql =  "select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, '' as lineCode, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode from th_logistic_inout where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, ioRtid as rtid, '' as lineCode, ioType as procType, ioQty, x.scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode \
                    from th_logistic_inout x \
                    inner join ( \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                        union all \
                        select palletId as scanId from td_logistic_pallet where palletId in ( \
                            select palletId from ( \
                                select * from td_logistic_box where boxId = '" + scanId + "' \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                            ) t \
                        ) \
                    ) y \
                    on y.scanId = x.scanId \
                    and dtRegistered < ifnull((select min(dtRegistered) from th_logistic_inout where scanId = '" + scanId + "'), dtRegistered + INTERVAL 1 SECOND) \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, rtid, lineCode, 'CREATE' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId = '" + scanId + "' \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                    union all \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'PACKING' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered, p1.tagCode  \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select x.* from td_logistic_box x \
                        inner join ( \
                            select palletId from td_logistic_box where boxId = '" + scanId + "' \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId ='" + scanId + "') \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                        ) y \
                        on y.palletId = x.palletId \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
                order by dtRegistered asc;"

    elif scanFlag in ('P'):
        sql =  "select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, '' as lineCode, '' as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered \
                        , (select tagCode from td_logistic_box where palletId = '" + scanId + "' order by dtPalletScan limit 1) as tagCode \
                    from th_logistic_inout x1 \
                    where scanId = '" + scanId + "' \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, d." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'CREATE' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered , p2.tagCode \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select * from td_logistic_box where palletId = '" + scanId + "' \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                inner join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                left outer join td_line d \
                on a.lineCode = d.lineCode \
                order by dtRegistered asc;"

    else:
        scanFlag = 'T'
        scanId = scanId.replace(' ', '')
        scanId = scanId.replace('%2B', '+')
        scanId = scanId.replace('%2F', '/')
        scanId = scanId.replace('%25', '%')
        scanId = scanId.replace('%3D%3D', '==')

        sql =  "select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, '' as lineCode, '' as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode from th_logistic_inout where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, x.scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode \
                    from th_logistic_inout x \
                    inner join ( \
                        select boxId as scanId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                        union all \
                        select palletId as scanId from td_logistic_pallet where palletId in ( \
                            select palletId from ( \
                                select * from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                            ) t \
                        ) \
                    ) y \
                    on y.scanId = x.scanId \
                    and dtRegistered < ifnull((select min(dtRegistered) from th_logistic_inout where scanId = '" + scanId + "'), dtRegistered + INTERVAL 1 SECOND) \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as reteailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, rtid, lineCode, 'CREATE' as procType, scanId, 'T' as scanType, tagQty as packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_tag where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                    union all \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'PACKING' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered, p1.tagCode \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select x.* \
                        from td_logistic_box x \
                        inner join ( \
                            select palletId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                        ) y \
                        on y.palletId = x.palletId \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                inner join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
                order by dtRegistered asc;"

    curs.execute(sql)
    trackingList = list(curs.fetchall())
    conn.close()

    cipher = CipherAgent()

    for index, tr in enumerate(trackingList):
        tr_dict = dict()
        tr_dict['companyCode'] = tr[0]
        tr_dict['retailerId'] = tr[1]
        tr_dict['retailerName'] = tr[2]
        tr_dict['lineCode'] = tr[3]
        tr_dict['lineName'] = tr[4]
        tr_dict['procType'] = tr[5]
        tr_dict['scanId'] = tr[6]
        tr_dict['qty'] = tr[7]
        tr_dict['scanType'] = tr[8]
        tr_dict['clientType'] = tr[9]
        tr_dict['latitude'] = cipher.decodingBase64AndDecrypt(str(tr[10]))
        tr_dict['longitude'] = cipher.decodingBase64AndDecrypt(str(tr[11]))
        tr_dict['dtRegistered'] = tr[12]
        tr_dict['tagCode'] = tr[13]
        tr_dict['tagName'] = tr[14]

        trackingList[index] = tr_dict

    return jsonify({'trackingList': trackingList})



@main.route('/api/selAppLogisticTracking', methods=['POST', 'GET'])
def select_LogisticAppTracking():    
    lang = get_locale()
    # json_data = request.get_json()

    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    scanId = json_data.get('scanId')
    lastYn = json_data.get('lastYn')
    scanFlag = scanId[:1]
    
    if lang == 'ko':
        sqlLangName = 'name_kr'
    elif lang == 'en':
        sqlLangName = 'name_en'
    else:
        sqlLangName = 'name_zh'

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    if scanFlag in ('S', 'M', 'L'):
        sql =  " \
        select companyCode, retailerId, retailerName, lineCode, lineName, procType, scanId, qty, scanType, clientType, latitude, longitude, dtRegistered, tagCode, tagName \
        from ( \
            select r1.*, \
                (CASE @vPartition WHEN r1.retailerId THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) rnum, \
                (@vPartition:=r1.retailerId) vPartition \
            from ( \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, '' as lineCode, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode from th_logistic_inout where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, ioRtid as rtid, '' as lineCode, ioType as procType, ioQty, x.scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode \
                    from th_logistic_inout x \
                    inner join ( \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                        union all \
                        select palletId as scanId from td_logistic_pallet where palletId in ( \
                            select palletId from ( \
                                select * from td_logistic_box where boxId = '" + scanId + "' \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                            ) t \
                        ) \
                    ) y \
                    on y.scanId = x.scanId \
                    and dtRegistered < ifnull((select min(dtRegistered) from th_logistic_inout where scanId = '" + scanId + "'), dtRegistered + INTERVAL 1 SECOND) \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, rtid, lineCode, 'CREATE' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId = '" + scanId + "' \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                    union all \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'PACKING' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered, p1.tagCode  \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select x.* \
                        from td_logistic_box x \
                        inner join ( \
                            select palletId from td_logistic_box where boxId = '" + scanId + "' \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId ='" + scanId + "') \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                        ) y \
                        on y.palletId = x.palletId \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
            ) r1 \
            ,(SELECT @vPartition:='', @rownum:=0 FROM DUAL) r2 \
            ORDER BY r1.dtRegistered desc \
        ) tot "
        if lastYn == 'Y': 
            sql += " where rnum = 1"

        sql += " order by dtRegistered asc;"

    elif scanFlag in ('P'):
        sql =  " \
        select companyCode, retailerId, retailerName, lineCode, lineName, procType, scanId, qty, scanType, clientType, latitude, longitude, dtRegistered, tagCode, tagName \
        from ( \
            select r1.*, \
                (CASE @vPartition WHEN r1.retailerId THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) rnum, \
                (@vPartition:=r1.retailerId) vPartition \
            from ( \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, '' as lineCode, '' as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered \
                        , (select tagCode from td_logistic_box where palletId = '" + scanId + "' order by dtPalletScan limit 1) as tagCode \
                    from th_logistic_inout x1 \
                    where scanId = '" + scanId + "' \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                inner join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, a.lineCode, d." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'CREATE' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered , p2.tagCode \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select * from td_logistic_box where palletId = '" + scanId + "' \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                inner join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                left outer join td_line d \
                on a.lineCode = d.lineCode \
        ) r1 \
            ,(SELECT @vPartition:='', @rownum:=0 FROM DUAL) r2 \
            ORDER BY r1.dtRegistered desc \
        ) tot "
        if lastYn == 'Y': 
            sql += " where rnum = 1"

        sql += " order by dtRegistered asc;"

    else:
        scanFlag = 'T'
        scanId = scanId.replace(' ', '')
        scanId = scanId.replace('%2B', '+')
        scanId = scanId.replace('%2F', '/')
        scanId = scanId.replace('%25', '%')
        scanId = scanId.replace('%3D%3D', '==')

        sql =  " \
        select companyCode, retailerId, retailerName, lineCode, lineName, procType, scanId, qty, scanType, clientType, latitude, longitude, dtRegistered, tagCode, tagName \
        from ( \
            select r1.*, \
                (CASE @vPartition WHEN r1.retailerId THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) rnum, \
                (@vPartition:=r1.retailerId) vPartition \
            from ( \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as retailerName, '' as lineCode, '' as lineName, a.procType, a.scanId, concat(ioQty, ' EA') as qty, a.scanType, a.clientType, a.latitude, a.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, c." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode from th_logistic_inout where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, ioRtid as rtid, ioType as procType, ioQty, x.scanId, scanType, clientType, latitude, longitude, dtRegistered, tagCode \
                    from th_logistic_inout x \
                    inner join ( \
                        select boxId as scanId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                        union all \
                        select boxId as scanId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                        union all \
                        select palletId as scanId from td_logistic_pallet where palletId in ( \
                            select palletId from ( \
                                select * from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                                union all \
                                select * from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                            ) t \
                        ) \
                    ) y \
                    on y.scanId = x.scanId \
                    and dtRegistered < ifnull((select min(dtRegistered) from th_logistic_inout where scanId = '" + scanId + "'),  dtRegistered + INTERVAL 1 SECOND) \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_holotag c \
                on a.companyCode = c.companyCode \
                and a.tagCode = c.code \
                \
                union all \
                \
                select a.companyCode, a.rtid as retailerId, b." + sqlLangName + " as reteailerName, a.lineCode, c." + sqlLangName + " as lineName, a.procType, a.scanId, case when a.scanType in ('T', 'S') then concat(packQty, ' EA') else concat(packQty, ' BOX') end as qty, a.scanType, a.clientType, b.latitude, b.longitude \
                        , DATE_FORMAT(a.dtRegistered, '%Y-%m-%d %T') as dtRegistered, a.tagCode, d." + sqlLangName + " as tagName \
                from ( \
                    select companyCode, rtid, lineCode, 'CREATE' as procType, scanId, 'T' as scanType, tagQty as packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_tag where scanId = '" + scanId + "' \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                    union all \
                    select companyCode, rtid, lineCode, 'PACKING' as procType, boxId as scanId, boxType as scanType, packQty, 'L' as clientType, dtRegistered, tagCode from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                    union all \
                    select p1.companyCode, p1.rtid, p1.lineCode, 'PACKING' as procType, p1.palletId as scanId, 'P' as scanType, count(p2.packQty) as packQty, 'L' as clientType, p1.dtRegistered, p1.tagCode \
                    from td_logistic_pallet p1 \
                    inner join ( \
                        select x.* \
                        from td_logistic_box x \
                        inner join ( \
                            select palletId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                            union all \
                            select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                        ) y \
                        on y.palletId = x.palletId \
                    ) p2 \
                    on p1.companyCode = p2.companyCode \
                    and p1.palletId = p2.palletId \
                    group by p1.palletId \
                ) a \
                inner join td_retailer b \
                on a.rtid = b.rtid \
                left outer join td_line c \
                on a.lineCode = c.lineCode \
                left outer join td_holotag d \
                on a.companyCode = d.companyCode \
                and a.tagCode = d.code \
            ) r1 \
            ,(SELECT @vPartition:='', @rownum:=0 FROM DUAL) r2 \
            ORDER BY r1.dtRegistered desc \
        ) tot "
        if lastYn == 'Y': 
            sql += " where rnum = 1"

        sql += " order by dtRegistered asc;"

    curs.execute(sql)
    trackingList = list(curs.fetchall())
    conn.close()

    cipher = CipherAgent()

    for index, tr in enumerate(trackingList):
        tr_dict = dict()
        tr_dict['companyCode'] = tr[0]
        tr_dict['retailerId'] = tr[1]
        tr_dict['retailerName'] = tr[2]
        tr_dict['lineCode'] = tr[3]
        tr_dict['lineName'] = tr[4]
        tr_dict['procType'] = tr[5]
        tr_dict['scanId'] = tr[6]
        tr_dict['qty'] = tr[7]
        tr_dict['scanType'] = tr[8]
        tr_dict['clientType'] = tr[9]
        tr_dict['latitude'] = cipher.decodingBase64AndDecrypt(str(tr[10]))
        tr_dict['longitude'] = cipher.decodingBase64AndDecrypt(str(tr[11]))
        tr_dict['dtRegistered'] = tr[12]
        tr_dict['tagCode'] = tr[13]
        tr_dict['tagName'] = tr[14]

        trackingList[index] = tr_dict    

    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'trackingList': trackingList
    })


@main.route('/api/getLogisticLastPackingId', methods=['POST'])
def get_LogisticLastPackingId():
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    scanId = json_data.get('scanId')    
    scanFlag = scanId[:1]

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    if scanFlag in ('S', 'M', 'L'):
        sql =  "select a.scanId, dtRegistered \
                from ( \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId = '" + scanId + "' \
                    union all \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                    union all \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                    union all \
                    select x.palletId as scanId, dtRegistered \
                    from td_logistic_pallet x \
                    inner join ( \
                        select palletId from td_logistic_box where boxId = '" + scanId + "' \
                        union all \
                        select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "') \
                        union all \
                        select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId = '" + scanId + "')) \
                    ) y \
                    on y.palletId = x.palletId \
                ) a \
                order by dtRegistered desc limit 1;"

    elif scanFlag in ('P'):
        sql =  "select palletId as scanId, dtRegistered \
                from td_logistic_pallet \
                where palletId = '" + scanId + "';"

    else:
        scanFlag = 'T'
        scanId = scanId.replace(' ', '')
        scanId = scanId.replace('%2B', '+')
        scanId = scanId.replace('%2F', '/')
        scanId = scanId.replace('%25', '%')
        scanId = scanId.replace('%3D%3D', '==')        

        sql =  "select a.scanId \
                from ( \
                    select scanId, dtRegistered from td_logistic_tag where scanId = '" + scanId + "' \
                    union all \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                    union all \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                    union all \
                    select boxId as scanId, dtRegistered from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                    union all \
                    select x.palletId as scanId, dtRegistered \
                    from td_logistic_pallet x \
                    inner join (	\
                        select palletId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "') \
                        union all \
                        select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "')) \
                        union all \
                        select palletId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select parentBoxId from td_logistic_box where boxId in (select boxId from td_logistic_tag where scanId = '" + scanId + "'))) \
                    ) y \
                    on y.palletId = x.palletId \
                ) a \
                order by dtRegistered desc limit 1;"

    curs.execute(sql)
    packingTree = list(curs.fetchall())
    conn.close()
    
    lastPackingId = ''
    
    if len(packingTree) > 0:
        lastPackingId = packingTree[0][0]

    return jsonify({'LastPackingId': lastPackingId})


@main.route('/api/selLogisticPackingTree', methods=['POST'])
def select_LogisticPackingTree():
    lang = get_locale()
    json_data = json.loads(request.data, strict=False)  # 제어문자(\t \r \n) 파싱 가능...
    scanId = json_data.get('scanId')    
    scanFlag = scanId[:1]

    # if lang == 'ko':
    #     sqlLangName = 'name_kr'
    # elif lang == 'en':
    #     sqlLangName = 'name_en'
    # else:
    #     sqlLangName = 'name_zh'

    conn = pymysql.connect(host=db.engine.url.host,
                           user=db.engine.url.username,
                           password=db.engine.url.password,
                           db=db.engine.url.database,
                           charset=db.engine.url.query['charset'],
                           port=db.engine.url.port)

    curs = conn.cursor()

    # if scanFlag in ('S', 'M', 'L'):
    #     sql =  "select t.pid, t.cid, t.companyCode, t.boxType, t.tagCode, h." + sqlLangName + " as tagName, t.lastRtid as lastRetailerId, r." + sqlLangName + " as lastRetailerName \
    #             from ( \
    #                 select '' as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where boxId = '" + scanId + "' \
    #                 union all \
    #                 select parentBoxId as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where parentBoxId = '" + scanId + "' \
    #                 union all \
    #                 select parentBoxId as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where parentBoxId = '" + scanId + "') \
    #                 union all \
    #                 select x.boxId as pid, scanId as cid, companyCode, 'T' as boxType, tagCode, lastRtid \
    #                 from td_logistic_tag x \
    #                 inner join ( \
    #                     select boxId from td_logistic_box where boxId = '" + scanId + "' \
    #                     union all \
    #                     select boxId from td_logistic_box where parentBoxId = '" + scanId + "' \
    #                     union all \
    #                     select boxId from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where parentBoxId = '" + scanId + "') \
    #                 ) y \
    #                 on y.boxId = x.boxId \
    #             ) t \
    #             inner join td_holotag h \
    #             on t.companyCode = h.companyCode \
    #             and t.tagCode = h.code \
    #             left outer join td_retailer r \
    #             on t.lastRtid = r.rtid \
    #             order by case boxType when 'P' then 1 \
	# 			 			          when 'M' then 2 \
	# 			 			          when 'S' then 3 \
	# 			 			          when 'T' then 4 end, cid \
    #             ;"    

    # elif scanFlag in ('P'):
    #     sql =  "select t.pid, t.cid, t.companyCode, t.boxType, t.tagCode, h." + sqlLangName + " as tagName, t.lastRtid as lastRetailerId, r." + sqlLangName + " as lastRetailerName \
    #             from ( \
    #                 select '' as pid, palletId as cid, companyCode, 'P' as boxType, tagCode, lastRtid from td_logistic_pallet where palletId = '" + scanId + "' \
    #                 union all \
    #                 select palletId as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where palletId = '" + scanId + "' \
    #                 union all \
    #                 select parentBoxId as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where palletId = '" + scanId + "') \
    #                 union all \
    #                 select parentBoxId as pid, boxId as cid, companyCode, boxType, tagCode, lastRtid from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where palletId = '" + scanId + "')) \
    #                 union all \
    #                 select x.boxId as pid, scanId as cid, companyCode, 'T' as boxType, tagCode, lastRtid \
    #                 from td_logistic_tag x \
    #                 inner join ( \
    #                     select boxId from td_logistic_box where palletId = '" + scanId + "' \
    #                     union all \
    #                     select boxId from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where palletId = '" + scanId + "') \
    #                     union all \
    #                     select boxId from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where parentBoxId in (select boxId from td_logistic_box where palletId = '" + scanId + "')) \
    #                 ) y \
    #                 on y.boxId = x.boxId \
    #             ) t \
    #             inner join td_holotag h \
    #             on t.companyCode = h.companyCode \
    #             and t.tagCode = h.code \
    #             left outer join td_retailer r \
    #             on t.lastRtid = r.rtid \
    #             order by case boxType when 'P' then 1 \
	# 			 			          when 'M' then 2 \
	# 			 			          when 'S' then 3 \
	# 			 			          when 'T' then 4 end, cid \
    #             ;"

    # else:
    #     scanFlag = 'T'
    #     scanId = scanId.replace(' ', '')
    #     scanId = scanId.replace('%2B', '+')
    #     scanId = scanId.replace('%2F', '/')
    #     scanId = scanId.replace('%25', '%')
    #     scanId = scanId.replace('%3D%3D', '==')        

    #     sql =  "select t.pid, t.cid, t.companyCode, t.boxType, t.tagCode, h." + sqlLangName + " as tagName, t.lastRtid as lastRetailerId, r." + sqlLangName + " as lastRetailerName \
    #             from ( \
    #                 select '' as pid, scanId as cid, companyCode, 'T' as boxType, tagCode, lastRtid from td_logistic_tag where scanId = '" + scanId + "' \
    #             ) t \
    #             inner join td_holotag h \
    #             on t.companyCode = h.companyCode \
    #             and t.tagCode = h.code \
    #             left outer join td_retailer r \
    #             on t.lastRtid = r.rtid \
    #             order by case boxType when 'P' then 1 \
	# 			                      when 'M' then 2 \
	# 			                      when 'S' then 3 \
	# 			                      when 'T' then 4 end, cid \
    #             ;"
    
    if scanFlag not in ('P', 'L', 'M', 'S'):
        scanFlag = 'T'
    args = [scanFlag, scanId, lang]
    curs.callproc('proc_selLogisticPackingTree', args)
    # curs.execute(sql)
    packingTree = list(curs.fetchall())
    conn.close()

    for index, tr in enumerate(packingTree):
        tr_dict = dict()
        tr_dict['pid'] = tr[0]
        tr_dict['cid'] = tr[1]
        tr_dict['companyCode'] = tr[2]
        tr_dict['boxType'] = tr[3]
        tr_dict['tagCode'] = tr[4]
        tr_dict['tagName'] = tr[5]
        tr_dict['lastRetailerId'] = tr[6]
        tr_dict['lastRetailerName'] = tr[7]

        packingTree[index] = tr_dict

    return jsonify({'packingTree': packingTree})
    

@main.route('/api/insLogistictagMulti', methods=['POST'])
def insert_logistictagMulti():
    json_data = request.get_json()

    insCnt = json_data.get('insCnt') 

    holotag = TdHolotag.query.filter_by(companyCode = json_data.get('companyCode'), code = json_data.get('tagCode')).first()

    findKey = 'T' + json_data.get('lineCode')[-6:] + datetime.now().strftime('%y%m%d')
    seq = 0
    sel = TdLogisticTag.query.filter(TdLogisticTag.companyCode == json_data.get('companyCode'), TdLogisticTag.tagId.like(findKey + '%')).order_by(TdLogisticTag.tagId.desc()).first()
    if sel is not None:
        seq = int(sel.tagId[-6:])

    if (seq + insCnt) > 999999:
        return jsonify({
            'result': {
                'code': 8512,
                # 'msg' : 'It is already registered data.'
                'msg' : '금일 발권 수량을 초과 합니다. 발권가능 잔량(' +  str(999999 - seq) + ')'
            }            
        })

    loop = 1
    
    while loop <= insCnt:
        loop += 1
        seq += 1        

        tagId = findKey + (6 - len(str(seq))) * '0' + str(seq)

        tag = TdLogisticTag(companyCode=json_data.get('companyCode'),
                            rtid=json_data.get('rtid'),
                            lineCode=json_data.get('lineCode'),
                            tagId=tagId,
                            tagCode=json_data.get('tagCode'),
                            scanYn='N',
                            dtScan=None,
                            packYn='N',
                            scanId=tagId,
                            random=None,
                            boxId=None,
                            tagQty=holotag.tagStdQty,
                            lastLineCode=json_data.get('lineCode'),
                            lastRtid=json_data.get('rtid'),                        
                            registrant=json_data.get('registrant'),
                            dtRegistered=datetime.now(),
                            modifier=None,
                            dtModified=None)
        
        db.session.add(tag)

    db.session.commit()
    return jsonify({
        'result': {
            'code': 1000,
            'msg' : gettext('1000')
        },
        'logistictag': tag.to_json()
    })