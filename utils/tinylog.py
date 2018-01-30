#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
simple logging handler
usage:

log = LogHandler("tst.log",logName="test",level="info")
log.debug("debug message")
log.info("info message")

'''


import logging
import logging.handlers


class LogHandler(object):

    def __init__(self, fileName, fileSize=0, backupCount=0,
                 logName=None, level="info"
                 ):
        self.fileName = fileName
        self.fileSize = fileSize
        self.backupCount = backupCount
        self.logName = logName
        self.level = level.lower()
        levelDict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        handler = logging.handlers.RotatingFileHandler(
            fileName, maxBytes=fileSize, backupCount=backupCount,
            encoding="utf-8", delay=0
        )
        fmt = logging.Formatter(
            "%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s"
        )
        # %(levelname)s

        handler.setFormatter(fmt)
        # set name who make log
        self.logger = logging.getLogger(self.logName)
        self.logger.addHandler(handler)
        self.logger.setLevel(levelDict[self.level])
        self.logger.info("**************  %s  **************" % fileName)

    def debug(self, msg): return self.logger.debug(msg)

    def info(self, msg): return self.logger.info(msg)

    def warning(self, msg): return self.logger.warning(msg)

    def error(self, msg): return self.logger.error(msg)

    def critical(self, msg): return self.logger.critical(msg)

    def exception(self, msg): return self.logger.exception(msg)
