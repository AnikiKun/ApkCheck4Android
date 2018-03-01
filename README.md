
# ApkChecker
    一款基于Python与Appium的UI自动化检查工具。目前支持简单的Bvt自动化用例定制，以及支持批量渠道包遍历。

    做这个工具的思路其实还是因为每当发包时，总有上百个渠道包需要遍历，以前用Monkeyrunner写的版本不太稳定，换机器后经常失败。所以开发了这款工具，对MonkeyRunner版本有兴趣的同学可以参考https://github.com/AnikiKun/MonkeyRunner_ApkTest


### 特色
- 基于Python开发，通过SetupTools直接安装即可
- 业务脚本编写通俗化
- 内置守护程序
- 多设备同时执行，效率效率再效率
- 脚本、路径、设备、全配置化，一个配置文件即可解决所有问题

### 使用方法

- 1、下载源码
- 2、运行`python setup.py install`，安装好apkchecker，在命令行中执行`apkchecker -h`查看是否安装成功
- 3、准备好渠道包并都放在一个目录中
- 4、设置好配置文件，可参考demo.yml
- 5、执行测试
`apkchecker -f <apkFilePath> -c <configFile> -d <deviceId>`


### 配置文件写法
```xml

#appium的启动程序路径
#appiumApp: "appium"

#是否截图
screenShot: True

#是否跳过当前错误包
ignoreErrorApk: False

#指定apk的包名和启动activity
capability:
  appPackage: "com.hujiang.hjclass"
  appActivity: ".activity.SplashActivity"

#每个包需要遍历的业务，支持TEXT、ID、XPATH和代码的定位方式(text和id支持android uiautomator的定位方式，写法：_text, _id)
workflow:
- "wait::5"
- "wait::_text>>>语音翻译新功能>>>15"
- "swipe::left"
- "wait::_text>>>详情页面新设计>>>15"
- "swipe::left"
- "click::_text>>>登录"
- "switch::webview"
- "input::xpath>>>//*[@id='hp-login-normal']/div[1]/input>>>玉芳姐"
- "input::xpath>>>//*[@id='hp-login-normal']/div[3]/input>>>zhangzili123"
- "click::xpath>>>//*[@id='hp-login-normal']/button"
- "switch::native"
- "click::_text>>>我的"
- "wait::_text>>>玉芳姐"


#安装应用过程中的意外弹窗处理，暂仅支持文本和ID
installingActions:
- "继续安装"

#处理在workflow执行过程中的意外弹窗以及元素
elementActions:
- action: "click"
  locator: "允许"
```



