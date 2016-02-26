#coding:utf-8
'''send sms config file'''
server_conf = {
    "port": 9000
}
sms_conf = {
    "VENDER": "sms_sender.sms.",
    'scrt_key': 'secret_key_plcloud',
    'CLan': {
        'gateway': 'http://222.73.117.158/msg/HttpBatchSendSM',
        'account': 'xxx',
        'pswd': 'xxx',
        'needstatus': 'false'
    },
    'OPEN189': {
        "gateway": "http://api.189.cn/v2/emp/templateSms/sendSms",
        "AT_gateway": "https://oauth.api.189.cn/emp/oauth2/v3/access_token",
        "app_id": "xxx",
        "app_secret": "xxx",
        "regist": "regist_template_id_in_open189"
    },
}

temp_conf = {
    "regist": u'您的注册验证码是：{{ code }}.请完成注册'
}
