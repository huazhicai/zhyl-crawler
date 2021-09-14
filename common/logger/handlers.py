# -*- coding:utf-8 -*-
import logging
import os
from logging.handlers import BaseRotatingHandler


class ProcessRotatingFileHandler(BaseRotatingHandler):
    """
    每次重启，写新日志
    """

    def __init__(self, filename, backupCount=9, encoding=None, delay=False):
        super().__init__(filename, 'a', encoding, delay)
        self.backupCount = backupCount

    def emit(self, record):
        logging.FileHandler.emit(self, record)

    def doRollover(self):
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename('%s.%d' % (self.baseFilename, i))
                dfn = self.rotation_filename('%s.%d' % (self.baseFilename, i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + '.1')
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()
