# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import threading

import wx

from outwiker.gui.texteditor import ApplyStyleEvent


class BaseTextStylingController(metaclass=ABCMeta):
    def __init__(self, application, pageTypeString=None):
        self._application = application
        self._colorizingThread = None
        self._runColorizingEvent = threading.Event()
        self._pageTypeString = pageTypeString

    @abstractmethod
    def getColorizingThread(self, page, params, runEvent):
        pass

    def _onEditorStyleNeeded(self, page, params):
        if (page is None or
                (not page.getTypeString() == self._pageTypeString)):
            return

        if (self._colorizingThread is None or
                not self._colorizingThread.is_alive()):

            thread = self.getColorizingThread(
                page,
                params,
                self._runColorizingEvent)

            if thread is not None:
                self._colorizingThread = thread
                self._runColorizingEvent.set()
                self._colorizingThread.start()

    def initialize(self, page):
        if page.getTypeString() == self._pageTypeString:
            self._bindEvents()

    def clear(self):
        self._unbindEvents()
        self._stopColorizing()

    def _bindEvents(self):
        self._application.onEditorStyleNeeded += self._onEditorStyleNeeded
        self._application.onPreferencesDialogCreate += self._stopEventHandler
        self._application.onPageSelect += self._stopEventHandler

    def _unbindEvents(self):
        self._application.onEditorStyleNeeded -= self._onEditorStyleNeeded
        self._application.onPreferencesDialogCreate -= self._stopEventHandler
        self._application.onPageSelect -= self._stopEventHandler

    def _stopColorizing(self):
        self._runColorizingEvent.clear()

        if self._colorizingThread is not None:
            self._colorizingThread.join()
            self._colorizingThread = None

    def updateStyles(self,
                     editor,
                     text,
                     styleBytes):
        event = ApplyStyleEvent(text=text, styleBytes=styleBytes)
        wx.PostEvent(editor, event)

    def _stopEventHandler(self, *args, **kwargs):
        self._stopColorizing()
