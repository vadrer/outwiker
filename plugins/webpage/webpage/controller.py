# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys

from outwiker.core.factoryselector import FactorySelector
from outwiker.utilites.textfile import writeTextFile

from .webnotepage import WebPageFactory, WebNotePage
from .spellcontroller import WebPageSpellController
from .i18n import get_
from .gui.guicontroller import GuiController

from .actions.downloadaction import (CreateChildWebPageAction,
                                     CreateSiblingWebPageAction)
from .actions.opensourceurl import OpenSourceURLAction
from .actions.showpageinfo import ShowPageInfoAction
from .actions.disablescripts import DisableScriptsAction
from .actions.copysourceurl import CopySourceURLToClipboardAction

from .misc import onPrepareHtmlEventString
from .events import PrepareHtmlEventParams
from .htmlprocessors.disablescripts import disableScripts
from .htmlprocessors.maxieversion import maxIEVersion


logger = logging.getLogger('webpage')

class Controller:
    """General plugin controller."""

    def __init__(self, plugin, application):
        self._plugin = plugin
        self._application = application
        self._guiController = GuiController(self._application)

        self._spellController = WebPageSpellController(self._application)
        self._actions = [
            (CreateChildWebPageAction, None),
            (CreateSiblingWebPageAction, None),
            (OpenSourceURLAction, None),
            (ShowPageInfoAction, None),
            (DisableScriptsAction, None),
            (CopySourceURLToClipboardAction, None),
        ]

        self._htmlProcessors = [
            disableScripts,
            maxIEVersion,
        ]

    def initialize(self):
        global _
        _ = get_()

        self._correctSysPath()
        self._application.onPageDialogPageFactoriesNeeded += self._onPageDialogPageFactoriesNeeded
        self._application.onPageViewDestroy += self._onPageViewDestroy
        self._application.onPageViewCreate += self._onPageViewCreate
        self._application.onPageUpdateNeeded += self._onPageUpdateNeeded

        self._registerHtmlProcessors()

        if self._application.mainWindow is not None:
            self._registerActions()
            self._guiController.initialize()
        FactorySelector.addFactory(WebPageFactory())

    def destroy(self):
        self._application.onPageDialogPageFactoriesNeeded -= self._onPageDialogPageFactoriesNeeded
        self._application.onPageViewDestroy -= self._onPageViewDestroy
        self._application.onPageViewCreate -= self._onPageViewCreate
        self._application.onPageUpdateNeeded -= self._onPageUpdateNeeded

        self._unregisterHtmlProcessors()

        if self._application.mainWindow is not None:
            self._guiController.destroy()
            self._unregisterActions()

        if (self._application.selectedPage is not None and
                self._application.selectedPage.getTypeString() == WebNotePage.getTypeString()):
            self._spellController.clear()

        FactorySelector.removeFactory(WebPageFactory().getTypeString())

    def _registerHtmlProcessors(self):
        for proc in self._htmlProcessors:
            self._application.getEvent(onPrepareHtmlEventString).bind(proc)

    def _unregisterHtmlProcessors(self):
        for proc in self._htmlProcessors:
            self._application.getEvent(onPrepareHtmlEventString).unbind(proc)

    def _registerActions(self):
        [*map(lambda actionTuple: self._application.actionController.register(
            actionTuple[0](self._application), actionTuple[1]), self._actions)]

    def _unregisterActions(self):
        [*map(lambda actionTuple: self._application.actionController.removeAction(
            actionTuple[0].stringId), self._actions)]

    def _correctSysPath(self):
        cmd_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'libs')

        if cmd_folder not in sys.path:
            logger.debug('Add path to sys.path: {}'.format(cmd_folder))
            sys.path.insert(0, cmd_folder)

    def _onPageDialogPageFactoriesNeeded(self, page, params):
        if(params.pageForEdit is not None and
                params.pageForEdit.getTypeString() == WebNotePage.getTypeString()):
            params.addPageFactory(WebPageFactory())

    def _onPageViewCreate(self, page):
        assert page is not None
        if page.getTypeString() == WebNotePage.getTypeString():
            self._spellController.initialize(page)

    def _onPageViewDestroy(self, page):
        assert page is not None
        if page.getTypeString() == WebNotePage.getTypeString():
            self._spellController.clear()

    def _onPageUpdateNeeded(self, page, params):
        if (page is not None and
                page.getTypeString() == WebNotePage.getTypeString()):
            self._updatePage(page)
            self._application.mainWindow.pagePanel.pageView.updateHtml()

    def _updatePage(self, page):
        path = page.getHtmlPath()
        html = self.generateHtml(page)
        writeTextFile(path, html)

    def generateHtml(self, page):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(page.content, "html.parser")
        params = PrepareHtmlEventParams(self._application.selectedPage, soup)
        self._application.getEvent(onPrepareHtmlEventString)(params)
        html = params.soup.decode()

        return html
