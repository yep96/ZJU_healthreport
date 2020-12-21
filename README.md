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
```

尝试着练练手，看着应该是问题不大，风险自负<del>我已经在用了</del>

不会markdown，语文水平也不好，描述颠三倒四只能凑合着看

下载项目后需要修改ZJUHealthReport脚本中37行起的用户名密码，UA，API和脚本位置等信息

area信息的获取：把手机关闭定位或不授予应用定位权限，手动选择相应的位置后填写，如图<a href="https://github.com/yep96/ZJU_healthreport/raw/master/定位.jpg">定位.jpg</a>

data文件中的数据可根据自己情况改，不修改提交效果如图<a href="https://github.com/yep96/ZJU_healthreport/raw/master/健康打卡.jpg">健康打卡.jpg</a>

其他信息可以在电脑上打开<a href="https://healthreport.zju.edu.cn/ncov/wap/default/index">健康打卡网址</a>，查看html信息来修改，如今日在校，搜索到399行
   ```html
    <div name="sfzx" class="radio"><span>今日是否在校？ Are you on campus today?<i class="icon iconfont icon-shuoming"></i><em></em></span>
        <div>
            <div @click="setSfzx('1')"><span :class="{active: info.sfzx==='1'}"><i></i></span> <span>是 Yes</span></div>
            <div @click="setSfzx('0')"><span :class="{active: info.sfzx==='0'}"><i></i></span> <span>否 No</span></div>
        </div>
    </div>

   ```
将data中"sfzx"对应的值改为"1"，其他信息同理。

其中定位我是直接返回定位失败后手动选择地址<del>不过我真的也没有定位成功过</del>

重新打开问卷，地址显示为"点击获取地理位置"没有问题。我试过在钉钉定位失败后手动选择地址提交，重新查看也是同样效果

或者可以先关闭钉钉定位权限并手选地址，填写完后用Fiddle4抓个包看看post了什么数据，搜索url解码后修改data文件，其中地址中的+换成空格，否则前后抓包不一致

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

这个脚本不需要一直运行，通过读取上一次运行时保存的cookies保持会话。也许不用每次都删除后更新cookies，猜测是可用的，没有测试过

如果去掉更新cookies，则可以部署到云函数上自动打卡。需要将ZJUHealthReport.py、cookies和data一起上传，不知道ip和定位不匹配会不会有问题<a href="https://github.com/yep96/ZJU_healthreport/raw/master/阿里云示例.jpg">如图</a>。阿里云服务的crontab最前面多了一个秒，0时区，可用 0 30 0 * * * 在八点半运行

绑定serve酱后，如果打卡失败微信会推送<a href="https://github.com/yep96/ZJU_healthreport/raw/master/打卡失败提醒.jpg">打卡失败提醒.jpg</a>

## Thanks
参考<a href="https://github.com/Tishacy/ZJU-nCov-Hitcarder">ZJU-nCov-Hitcarder项目</a>

## LICENSE

Copyright (c) 2020 yep96.

Licensed under the [MIT License](https://github.com/yep96/ZJU_healthreport/blob/master/LICENSE)


