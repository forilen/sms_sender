#coding:utf-8
"""
SMS Module , send sms to user
"""
import abc
import json
import logging
import datetime
import re
import requests

from sms_sender import utils as importutils
from sms_sender import conf as CONF
from sms_sender.log import Log as LOG


class SMSMeta(object):
    """因为各个短信平台接口不一致，需要短信接口基类"""
    __metaclass__ = abc.ABCMeta
    CONFIG = getattr(CONF, 'sms_conf', {})

    @abc.abstractmethod
    def send_sms(self, message, mobiles):
        '''发送短信,
        param message：发送的短信信息
        param mobiles: 发送的手机号，需要为list类型'''

    @abc.abstractmethod
    def tpl_send_sms(self, meta_data, mobiles):
        '''发送模板短信,
        param message：发送的短信信息
        param mobiles: 发送的手机号，需要为list类型'''


class SMS(SMSMeta):
    def __init__(self, *args, **kwargs):
        VENDER = self.CONFIG.get('VENDER')
        if not VENDER:
            raise RuntimeError("SMS VENDER NOT FOUND")
        VENDER += kwargs['channel']
        self.vender = importutils.import_class(VENDER)(*args, **kwargs)

    def send_sms(self, message, mobiles):
        self.vender.send_sms(message, mobiles)

    def tpl_send_sms(self, meta_data, mobiles):
        self.vender.tpl_send_sms(mobiles, meta_data)


class Montnets(SMSMeta):
    '''梦网短信网关接口实现，使用soap协议'''
    def __init__(self, gateway=None, userId=None, password=None, channel=None):
        self.CONFIG = self.CONFIG['Montnets']

        from suds.client import Client
        if gateway:
            self.gateway = gateway
        else:
            self.gateway = self.CONFIG['gateway']
        if userId:
            self.userId = userId
        else:
            self.userId = self.CONFIG['userId']
        if password:
            self.password = password
        else:
            self.password = self.CONFIG['password']
        self.client = Client(self.gateway)

    def send_sms(self, mobiles, Msg, SubPort='*'):
        '''
        param message:短信内容， 内容长度不大于350个汉字
        param mobiles:目标号码，用英文逗号(,)分隔，最大100个号码。一次提交的号码类型不受限制，
        但手机号会做验证，若有不合法的手机号将会被退回。 号码段类型分为：移动、联通、电信手机。 注意：请不要使用中文的逗号

        param SubPort:子端口号码，不带请填星号{*} 长度由账号类型定4-6位，
        通道号总长度不能超过20位。如：10657****主通道号，3321绑定的扩展端口，主+扩展+子端口总长度不能超过20位。'''
        pszMobis = ','.join(mobiles)
        iMobiCount = len(mobiles)
        result = self.client.service.MongateCsSpSendSmsNew(
            self.userId,
            self.password,
            pszMobis,
            Msg,
            iMobiCount,
            SubPort
        )
        return result

    def tpl_send_sms(self, meta_data, mobiles):
        pass


class CLan(SMSMeta):
    """上海创蓝文化传播短信网接口实现"""
    def __init__(self, gateway=None, account=None, pswd=None, needstatus=None,
                 channel=None):
        self.CONFIG = self.CONFIG['CLan']
        self.gateway = self.CONFIG['gateway']
        if account:
            self.account = account
        else:
            self.account = self.CONFIG['account']
        if pswd:
            self.pswd = pswd
        else:
            self.pswd = self.CONFIG['pswd']
        if needstatus:
            self.needstatus = needstatus
        else:
            self.needstatus = self.CONFIG['needstatus']

    def send_sms(self, mobiles, msg):
        """
        """

        mobiles = ','.join(mobiles)
        data = {'account': self.account,
                'pswd': self.pswd,
                'needstatus': self.needstatus,
                'mobile': mobiles,
                'msg': msg}
        r = requests.post(self.gateway, data)
        return r

    def tpl_send_sms(self, meta_data, mobiles):
        pass


