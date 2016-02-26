# 短信发送微服务

## 配置说明

```
server_conf = {
    "port": 9000 #服务端口
}
sms_conf = {
    "VENDER": "sms_sender.sms.",
    'scrt_key': 'secret_key_plcloud', #服务密钥，与客户端配对一致
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
        "regist": "regist_template_id_in_open189" #open189平台自定义regist模板ID
    },
}

temp_conf = {
    "regist": u'您的注册验证码是：{{ code }}.请完成注册' #通用短信模板
}
```

## supervisor配置服务

```
[program:sms_sender]
command=/usr/bin/python /opt/sms_sender/sms_sender/notify.py
```

## 服务启动

```
[root@mongo1 sms_sender]# supervisorctl start sms_sender
sms_sender: started

```

## 测试

## references