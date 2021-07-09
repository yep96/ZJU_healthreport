# ZJU_healthreport
浙大健康打卡自动化脚本

```
 8/8  更新表单，对“以下地区返回浙江”表单内容简单的检测，判断表单是否更改
 8/29 前两天把Linux小服务器弄坏了，今天就检测出表单已修改。今天抓包修改程序，明天测试程序是否正常运行
 8/30 修改语法错误，测试通过可正常使用。务必设置提醒api，否则如果签到失败会没提醒。简易检测有无新版
 9/2  添加阿里云云函数版index_Ali.py，使用前需在本地运行ZJUHealthReport.py获取cookies文件，将cookies、data文件
      上传至代码同级目录。触发器选择定时触发器，cron表达式“0 30 0 * * *”为北京时间8点30分运行
 9/26 修改正则匹配，学校去掉了几个"导致匹配失败
 9/27 修改data中错误
10/26 修改正则匹配，学校重新加上了几个"导致匹配失败
11/30 更新表单匹配
12/21 更新表单匹配及提交表格
 1/14 更新表单匹配及提交表格
 1/15 更新表单匹配
  2/6 更新表单匹配
 5/19 原来以为学校把数据加密了，原来是前一天没有打卡导致没有缓存数据。改了一下继续用
  7/9 增加多人任务，可以帮同学打卡了，只用获取cookies保存到此目录下后修改名字即可。不再对"id":"XXX"和"id":XXX进行区分
```

听同学说有个健康打卡的网站，输入统一认证一卡通、密码后定时打卡。网站所有者可能不拿来干什么，但是将账号密码发送给陌生人是一件很危险的事情。

所以最近修改了一个阿里云函数的版本。将data，cookies，ali.py上传至云函数平台，设置触发任务为时间触发 0 30 0 * * * 即可在八点半运行。若上传了cookies则不必在脚本中填写账号密码，否则必须填写（cookies本身有效期是1个月，如果本地用session每次会更新不会失效，在云函数上不确定，正在测试）。试了一个多星期没问题，没试过更久的

相对于别的打卡脚本，我这个显得麻烦的多，又要更新又要设置api、ua的。为了更像真人，这里选择用cookies保持，而不是每次都重新登录；同时如果打卡网页发生改变，提交不对应的信息其实也能打卡成功，但学校会不会认真我也不知道。所以脚本的容差性是故意写的很差的，以免网页修改后乱打卡。不做GitHub action是因为这是境外ip。希望是想的太多吧

钉钉api：由于serve酱的公众号通道即将关闭，本项目改用钉钉机器人。1.随便拉2个同学建钉钉群 2.点自己的头像，选择机器人管理 3.选择自定义 4.添加到刚刚创建的群，选自定义关键词 通知 5.将获取到的webhook地址填到脚本中 6.将其他人从群聊中移出

area信息的获取：健康打卡中所在地点即可，如图<a href="https://github.com/yep96/ZJU_healthreport/raw/master/定位.jpg">定位.jpg</a>

data文件中的数据可根据自己情况改，不修改提交效果如图<a href="https://github.com/yep96/ZJU_healthreport/raw/master/健康打卡.jpg">健康打卡.jpg</a>

建议在电脑上打开<a href="https://healthreport.zju.edu.cn/ncov/wap/default/index">健康打卡网址</a>，按自己的情况填写后按F12，选择Network，断网（可选）点提交后，复制Form后，修改成提供文件的形式写入data文件。可用正则(.*):\ (.*)替换为'\1':'\2',

脚本需安装requests模块
   ```bash
   $ python3 -m pip install requests -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   ```

运行
   ```bash
   $ python3 ZJUHealthReport.py
   ```

crontab定时任务，如在8点30打卡
   ```bash
   $ crontab -e
   $ 30 8 * * * python3 /YOUR_PATH/ZJUHealthReport.py
   ```

这个脚本不需要一直运行，通过读取上一次运行时保存的cookies保持会话。

## Thanks
参考<a href="https://github.com/Tishacy/ZJU-nCov-Hitcarder">ZJU-nCov-Hitcarder项目</a>

## LICENSE

Copyright (c) 2020 yep96.

Licensed under the [MIT License](https://github.com/yep96/ZJU_healthreport/blob/master/LICENSE)


