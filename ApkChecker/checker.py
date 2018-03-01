# -*- coding:utf-8 -*-

'''
author: HuangWeiDong
created: 2016-09-02 17:57:25
'''
import sys, getopt, os
from ApkChecker.CheckerConf import checkerConf
from ApkChecker.AndroidChecker import apkChecker

def main():
    argv = sys.argv[1:]
    apkPath = ""
    confPath = ""
    deviceId = ""

    aConf = checkerConf()

    root = os.getcwd()
    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hc:f:d:p:", ["path=", "conf=", "device=", "port="])
    except getopt.GetoptError:
        print 'Error: apkchecker -f <apkFilePath> -c <configFile> -d <deviceId>'
        print '   or: apkchecker --path=<apkFilePath> --conf=<configFile> --device=<deviceId>'
        sys.exit(2)


    for opt, arg in opts:
        if opt == "-h":

            print r'''
////////////////////////////////////////////////////////////////////
//                          _ooOoo_                               //
//                         o8888888o                              //
//                         88" . "88                              //
//                         (| ^_^ |)                              //
//                         O\  =  /O                              //
//                      ____/`---'\____                           //
//                    .'  \\|     |//  `.                         //
//                  /  _||||| -:- |||||-  \                       //
//                  | \_|  ''\---/''  |   |                       //
//                  \  .-\__  `-`  ___/-. /                       //
//                ___`. .'  /--.--\  `. . ___                     //
//              ."" '<  `.___\_<|>_/___.'  >'"".                  //
//      ========`-.____`-.___\_____/___.-`____.-'========         //
//                           `=---='                              //
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
//                   ApkChecker UI Helper  v0.8                   //
////////////////////////////////////////////////////////////////////
'''

            print 'ApkCheck Help:'
            print '     -f --path: apk files path'
            print '     -c --conf: config file'
            print '     -d --device: deviceId, udid'

            print 'Sample:'
            print '     apkchecker -f <apkFilePath> -c <configFile> -d <deviceId>'
            print '     Or: apkchecker --path=<apkFilePath> --conf=<configFile> --device=<deviceId>'
            print '  Multi device test:'
            print '     apkchecker -f <apkFilePath> -c <configFile> -d <deviceId> -p 4730'
            print '     Or: apkchecker --path=<apkFilePath> --conf=<configFile> --device=<deviceId> --port=4730'
            sys.exit()
        elif opt in ("-f", "--path"):
            apkPath = os.path.join(root,arg)
            aConf.apkPath = apkPath
        elif opt in ("-c", "--conf"):
            confPath = arg
            aConf.confPath = confPath
        elif opt in ("-d", "--device"):
            deviceId = arg
            aConf.deviceId = deviceId
        elif opt in ("-p", "--port"):
            port = arg
            aConf.ports['appiumPort'] = port

    if apkPath == "":
        print("Error: Apk Path cannot be empty.")
        sys.exit(2)
    if confPath == "":
        print("Error: Config Path cannot be empty.")
        sys.exit(2)
    if deviceId == "":
        print("Error: DeviceId cannot be empty.")
        sys.exit(2)


    apkChecker(aConf).start()

if __name__ == "__main__":
    main()
