# -*- coding: utf-8 -*-

import sys
import logging
import time


class LogRedirector:
    def __init__(self, filename, level):
        self._terminal = sys.stdout
        self._fname = filename
        self._level = level

    def init(self):
        sys.stdout = self
        sys.stderr = self

        self._firstWrite = True

        self._runTime = time.strftime(u'%Y-%m-%d %H:%M:%S')

        logging.basicConfig(format='%(levelname)-10s %(asctime)-25s %(name)s - %(module)s - %(message)s',
                            level=self._level)
        logging.getLogger("comtypes").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)

    def write(self, message):
        if self._terminal is not None:
            self._terminal.write(message)

        with open(self._fname, "a", encoding='utf8') as fp:
            if self._firstWrite:
                fp.write(u'\n\n{} - START\n'.format(self._runTime))
                self._firstWrite = False
            fp.write(message)

    def flush(self):
        if self._terminal is not None:
            self._terminal.flush()

    def fileno(self):
        if self._terminal is not None:
            return self._terminal.fileno()

        return None
