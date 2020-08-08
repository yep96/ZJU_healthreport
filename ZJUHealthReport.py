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


try:
    usr = r''
    pwd = r''  # 统一认证账号密码
    UA = r''  # 自己的钉钉ua，如在钉钉中打开http://www.all-tool.cn/Tools/ua/
    api = "https://sc.ftqq.com/XXX.send"  # server酱的微信推送api，用于打卡失败提醒，可不用
    area = r'xx省 xx市 xx市'
    province = r'xx省'
    city = r'xx市'  # area中第一个市
    cwd = r''  # 脚本所在路径 crontab执行时需要
    exit()  # 修改完上面的删掉这句
    s = requests.Session()
    if os.path.exists(cwd+'cookies'):
        with open(cwd+'cookies') as f:
            dict = eval(f.read())
        s.cookies = requests.utils.cookiejar_from_dict(dict, cookiejar=None, overwrite=True)
        os.remove(cwd+'cookies')
    else:
        while not login(s,usr,pwd):
            time.sleep(30)
    header = {'User-Agent': UA,}
    res = s.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index',headers={'User-Agent':UA,},verify=False)
    res.raise_for_status()
    res.encoding = "utf-8"  # 8/8表单更改后不需要从该网页提取信息
    with open(cwd+'data', encoding='utf-8') as f:
        data = eval(f.read())
    data['area'] = area
    data['province'] = province
    data['city'] = city
    time.sleep(10)  # 延迟10s假装在填写，应该没用
    res = s.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save',data=data,headers={'User-Agent':UA,},verify=False)
    res.raise_for_status()
    res.encoding = "utf-8"
    assert(re.search('"e":0',res.text) is not None)  # 检查返回值，是否成功打卡
    print('打卡成功')
    with open(cwd+'cookies', 'w', encoding='utf-8') as f:
        f.write(str(requests.utils.dict_from_cookiejar(s.cookies)))  # 此时的cookies是有效的更新，否则不保存下次登录
except Exception as e:
    requests.post(url=api, data={'text': '浙大健康打卡失败','data':str(e),})
