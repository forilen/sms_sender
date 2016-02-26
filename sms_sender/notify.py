#coding:utf-8
import os
import sys
import eventlet
import random
import json
import hashlib
from urlparse import parse_qsl

from jinja2 import Template


# If ../sms_sender/__init__.py exists, add . to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir,
                               'sms_sender',
                               '__init__.py')):
    sys.path.insert(0, possible_topdir)


from sms_sender import utils
from sms_sender.conf import sms_conf as CONF
from sms_sender.conf import temp_conf as TEMPLATE
from sms_sender.conf import server_conf
from sms_sender import sms
from sms_sender.log import Log as LOG


def _chain(cleaned_data):
    '''原始字符串'''
    # Charset Encode
    ce = lambda x: (x[0], utils.smart_str(x[1], 'utf-8'))

    chain = sorted(map(ce, cleaned_data.items()))
    return chain

def _sign(chain):
    '''签名方法'''
    encoded = '&'.join('%s=%s' % x for x in chain)
    return hashlib.md5('%s%s' % (encoded, CONF['scrt_key'])).hexdigest()

def check_sign(cleaned_data):
    _sgin_code = cleaned_data.pop('sign')
    if _sgin_code:
        sign = _sign(_chain(cleaned_data))
        if _sgin_code == sign:
            return True
        else:
            LOG.warning("sign error")
    return False

def sendsms(cleaned_data):
    if check_sign(cleaned_data):
        channel = cleaned_data.pop('channel')
        sms_type = cleaned_data.pop('sms_type')
        phonenum_list = json.loads(cleaned_data.pop('phone_number'))
        if sms_type == "send_sms":
            # 发送短信
            template = Template(TEMPLATE.get(cleaned_data.get('temp_id')))
            msg = template.render(json.loads(cleaned_data.get('meta_data')))
            LOG.info(msg)
            LOG.info(phonenum_list)
            return sms.SMS(channel=channel).send_sms(msg, phonenum_list)
        elif sms_type == "tpl_send_sms":
            # 发送模板短信
            temp_id = CONF[channel].get(cleaned_data.get('temp_id'))
            cleaned_data['temp_id'] = temp_id
            meta_data = json.loads(cleaned_data['meta_data'])
            return sms.SMS(channel=channel).tpl_send_sms(phonenum_list, meta_data)
        else:
            raise

def application(environ, start_response):
    if environ['PATH_INFO'] == '/send_sms/':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        start_response('200 OK', [('Content-Type', 'text/plain')])
        # request_body is string
        request_body = environ['wsgi.input'].read(request_body_size)
        request_body = dict(parse_qsl(request_body))
        # check sign and send sms
        eventlet.spawn_n(sendsms, request_body)
        return json.dumps({'code': 0, 'message': 'success'})
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return json.dumps({'code': 1, 'message': 'error'})


if __name__ == '__main__':
    from eventlet import wsgi
    port = getattr(server_conf, 'port', 9000)
    wsgi.server(eventlet.listen(('', port)), application)
