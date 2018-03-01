#coding:utf-8

'''
author: HuangWeiDong
created: 2016-08-31 16:10:03
'''

import os, subprocess, logging, sys, threading, time, traceback
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from ApkChecker.CommonLog import commonLog
from ApkChecker.DataParser import DataParser
from ApkChecker.CheckerConf import checkerConf
reload(sys)
sys.setdefaultencoding('utf8')


class apkChecker():
    '''

    '''
    desired_caps = {}
    driver = None
    apkFileCount = 0
    curApkFileName = ''
    pageDom = ''
    currentContext = 'native'

    #用于判断应用是否安装好
    driverUp = False

    def __init__(self, aConf=None):
        if aConf != None:
            self.aConf = aConf
        else:
            self.aConf = checkerConf()
        self.device = aConf.deviceId
        logging.setLoggerClass(commonLog)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        timeStamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.resultDir   = os.path.join(os.getcwd(),"{}_{}".format(self.device, timeStamp))
        if not os.path.isdir(self.resultDir):
            os.makedirs(self.resultDir)
        logPath     = os.path.join(self.resultDir, 'checkerLog.log')
        logFileHandler = logging.FileHandler(logPath)
        formatter = logging.Formatter("[%(levelname)s]%(asctime)s [%(funcName)s: %(filename)s,%(lineno)d] %(message)s")
        logFileHandler.setFormatter(formatter)
        self.logger.addHandler(logFileHandler)
        self.aConf.resultDir = self.resultDir

    def loadConf(self):
        confPath = self.aConf.confPath
        self.aConf.loadYml(confPath)


    def startAppiumServer(self):
        appiumApp  = self.aConf.appiumApp if self.aConf.appiumApp != "" else "appium"
        appiumLogPath = os.path.join(self.resultDir, 'appiumLog.log')
        self.logger.info("Appium Log Path:{}".format(appiumLogPath))
        appiumPort = self.aConf.ports['appiumPort']
        portCut = int(appiumPort) - 4723
        chromeDriverPort = int(self.aConf.ports['chromeDriverPort']) + portCut
        selendroidPort  = int(self.aConf.ports['selendroidPort']) + portCut
        bootstrapPort  = int(self.aConf.ports['bootstrapPort']) + portCut
        self.logger.info("Start Appium Server...")
        startCmd = "{} -U{} --port={} --bootstrap-port={} --chromedriver-port={} --selendroid-port={} --log-timestamp >{} 2>&1".format(
            appiumApp, self.device, appiumPort, bootstrapPort, chromeDriverPort, selendroidPort,  appiumLogPath
        )
        # import tempfile
        # self.out_temp = tempfile.SpooledTemporaryFile(bufsize=10*1000)
        # fileno = self.out_temp.fileno()
        # self.appiumProcess = subprocess.Popen(startCmd,stderr=fileno,shell=True)
        self.appiumProcess = os.popen(startCmd)


    def startDriver(self):
        '''
        :return:
        '''
        self.logger.info("Session starting...")
        self.desired_caps.update(self.aConf.capability)
        self.driver = webdriver.Remote('http://localhost:{}/wd/hub'.format(self.aConf.ports['appiumPort']), self.desired_caps)
        self.driver.implicitly_wait(15)
        time.sleep(3)

    def start(self):
        '''

        :return:
        '''
        self.logger.info("Start apk check.")
        self.loadConf()
        aServer = threading.Thread(target=self.startAppiumServer)
        aServer.setDaemon(True)
        aServer.start()
        time.sleep(5)
        self.checker()
        if self.appiumProcess:
            self.appiumProcess.close()
            # self.appiumProcess.kill()
        # if self.out_temp:
        #     self.out_temp.close()

    def checker(self):
        '''

        :return:
        '''
        apkFileList = self.getApkFiles()
        i = 1
        for apk in apkFileList:
            self.curApkFileName = apk.replace(self.aConf.apkPath,"").replace("/","")
            self.logger.info("Start checking {}".format(self.curApkFileName))
            self.aConf.capability['app'] = apk
            self.initMobile()
            installingAction = threading.Thread(target=self.installingActions)
            installingAction.setDaemon(True)
            installingAction.start()
            self.startDriver()
            self.driverUp = True
            self.logger.info("Start element check.")
            self.DoWorkFlowAction()
            self.driver.quit()
            self.driverUp = False
            self.logger.info("已遍历渠道包{}个  {}%".format(i,round(float(i)/float(len(apkFileList)),2)*100))
            i+=1

    def getApkFiles(self):
        '''

        :return:
        '''
        self.logger.info("Getting apk files.")
        apkPath = self.aConf.apkPath
        if not os.path.isdir(apkPath):
            raise IOError,"Apk path is not a Dir : {}".format(apkPath)
        apkFileList = map(lambda x:os.path.join(apkPath, x),
                          filter(lambda x:x.endswith(".apk"),
                                 os.listdir(self.aConf.apkPath)))
        self.logger.info("Apk files count: {}".format(len(apkFileList)))
        return apkFileList

    def initMobile(self):
        device = self.device
        uninstallCmd ="adb -s {} uninstall {}".format(device,self.aConf.capability['appPackage']) #["adb", "uninstall", self.aConf.capability['appPackage']]
        self.logger.info('Uninstall history apk...{}'.format(uninstallCmd))
        subprocess.Popen(uninstallCmd, stdout=subprocess.PIPE, shell=True)

    def DoWorkFlowAction(self):
        self.logger.info("Do config actions.")
        workflow = self.aConf.workflow
        for wf in workflow:
            try:
                self.pageDom = self.driver.page_source
                self.beforeActions()
            except:
                pass
                # traceback.print_exc("Get Page Source Fail!")
            self._doAction(wf)

    def _doAction(self, work):
        '''

        :param action:
        :param location:
        :return:
        '''
        action = work.split("::")[0]
        if action == "click":
            location = work.split("::")[1].split(">>>")[0].lower()
            locValue = work.split("::")[1].split(">>>")[1]
            self.logger.info(u"click {} ({})".format(locValue, location))
            if location == "id":
                self.driver.find_element_by_id(locValue).click()
            elif location == "xpath":
                self.driver.find_element_by_xpath(locValue).click()
            elif location == "text":
                self.driver.find_element_by_xpath(u"//*[@text='{}']".format(locValue)).click()
            elif location == "_id":
                self.driver.find_element_by_android_uiautomator('new UiSelector().resourceId("{}")'.format(locValue)).click()
            elif location == "_text":
                self.driver.find_element_by_android_uiautomator(u'new UiSelector().text("{}")'.format(locValue)).click()
            else:
                self.logger.info("unknown location! <- {} ->".format(location))
        elif action == "input":
            location = work.split("::")[1].split(">>>")[0].lower()
            locValue = work.split("::")[1].split(">>>")[1]
            value    = work.split("::")[1].split(">>>")[2]
            self.logger.info(u"input '{}' to {}".format(value, locValue))
            if location == "id":
                self.driver.find_element_by_id(locValue).send_keys(value)
            elif location == "_id":
                self.driver.find_element_by_android_uiautomator(u'new UiSelector().text("{}")'.format(locValue)).send_keys(value)
            elif location == "xpath":
                self.driver.find_element_by_xpath(locValue).send_keys(value)
        elif action == "switch":
            context = work.split("::")[1]
            self._setContext(context)
        elif action == "swipe":
            direct = work.split("::")[1].strip()
            self._swipe(direct)
        elif action == "script":
            script = work.split("::")[1]
            self.logger.info(u"exec > {}".format(script))
            exec(script)
        elif action == "wait":
            locator = work.split("::")[1].split(">>>")[0].lower()
            try:
                locator = int(locator)
            except:
                pass
            if isinstance(locator, int):
                self._wait(ms=locator)
            else:
                locValue = work.split("::")[1].split(">>>")[1]
                seconds = work.split("::")[1].split(">>>")[2]
                try:
                    seconds = int(seconds)
                except:
                     raise KeyError, "The value of seconds [{}] is not correct.".format(seconds)
                self._wait(seconds, locator, locValue)
        else:
            raise AttributeError, "Unknown Action Key Word : {}".format(action)
        if action != "switch" and self.currentContext != 'webview':
            self.screenShot()


    def _setContext(self, context):
        context = context.lower()
        allContexts = self.driver.contexts
        appPackage  = self.aConf.capability['appPackage'].lower()
        self.logger.info("Current context is {}".format(self.driver.current_context))
        for tContext in allContexts:
            if tContext.lower().find(context)>=0 and tContext.lower().find("undefined")<0:
                if (context == "webview" and tContext.split("_")[1].lower() == appPackage) or (context == "native"):
                    self.logger.info(u"找到与当前App匹配的Context： {}".format(tContext))
                    self.driver.switch_to.context(tContext)
                    self.logger.info(u"切换Context至{}成功".format(tContext))
                    self.currentContext = context
                    break
                else:
                    self.logger.info(u"没有找到相关的Context.")
            elif tContext.lower().find(context)>=0 and tContext.lower().find("undefined")>=0:
                #当出现web undefined的时候,重新获取当前的context
                self._setContext(context)
        curContext = self.driver.current_context
        if context not in curContext.lower():
            raise RuntimeError, "Switch context to {} Failed!".format(context)

    def _wait(self, ms, locator=None ,what=None):
        if what == None:
            what = ''
        self.logger.info("Wait {} {}s".format(what, ms))
        if locator == None:
            time.sleep(ms)
        elif locator.lower() == 'id':
            WebDriverWait(self.driver, ms).until(lambda driver:driver.find_element_by_id(what), "{} dose not appear.".format(what))
        elif locator.lower() == 'text':
            xpath = u'//*[@text="{}"]'.format(what)
            WebDriverWait(self.driver, ms).until(lambda driver:driver.find_element_by_xpath(xpath), "{} dose not appear.".format(what))
        elif locator.lower() == '_text':
            WebDriverWait(self.driver, ms).until(lambda driver:driver.find_element_by_android_uiautomator(u'new UiSelector().text("{}")'.format(what)), "{} dose not appear.".format(what))
        elif locator.lower() == '_id':
            WebDriverWait(self.driver, ms).until(lambda driver:driver.find_element_by_android_uiautomator(u'new UiSelector().resourceId("{}")'.format(what)), "{} dose not appear.".format(what))
        elif locator.lower() == 'xpath':
            WebDriverWait(self.driver, ms).until(lambda driver:driver.find_element_by_xpath(what), "{} dose not appear.".format(what))
        else:
            raise AttributeError, "Unknown Action Location: {}".format(locator)

    def _swipe(self, direct):
        '''

        :param direct:
        :return:
        '''
        self.logger.info("Swipe {}".format(direct))
        if direct.lower() == "left":
            self.driver.swipe(0.9, 0.5, 0.2, 0.5, duration=2000)
        elif direct.lower() == "right":
            self.driver.swipe(0.2, 0.5, 0.9, 0.5, duration=1500)
        elif direct.lower() == "up":
            self.driver.swipe(0.5, 0.9, 0.5, 0.1, duration=1500)
        elif direct.lower() == "down":
            self.driver.swipe(0.5, 0.2, 0.5, 0.9, duration=1500)
        else:
            self.logger.error("Unknown direct:{}".format(direct))

    def beforeActions(self):
        '''

        :return:
        '''
        self.logger.info("Doing action before work step.")
        elementActions = self.aConf.elementActions
        for elementAction in elementActions:
            action = elementAction['action']
            locator = elementAction['locator']
            allElements = DataParser().getAllElementList(self.pageDom)
            tElements = filter(lambda x:x['text']==locator or x['resource-id'].find(locator)>=0, allElements)
            while len(tElements)>0:
                if action == "click":
                    for e in tElements:
                        eXpath = DataParser().getXpathByNodeInfo(e)
                        self.logger.info("Click Element : {}".format(eXpath))
                        self.driver.find_element_by_xpath(eXpath).click()
                else:
                    for e in tElements:
                        eXpath = DataParser().getXpathByNodeInfo(e)
                        self.logger.info("Click Element : {}".format(eXpath))
                        self.driver.find_element_by_xpath(eXpath).send_keys(action)
                self.pageDom = self.driver.page_source
                allElements = DataParser().getAllElementList(self.pageDom)
                tElements = filter(lambda x:x['text']==locator or x['resource-id'].find(locator)>=0, allElements)
                self.screenShot()

    def installingActions(self):
        '''

        :return:
        '''
        self.logger.info("Installing Actions start")
        device = self.device
        appPackage = self.aConf.capability['appPackage']
        installingActions = self.aConf.installingActions
        self.logger.info("Pre actions:"+",".join(installingActions))
        while(not self.driverUp):
            unLockAppInstallStr = os.popen("adb -s {} shell pm path io.appium.unlock".format(device)).read()
            tAppInstallStr = os.popen("adb -s {} shell pm path {}".format(device,appPackage)).read()
            if(unLockAppInstallStr.find("io.appium.unlock") > 0 and tAppInstallStr.find(appPackage) > 0):
                self.driverUp = True
                continue
            subprocess.Popen("adb -s {} shell rm /data/local/tmp/uidump.xml".format(device),stdout=subprocess.PIPE, shell=True)
            subprocess.Popen("adb -s {} shell uiautomator dump /data/local/tmp/uidump.xml".format(device), stdout=subprocess.PIPE,shell=True)
            dumpSuccessFlag = False
            pageSource = os.popen("adb -s {} shell cat /data/local/tmp/uidump.xml".format(device)).read()
            while not dumpSuccessFlag:
                if pageSource.find("No such file")>0 or pageSource == '':
                    pageSource = os.popen("adb -s {} shell cat /data/local/tmp/uidump.xml".format(device)).read()
                    continue
                dumpSuccessFlag = True
            # self.logger.info(pageSource)
            allMap = DataParser().getAllElementList(pageSource)
            for installingAction in installingActions:
                # self.logger.info(installingAction)
                allMap = filter(lambda x:x['text']==installingAction or x['resource-id'].find(installingAction)>=0, allMap)
                for e in allMap:
                    self.logger.info("Found element :{}".format(e))
                    bounds = e['bounds']
                    boundsList = bounds.replace("][",",").replace("[","").replace("]","").split(",")
                    boundX = (int(boundsList[0]) + int(boundsList[2]))/2
                    boundY = (int(boundsList[1]) + int(boundsList[3]))/2
                    self.logger.info("click coordinate on {}, {}".format(boundX,boundY))
                    subprocess.Popen("adb -s {} shell input tap {} {}".format(device, boundX, boundY), shell=True)

    def screenShot(self):
        needShot = self.aConf.screenShot
        if needShot:
            timeStamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
            fileName =  '{}_{}.png'.format(self.curApkFileName.replace(".apk","").strip(),timeStamp)
            shotFileName = os.path.join(self.aConf.resultDir, fileName)
            if sys.platform == 'win32':
                shotFileName = os.path.join(self.aConf.resultDir+'\\'+fileName)
            self.logger.info("Save ScreenShot File: {}".format(shotFileName))
            try:
                self.driver.get_screenshot_as_file(shotFileName)
            except Exception,e:
                self.logger.error("Save ScreenShot Failed! Exception: {}".format(e))

if __name__ == "__main__":
    # ApkChecker().start()
    # ac = apkChecker()
    # ac.loadConf()
    # ac.installingActions()
    pass