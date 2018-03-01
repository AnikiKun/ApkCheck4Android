#coding:utf-8

import yaml

'''
author 'huangweidong'
created 2016-08-31 16:32:19
'''
class checkerConf(object):


    #是否截图
    screenShot = False

    #是否跳过当前错误包
    ignoreErrorApk = False

    #指定apk文件的目录
    apkPath = ""

    #配置文件的路径
    confPath = ""

    #连接设备
    deviceId = ""

    #报告目录
    resultDir = ""

    #appium的启动路径
    appiumApp = "appium"

    #端口
    ports = {
        "appiumPort": 4723,
        "chromeDriverPort": 9515,
        "selendroidPort": 8088,
        "bootstrapPort": 7474
    }

    #appium session启动参数
    capability = {
        "app":"",
        "platformName":"Android",
        "platformVersion":"5.0",
        "deviceName":"test",
        "appPackage":"",
        "appActivity":"",
        "unicodeKeyboard":"true",
        "resetKeyboard":"true"
    }

    #需要遍历的业务流
    workflow = []

    #安装前的元素才做
    installingActions = []

    #元素触发操作
    elementActions = []

    def loadYml(self, confFile):
        '''

        :return:
        '''
        content = yaml.load(file(confFile, 'r'))
        for key,value in content.items():
            if isinstance(value,dict):
                getattr(self,key).update(value)
            else:
                setattr(self,key,value)
        return self

if __name__ == "__main__":

    aConf = checkerConf()
    # confPath = os.path.join(os.getcwd(), "conf", "hjclass.yml")
    o = aConf.loadYml("/Users/zhaoziliang/PycharmProjects/AndroidApkChecker/conf/hjclass.yml")
    print aConf.capability
    print aConf.apkPath