class B2Tong(SMSMeta):
    """亿美网通短信网关接口实现"""
    def __init__(self, gateway=None, cdkey=None, password=None, signature=None,
                 channel=None):
        self.CONFIG = self.CONFIG['B2Tong']
        if gateway:
            self.gateway = gateway
        else:
            self.gateway = self.CONFIG['gateway']
        if cdkey:
            self.cdkey = cdkey
        else:
            self.cdkey = self.CONFIG['cdkey']
        if password:
            self.password = password
        else:
            self.password = self.CONFIG['password']
        if signature:
            self.signature = '【' + signature + '】 '
        else:
            self.signature = '【' + self.CONFIG['signature'] + '】 '

    def _request(self, method, url, data):
        if method == 'POST':
            return requests.post(url, data)
        if method == 'GET':
            return requests.get(url, data)

    def request(self, method=None, url=None, data=None):
        resp = self._request(method, url, data)
        return resp

    def regist(self):
        url = self.gateway + '/regist.action'
        data = {'cdkey': self.cdkey,
                'password': self.password}
        method = 'POST'
        r = self.request(method, url, data=json.dumps(data))
        return r.text

    def logout(self):
        url = self.gateway + '/logout.action'
        data = {'cdkey': self.cdkey,
                'password': self.password}
        method = 'POST'
        r = self.request(method, url, data)
        return r

    def querybalance(self):
        url = self.gateway + '/querybalance.action'
        data = {'cdkey': self.cdkey,
                'password': self.password}
        method = 'POST'
        r = self.request(method, url, data)
        return r

    def send_sms(self, mobiles, Msg):
        """
        param mobiles: the list of phone number, less than 200
        param MSG: SMS content, less then 500 Chinese characters or 1000 english words
        """

        url = self.gateway + '/sendsms.action'
        mobiles = ','.join(mobiles)
        data = {'cdkey': self.cdkey,
                'password': self.password,
                'phone': mobiles,
                'message': self.signature + Msg}
        method = 'POST'
        r = self.request(method, url, data)
        return r

    def tpl_send_sms(self, meta_data, mobiles):
        pass


class QF106(SMSMeta):
    def __init__(self, gateway=None, userid=None, account=None, password=None,
                 channel=None):
        self.CONFIG = self.CONFIG['QF106']
        self.gateway = gateway or self.CONFIG['gateway']
        self.userid = userid or self.CONFIG['userid']
        self.account = account or self.CONFIG['account']
        self.password = password or self.CONFIG['password']

    def send_sms(self, message, mobiles):
        data = {'action': 'send',
                'userid': self.userid,
                'account': self.account,
                'password': self.password,
                'mobile': ','.join(mobiles),
                'content': message,
                'countnumber': len(mobiles),
                'mobilenumber': len(mobiles),
                'telephonenumber': 0}
        resp = requests.post(self.gateway, data)
        LOG.debug(resp.text)
        return resp

    @property
    def balance(self):
        data = {'action': 'overage',
                'userid': self.userid,
                'account': self.account,
                'password': self.password}
        resp = requests.post(self.gateway, data)
        LOG.debug(resp.text)
        return resp

    def tpl_send_sms(self, meta_data, mobiles):
        pass


class OPEN189(SMSMeta):
    def __init__(self, gateway=None, app_id=None, template_id=None,
                 channel=None):
        '''
        发送模板短信: http://open.189.cn/index.php?m=api&c=index&a=show&id=858
        '''
        self.CONFIG = self.CONFIG['OPEN189']
        self.gateway = gateway or self.CONFIG['gateway']
        self.app_id = app_id or self.CONFIG['app_id']

        self.AT_gateway = self.CONFIG.get('AT_gateway')
        self.app_secret = self.CONFIG.get('app_secret')

    def _getUIAT(self):
        '''
        令牌接口: http://open.189.cn/index.php?m=content&c=index&a=lists&catid=62
        发送模板短信无须“授权”，采用“令牌接口”的“应用场合二”
        '''
        data = {'grant_type': "client_credentials",
                'app_id': self.app_id,
                'app_secret': self.app_secret}
        try:
            resp = requests.post(self.AT_gateway, data, verify=False)
            resp = json.loads(resp.text)
            if resp.get("res_code") == "0":
                return resp.get("access_token")
            else:
                LOG.error("get token error: %s" % resp.get('res_message'))
                return None
        except Exception as err:
            LOG.error("get token error")
            return None

    def tpl_send_sms(self, meta_data, mobiles):
        access_token = self._getUIAT()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if all((access_token, meta_data)):
            data = {'app_id': self.app_id,
                    'access_token': self._getUIAT(),
                    'acceptor_tel': mobiles[0],
                    'template_id': meta_data.pop('temp_id'),
                    'template_param': meta_data,
                    'timestamp': now}
            LOG.debug(json.dumps(data))
            resp = requests.post(self.gateway, data)
            LOG.debug("[%s]%s" % (mobiles[0], resp.text))
            resp = json.loads(resp.text)
            if resp.get("res_code") == 0:
                return resp.get("identifier")
            else:
                LOG.error("send sms failed: %s" % resp.get('res_message'))
                return None
        else:
            LOG.error("Could not send sms")
            return None


class Yunpian(SMSMeta):

    def __init__(self):
        '''https://github.com/yunpian/sms/blob/master/yunpian/python/yunpianSmsClient.py'''
        pass

    def send_sms(self, message, mobiles):
        pass

    def tpl_send_sms(self, meta_data, mobiles):
        pass


if __name__ == '__main__':
    pass
