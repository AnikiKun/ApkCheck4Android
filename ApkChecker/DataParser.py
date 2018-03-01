#coding:utf-8

'''
author: HuangWeiDong
created: 2016-09-01 17:52:05
'''

import logging
from ApkChecker.CommonLog import commonLog
from xml.etree import ElementTree as ET

class DataParser(object):


    androidNodeNameList = [
        'android.widget.FrameLayout',
        'android.widget.LinearLayout',
        'android.widget.ImageView',
        'android.widget.TextView',
        'android.widget.Button',
    ]

    def __init__(self):
        self.logger = logging.setLoggerClass(commonLog)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def getAllElementList(self, pageDom):
        if isinstance(pageDom,str) or isinstance(pageDom, unicode):
            tree = ET.fromstring(pageDom)
        else:
            tree = ET.parse(pageDom)
        nodes = tree.getiterator("node")
        if len(nodes) == 0:
            for androidTagName in self.androidNodeNameList:
                nodes.extend(tree.getiterator(androidTagName))
        elementList  = []
        for node in nodes:
            elementList.append(node.attrib)
        return elementList


    def getXpathByNodeInfo(self, node):
        text = node['text'] if node['text']!='' else None
        resourceId = node['resource-id'] if node['resource-id']!='' else None
        xPath = ''
        if text:
            xPath = "//*[ @text='{}']".format(text)
        if resourceId:
            if xPath != '':
                xPath = xPath.replace("]","") + " and @resource-id='{}'] ".format(resourceId)
            else:
                xPath = "//*[ @resource-id='{}' ]".format(resourceId)
        return xPath

if __name__ == "__main__":
    tree = ET.parse("window_dump.xml")
    androidNodeNameList = [
        'android.widget.FrameLayout',
        'android.widget.LinearLayout',
        'android.widget.ImageView',
        'android.widget.TextView',
        'android.widget.Button',
    ]
    nodes = []
    for nodeTag in androidNodeNameList:
        nl = tree.getiterator(nodeTag)
        nodes.extend(nl)
    print nodes
    for node in nodes:
        print node.attrib