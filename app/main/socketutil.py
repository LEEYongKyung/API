from flask import Flask, jsonify, render_template, json, request
from subprocess import call
from flask_socketio import SocketIO, send, emit
from app import socket_io
from app import db, get_locale
from app.models_bswms import SysTranMsg
from datetime import datetime
import simplejson

from . import main

@main.route('/chat')
def chatting():
    return render_template('chat.html')

@socket_io.on("message")
def chat_request(message):
    print("message : " + message)
    to_client = dict()
    if message == 'new_connect':    
        to_client['message'] = "접속 되었습니다 !"
        to_client['type'] = 'connect'
        # to_client['sid'] = request.sid
        # reg_tran_msg_log_2('client_to_server_chat_new_connect', to_client)
        
        send(to_client, broadcast = False)
    else:
        to_client['message'] = message
        to_client['type'] = 'normal'
        # reg_tran_msg_log_2('client_to_server_chat_send_message', to_client)
        # to_client['sid'] = request.sid
        send(to_client, broadcast = True)

@socket_io.on("socket_message")
def socket_message(data):
    print("* socket_message : " + data)

    json_data = json.loads(data)    
    message = json_data.get('message')    
    userCd = json_data.get('userCd')

    to_client = dict()
    to_client['message'] = message    
    to_client['userCd'] = userCd    
    # send(to_client, broadcast = True)
    emit("socket_message", to_client, broadcast = True)

@socket_io.on("client_to_server_pre_connect_closed_request")
def client_to_server_pre_connect_closed_request(data):
    print("* client_to_server_pre_connect_closed_request : " + data)
    reg_tran_msg_log('client_to_server_pre_connect_closed_request', data)
    emit("server_to_client_pre_connect_closed_request", data, broadcast = True)
    
@socket_io.on("client_to_server_manual_connect_closed_request")
def client_to_server_manual_connect_closed_request(data):
    print("* client_to_server_manual_connect_closed_request : " + data)
    reg_tran_msg_log('client_to_server_manual_connect_closed_request', data)
    emit("server_to_client_manual_connect_closed_request", data, broadcast = True)

def reg_tran_msg_log(protocol, data):

    json_data = json.loads(data)
    msgDate = datetime.now().strftime('%y%m%d')
    msgSeq = 1    
    chk = SysTranMsg.query.filter(SysTranMsg.siteCd == json_data.get('siteCd'), SysTranMsg.msgDate == msgDate).order_by(SysTranMsg.msgSeq.desc()).first()
    if chk is not None:
        msgSeq = chk.msgSeq + 1
    
    log = SysTranMsg(
            siteCd=json_data.get('siteCd'),
            msgDate=msgDate,
            msgSeq=msgSeq,
            fConnCd=json_data.get('fConnCd'),
            tConnCd=json_data.get('tConnCd'),
            protocol=protocol,
            message=data,
            state='R',
            regUser=json_data.get('userCd'),
            regDate=datetime.now(),
            modUser=None,
            modDate=None)

    db.session.add(log)
    db.session.commit()

def reg_tran_msg_log_2(protocol, data):
    
    msgDate = datetime.now().strftime('%y%m%d')
    msgSeq = 1    
    chk = SysTranMsg.query.filter(SysTranMsg.siteCd == 'test1', SysTranMsg.msgDate == msgDate).order_by(SysTranMsg.msgSeq.desc()).first()
    if chk is not None:
        msgSeq = chk.msgSeq + 1
    
    log = SysTranMsg(
            siteCd='test1',
            msgDate=msgDate,
            msgSeq=msgSeq,
            fConnCd='',
            tConnCd='',
            protocol=protocol,
            message=str(data),
            state='R',
            regUser='',
            regDate=datetime.now(),
            modUser=None,
            modDate=None)

    db.session.add(log)
    db.session.commit()