#coding:utf-8
import hashlib
import json
import requests
import threading
from time import ctime, sleep


CONF = {'app_id': 'openstack_dashboard',
        'scrt_key': 'secret_key_plcloud',
        'gate_way': 'http://192.168.212.241:9000/send_sms/',
        'channel': 'CLan',
        'sms_type': 'send_sms',
        'temp_id': 'regist'}

def _chain(cleaned_data):
    '''原始字符串'''
    # Charset Encode
    ce = lambda x: (x[0], smart_str(x[1], 'utf-8'))

    chain = sorted(map(ce, cleaned_data.items()))
    return chain

def _sign(chain):
    '''签名方法'''
    encoded = '&'.join('%s=%s' % x for x in chain)
    return hashlib.md5('%s%s' % (encoded, CONF['scrt_key'])).hexdigest()

def _post_data(cleaned_data):
    chain = _chain(cleaned_data)
    cleaned_data.update({'sign': _sign(chain)})
    return cleaned_data

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    if isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def check_sgin(s, pri_key):
    cleaned_data = json.loads(s)
    _sgin_code = cleaned_data.pop('sign')
    if _sgin_code:
        sign = _sign(_chain(cleaned_data))
        if _sgin_code == sign:
            return True
    return False


def main():
    data = {'app_id': CONF['app_id'],
            'channel': CONF['channel'],
            'phone_number': json.dumps(['13088873954']),
            'meta_data': json.dumps({'code': '123123'}),
            'temp_id': CONF['temp_id'],
            'sms_type': CONF['sms_type']}
    post_data = _post_data(data)
    try:
        r = requests.post(CONF['gate_way'], post_data)
        print r.text
    except Exception, e:
        raise e

if __name__ == '__main__':
    main()
