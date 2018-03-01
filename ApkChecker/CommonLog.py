#coding:utf-8
import logging

'''
author: HuangWeiDong
created: 2016-09-01 17:47:08
'''

class commonLog(logging.Logger):
    """
    Custom logger class with additional levels and methods
    """
    WARNPFX = logging.WARNING+1

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        logging.addLevelName(self.WARNPFX, 'WARNING')
        fileHandle = logging.FileHandler('test.log')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter("[%(levelname)s]%(asctime)s [%(funcName)s: %(filename)s,%(lineno)d] %(message)s")
        fileHandle.setFormatter(formatter)
        console.setFormatter(formatter)

        # add the handlers to logger
        self.addHandler(console)
        self.addHandler(fileHandle)

        return

    def warnpfx(self, msg, *args, **kw):
        self.log(self.WARNPFX, "! PFXWRN %s" % msg, *args, **kw)


# logging.setLoggerClass(commonLog)
# rrclogger = logging.getLogger("rrcheck")
# rrclogger.setLevel(logging.INFO)
#
# def test():
#     rrclogger.debug("DEBUG message")
#     rrclogger.info("INFO message")
#     rrclogger.warnpfx("warning with prefix")

# test()

#
#
# if __name__ == "__main__":
#     LOG = commonLog().log
#     LOG.info("呵呵")
#     LOG.info("呵呵")
#     LOG.debug("呵呵")