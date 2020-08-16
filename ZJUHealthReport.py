import requests
import re
import os
import time
requests.packages.urllib3.disable_warnings()


def login(s,usr,pwd):
    login_url='https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex'
    res = s.get(url=login_url,verify=False)
    execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
    res = s.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey',verify=False).json()
    M_str, e_str = res['modulus'], res['exponent']
    password_bytes = bytes(pwd, 'ascii')
    password_int = int.from_bytes(password_bytes, 'big')
    e_int = int(e_str, 16)
    M_int = int(M_str, 16)
    result_int = pow(password_int, e_int, M_int)
    encrypt_password = hex(result_int)[2:].rjust(128, '0')
    data = {
        'username': usr,
        'password': encrypt_password,
        'execution': execution,
        '_eventId': 'submit'
    }
    res = s.post(url=login_url, data=data,verify=False)
    if '统一身份认证' in res.content.decode():
        return False
    return True

def SendText(api,Error):
    requests.post(url=api, data={'text': '浙大健康打卡失败','desp':Error,})
    exit()


try:
    usr = r''
    pwd = r''  # 统一认证账号密码
    ua = r''  # 自己的钉钉ua，如在钉钉中打开http://www.all-tool.cn/Tools/ua/
    api = r'https://sc.ftqq.com/XXX.send'  # server酱的微信推送api，用于打卡失败提醒
    area = r'xx省 xx市 xx区'  # 如浙江省 温州市 鹿城区 或 北京市 北京市 东城区。这里把手机关闭定位或不授予应用定位权限手动选择
    cwd = r''  # 脚本所在路径 如/etc/Tasks/ 或 D:/Tasks/ ,crontab执行时需要
    exit()  # 修改完上面的删掉这句
    s = requests.Session()
    if os.path.exists(cwd+'cookies'):
        with open(cwd+'cookies') as f:
            dict = eval(f.read())
        s.cookies = requests.utils.cookiejar_from_dict(dict, cookiejar=None, overwrite=True)
        os.remove(cwd+'cookies')
    else:
        while not login(s,usr,pwd):
            with open(cwd+'login','a',encoding='utf-8') as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'登录ZJU\n')  # 记录登录次数及时间
            time.sleep(30)
    res = s.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index',headers={'User-Agent':ua,},verify=False)
    res.raise_for_status()
    res.encoding = "utf-8"  # 8/8表单更改后不需要从该网页提取信息
    if (len(re.findall('getdqtlqk',res.text)) != 14) or (len(re.findall('武汉',res.text)) != 2) or (len(re.findall('北京市',res.text)) != 1):
        SendText(api, '表单已更改，请等待更新或自行修改')  # 从“以下地区返回浙江”地区数量是否改变简单判断表单是否改变
    with open(cwd+'data', encoding='utf-8') as f:
        data = eval(f.read())
    data['area'] = area
    data['province'] = area.split()[0]
    data['city'] = area.split()[1]
    time.sleep(10)  # 延迟10s假装在填写，应该没用
    res = s.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save',data=data,headers={'User-Agent':ua,},verify=False)
    res.raise_for_status()
    res.encoding = "utf-8"
    if (re.search('"e":0',res.text) is None):  # 检查返回值，是否成功打卡
        SendText(api, '打卡失败')
    print('打卡成功')
    with open(cwd+'cookies', 'w', encoding='utf-8') as f:
        f.write(str(requests.utils.dict_from_cookiejar(s.cookies)))  # 此时的cookies是有效的更新，否则不保存下次登录
except Exception as e:
    SendText(api,str(e))
