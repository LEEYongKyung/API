from flask import Blueprint

main = Blueprint('main', __name__)

#from . import views, errors, views_bstnt, cipherutil #lkh (, views_mysql, cipherutil)
from . import errors, views_bswms_sys, views_bswms_mst, cipherutil, views_bswms_sal, views_bswms_pur, views_bswms_stk, views_bswms_pos, views_bswms_anl, socketutil, handlerutil