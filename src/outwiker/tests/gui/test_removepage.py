# -*- coding: utf-8 -*-

import unittest

import wx

from outwiker.app.actions.removepage import RemovePageAction
from outwiker.api.services.tree import removePage
from outwiker.gui.tester import Tester
from outwiker.pages.text.textpage import TextPageFactory
from outwiker.tests.basetestcases import BaseOutWikerGUIMixin


class RemovePageGuiTest(unittest.TestCase, BaseOutWikerGUIMixin):
    """
    Тесты удаления страниц через интерфейс
    """

    def setUp(self):
        self.initApplication()
        self.wikiroot = self.createWiki()

        factory = TextPageFactory()
        factory.create(self.wikiroot, "Страница 1", [])
        factory.create(self.wikiroot, "Страница 2", [])
        factory.create(self.wikiroot["Страница 2"], "Страница 3", [])

    def tearDown(self):
        self.destroyApplication()
        self.destroyWiki(self.wikiroot)

    def testCommandRemove_01(self):
        Tester.dialogTester.appendNo()

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = self.wikiroot["Страница 1"]

        removePage(self.wikiroot["Страница 1"])

        self.assertNotEqual(self.wikiroot["Страница 1"], None)

    def testCommandRemove_02(self):
        Tester.dialogTester.appendYes()

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = self.wikiroot["Страница 1"]

        removePage(self.wikiroot["Страница 1"])

        self.assertEqual(self.wikiroot["Страница 1"], None)

    def testCommandRemove_03(self):
        Tester.dialogTester.appendYes()

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = None

        removePage(self.wikiroot["Страница 1"])

        self.assertEqual(self.wikiroot["Страница 1"], None)

    def testCommandRemove_04(self):
        Tester.dialogTester.appendYes()

        removePage(self.wikiroot["Страница 1"])

        self.assertEqual(self.wikiroot["Страница 1"], None)

    def testCommandRemove_05_ReadOnly(self):
        Tester.dialogTester.appendOk()
        self.wikiroot["Страница 1"].readonly = True

        removePage(self.wikiroot["Страница 1"])

        self.assertNotEqual(self.wikiroot["Страница 1"], None)

    def testCommandRemove_06(self):
        Tester.dialogTester.appendYes()

        removePage(self.wikiroot["Страница 2/Страница 3"])

        self.assertEqual(self.wikiroot["Страница 2/Страница 3"], None)
        self.assertNotEqual(self.wikiroot["Страница 2"], None)

    def testCommandRemove_08_root(self):
        # Tester.dialogTester.appendYes()
        self.application.mainWindow.toaster.counter.clear()

        removePage(self.wikiroot)

        # self.assertEqual(Tester.dialogTester.count, 0)
        self.assertEqual(
            self.application.mainWindow.toaster.counter.showErrorCount,
            1)

    def testCommandRemove_07_IOError(self):
        def removeBeforeRemove(dialog):
            self.wikiroot["Страница 2/Страница 3"].remove()
            # Для сообщения об ошибке удаления
            Tester.dialogTester.appendOk()
            return wx.YES

        self.application.mainWindow.toaster.counter.clear()
        Tester.dialogTester.append(removeBeforeRemove)

        removePage(self.wikiroot["Страница 2/Страница 3"])

        # Убедимся, что были показаны все сообщения
        self.assertEqual(
            self.application.mainWindow.toaster.counter.showErrorCount,
            1)

    def testActionRemovePage_01(self):
        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = None

        self.application.actionController.getAction(
            RemovePageAction.stringId).run(None)

        self.assertNotEqual(self.wikiroot["Страница 1"], None)
        self.assertNotEqual(self.wikiroot["Страница 2"], None)

    def testActionRemovePage_02(self):
        Tester.dialogTester.appendYes()

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = self.wikiroot["Страница 1"]

        self.application.actionController.getAction(
            RemovePageAction.stringId).run(None)

        self.assertEqual(self.wikiroot["Страница 1"], None)
        self.assertNotEqual(self.wikiroot["Страница 2"], None)

    def testActionRemovePage_03(self):
        Tester.dialogTester.appendYes()

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = self.wikiroot["Страница 2/Страница 3"]

        self.application.actionController.getAction(RemovePageAction.stringId).run(None)

        self.assertEqual(self.wikiroot["Страница 2/Страница 3"], None)
        self.assertNotEqual(self.wikiroot["Страница 2"], None)
