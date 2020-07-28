# ZJU_healthreport
浙大健康打卡自动化脚本

尝试着练练手，看着应该是问题不大，风险自负<del>我已经在用了</del>

不会markdown，语文水平也不好，描述颠三倒四只能凑合着看

下载项目后需要修改data文件中的地址及ZJUHealthReport脚本中33行起的用户名密码和脚本位置等信息

脚本需安装requests模块
   ```bash
   $ python3 -m pip install requests
   ```

运行
   ```bash
   $ python3 ZJUHealthReport.py
   ```

crontab定时任务，如在8点30打卡
   ```bash
   $ crontab -e
   $ 0 30 8 * * * python3 /YOUR_PATH/ZJUHealthReport.py
   ```

data中的数据根据自己情况改，提交效果如图<a href="https://github.com/yep96/ZJU_healthreport/raw/master/健康打卡.jpg">健康打卡.jpg</a>

其中定位我是直接返回定位失败后手动选择地址<del>不过我真的也没有定位成功过</del>

地址为显示“点击获取地理位置”没有问题，我试过手动提交，重新打卡查看也是这样

不放心可以先关闭钉钉定位权限并手选地址，再用Fiddle4抓个包看看post了什么数据，再url解码后修改，其中地址中的+换成空格，否则前后抓包不一致

这个脚本不需要一直运行，通过读取上一次运行时保存的cookies保持会话。也许不用每次都删除后更新cookies，猜测是可用的，没有测试过

如果去掉更新cookies，则可以部署到云函数上自动打卡。需要将ZJUHealthReport.py、cookies和data一起上传，不知道ip和定位不匹配会不会有问题。阿里云服务的crontab最前面多了一个秒，0时区，可用 0 0 30 0 * * * 在八点半运行

## Thanks
参考<a href="https://github.com/Tishacy/ZJU-nCov-Hitcarder">ZJU-nCov-Hitcarder项目</a>

## LICENSE

Copyright (c) 2020 yep96.

Licensed under the [MIT License](https://github.com/yep96/ZJU_healthreport/blob/master/LICENSE)


