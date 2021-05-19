import requests
import re
import os
import time
requests.packages.urllib3.disable_warnings()


def SendText(api, Error):
    print(Error)
    data = '{"msgtype":"markdown","markdown": {"title":"健康打卡通知","text": "健康打卡失败\n\n'+Error+'\n> [更新地址](https://github.com/yep96/ZJU_healthreport)"}}'
    requests.post(url=api, headers={'Content-Type': 'application/json'}, data=data.encode('utf-8'))
    exit()


class ZJUHealthReport():
    def __init__(self, user, passwd, ua, api, area):
        self.session = requests.session()
        self.ua = ua
        self.api = api
        self.area = area

        version = requests.get('https://pastebin.com/raw/6XCDvF71', verify=False).text
        if version != '2021/5/19':  # 检测一下有无更新，github国内访问不稳定
            SendText(self.api, '请更新版本')

        if os.path.exists('cookies'):
            with open('cookies', encoding='utf-8') as f:
                cookies = eval(f.read())
            self.session.cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
        else:
            if not self.login(user, passwd):
                SendText(self.api, '登陆失败')

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
        res = self.session.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index', headers={'User-Agent': self.ua, }, verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        print(str(requests.utils.dict_from_cookiejar(self.session.cookies)))
        if "hasFlag: '1'" in res.text:
            print('已打卡')
            exit()
        if '统一身份认证' in res.text:
            SendText(self.api, '登录失效，请更新cookies')

        if (len(re.findall('getdqtlqk', res.text)) != 15) or (len(re.findall('"', res.text)) != 1973) or (len(re.findall('<', res.text)) != 1230) or (len(re.findall('active', res.text)) != 69):
            SendText(self.api, '表单已更改，请等待更新或自行修改{} {} {} {}'.format(len(re.findall('getdqtlqk', res.text)), len(re.findall('"', res.text)), len(re.findall('<', res.text)), len(re.findall('active', res.text))))  # 简单判断表单是否改变

        self.data['area'] = self.area
        self.data['province'] = self.area.split()[0]
        self.data['city'] = self.area.split()[1]
        self.data['id'] = re.search(r'"id":"(\d*?)",', res.text).groups()[0]
        self.data['uid'] = re.search(r'"uid":"(\d*?)"', res.text).groups()[0]
        self.data['date'] = re.search(r'"date":"(\d*?)"', res.text).groups()[0]
        self.data['created'] = re.search(r'"created":"(\d*?)",', res.text).groups()[0]

        data2 = {'error': r'{"type":"error","message":"Get geolocation time out.Get ipLocation failed.","info":"FAILED","status":0}'}
        time.sleep(3)
        self.session.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save-geo-error', data=data2, headers={'User-Agent': self.ua, }, verify=False)
        time.sleep(3)  # 延迟假装在填写，应该没用
        res = self.session.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save', data=self.data, headers={'User-Agent': self.ua, }, verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        if (re.search('"e":0', res.text) is None):  # 检查返回值，是否成功打卡
            SendText(self.api, '打卡失败')
        print('打卡成功')


def handler(event, context):
    usr = r'XXX'
    pwd = r'XXX'  # 统一认证账号密码
    # 自己的钉钉ua，如在钉钉中打开http://www.all-tool.cn/Tools/ua/
    ua = r'XXX'
    # 钉钉推送api，用于打卡失败提醒，很重要务必设置
    api = r'https://oapi.dingtalk.com/robot/send?access_token=XXX'
    area = r'浙江省 杭州市 西湖区'  # 如浙江省 温州市 鹿城区 或 北京市 北京市 东城区。这里把手机关闭定位或不授予应用定位权限手动选择
    try:
        DK = ZJUHealthReport(usr, pwd, ua, api, area)
        DK.DK()
    except Exception as e:
        SendText(api, str(e))
