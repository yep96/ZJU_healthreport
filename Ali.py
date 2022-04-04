import os
import time
import re
import requests
from random import random as rand
requests.packages.urllib3.disable_warnings()


def SendText(api, Error):
    print(Error)
    data = '{"msgtype":"markdown","markdown": {"title":"健康打卡通知","text": "健康打卡失败\n\n'+Error+'\n> [更新地址](https://github.com/yep96/ZJU_healthreport)"}}'
    requests.post(url='https://oapi.dingtalk.com/robot/send?access_token='+api, headers={'Content-Type': 'application/json'}, data=data.encode('utf-8'))


class ZJUHealthReport():
    def __init__(self, user, passwd, ua, api, area, cookiesName = 'cookies'):
        self.session = requests.session()
        self.ua = {'User-Agent': ua}
        self.api = api
        self.area = area
        self.user = user

        with open(cookiesName) as f:
            cookies = eval(f.read())

        self.session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
        if '日常健康报备' not in self.session.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index', headers=self.ua).text:
            if not self.login(user, passwd):
                SendText(self.api, '登陆失败')
                self.session = None

        with open('data', encoding='utf-8') as f:
            self.data = eval(f.read())

    def login(self, user, passwd):
        login_url = 'https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex'
        res = self.session.get(url=login_url, verify=False)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.session.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', verify=False).json()
        M_str, e_str = res['modulus'], res['exponent']
        password_bytes = bytes(passwd, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        encrypt_password = hex(result_int)[2:].rjust(128, '0')
        data = {
            'username': user,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.session.post(url=login_url, data=data, verify=False)
        res.encoding = "utf-8"
        if '统一身份认证' in res.text:
            return False
        return True

    def DK(self):
        if self.session == None:
            return False
        res = self.session.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index', headers=self.ua, verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        # print(str(requests.utils.dict_from_cookiejar(self.session.cookies)))
        if "hasFlag: '1'" in res.text:
            print('已打卡')
            return True

        if (len(re.findall('getdqtlqk', res.text)) != 15) or (len(re.findall('<', res.text)) != 1251) or (len(re.findall('active', res.text)) != 72):
            SendText(self.api, '表单已更改，请等待更新或自行修改 {} {} {}'.format(len(re.findall('getdqtlqk', res.text)), len(re.findall('<', res.text)), len(re.findall('active', res.text))))  # 简单判断表单是否改变

        self.data['area'] = self.area
        self.data['province'] = self.area.split()[0]
        self.data['city'] = self.area.split()[1]
        self.data['id'] = re.search(r'"id":"?(\d*)"?,', res.text).groups()[0]
        self.data['uid'] = re.search(r'"uid":"?(\d*)"?,', res.text).groups()[0]
        self.data['date'] = re.search(r'"date":"?(\d*)"?,', res.text).groups()[0]
        self.data['created'] = re.search(r'"created":"?(\d*)"?,', res.text).groups()[0]
        csrf = re.search(r'"(\w{32})": ?"(\w{10})", ?"(\w{32})": ?"(\w{32})"[\s\S]{1,50}oldInfo', res.text).groups()
        self.data[csrf[0]] = csrf[1]
        self.data[csrf[2]] = csrf[3]

        data2 = {'error': r'{"type":"error","message":"Get geolocation time out.Get ipLocation failed.","info":"FAILED","status":0}'}
        time.sleep(rand()*3+3)
        self.session.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save-geo-error', data=data2, headers=self.ua, verify=False)
        time.sleep(rand()*3+2)  # 延迟假装在填写，应该没用
        res = self.session.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save', data=self.data, headers=self.ua, verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        if '"e":0' not in res.text:  # 检查返回值，是否成功打卡
            SendText(self.api, '打卡失败')
            return False
        print('打卡成功')


if __name__ == '__main__':
    usr = '学号'
    passwd = r'密码' # 登录好像有问题，随便填个占位置
    # 自己的钉钉ua，如在钉钉中打开http://www.all-tool.cn/Tools/ua/，也可只设置一个UA，修改ZJUHealthReport传入参数为ua[0]
    ua = r'UA'
    # 钉钉推送api，用于打卡失败提醒，很重要务必设置。填写https://oapi.dingtalk.com/robot/send?access_token=之后的即可
    api = r'API'
    area = r'浙江省 杭州市 西湖区' # 填入健康打卡“所在地点”地址
    cookiesName = 'DK' # cookies的文件名
    time.sleep(rand()*5+2)
    try:
        DK = ZJUHealthReport(usr, passwd, ua, api, area, cookiesName=cookiesName)
        DK.DK()
    except Exception as e:
        SendText(api, str(e))
