import requests
import re
import os
import time
requests.packages.urllib3.disable_warnings()


def SendText(api,Error):
    print(Error)
    requests.post(url=api, data={'text': '浙大健康打卡失败','desp':Error,})
    exit()


def handler(event, context):
    try:
        ua = r''  # 自己的钉钉ua，如在钉钉中打开http://www.all-tool.cn/Tools/ua/
        api = r'https://sc.ftqq.com/XXX.send'  # server酱的微信推送api，用于打卡失败提醒，很重要务必设置
        area = r'xx省 xx市 xx区'  # 如浙江省 温州市 鹿城区 或 北京市 北京市 东城区。这里把手机关闭定位或不授予应用定位权限手动选择
        exit()  # 修改完上面的删掉这句
        version=requests.get('https://pastebin.com/raw/6XCDvF71',verify=False).text
        if version != '2020/8/30':  # 检测一下有无更新，github国内访问不稳定
            SendText(api, '请更新版本\nhttps://github.com/yep96/ZJU_healthreport')
        s = requests.Session()
        if os.path.exists('cookies'):
            with open('cookies') as f:
                dict = eval(f.read())
            s.cookies = requests.utils.cookiejar_from_dict(dict, cookiejar=None, overwrite=True)
        else:
            SendText(api, '云函数无法修改文件，请在本地运行一次后获取cookies文件，上传至代码目录')
        res = s.get(url='https://healthreport.zju.edu.cn/ncov/wap/default/index',headers={'User-Agent':ua,},verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        if (len(re.findall('getdqtlqk',res.text)) != 15) or (len(re.findall('武汉',res.text)) != 2) or (len(re.findall('大连',res.text)) != 1) or (len(re.findall('active',res.text)) != 75):
            SendText(api, '表单已更改，请等待更新或自行修改')  # 从“以下地区返回浙江”地区数量是否改变简单判断表单是否改变
        with open('data', encoding='utf-8') as f:
            data = eval(f.read())
        data['area'] = area
        data['province'] = area.split()[0]
        data['city'] = area.split()[1]
        data['id'] = re.search(r'id":"(\d*?)"', res.text).groups()[0]
        data['uid'] = re.search(r'uid":"(\d*?)"', res.text).groups()[0]
        data['date'] = re.search(r'date":"(\d*?)"', res.text).groups()[0]
        data['created'] = re.search(r'created":"(\d*?)"', res.text).groups()[0]
        data2 = {'error': r'{"type":"error","message":"Get geolocation time out.Get ipLocation failed.","info":"FAILED","status":0}'}
        time.sleep(5)
        s.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save-geo-error',data=data2,headers={'User-Agent':ua,},verify=False)
        time.sleep(5)  # 延迟假装在填写，应该没用
        res = s.post(url='https://healthreport.zju.edu.cn/ncov/wap/default/save',data=data,headers={'User-Agent':ua,},verify=False)
        res.raise_for_status()
        res.encoding = "utf-8"
        if (re.search('"e":0',res.text) is None):  # 检查返回值，是否成功打卡
            SendText(api, '打卡失败')
        print('打卡成功')
    except Exception as e:
        SendText(api,str(e))
