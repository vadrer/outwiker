# -*- coding: utf-8 -*-

import os
import os.path
from tempfile import mkdtemp
from unittest import TestCase

from outwiker.api.core.tree import createNotesTree
from outwiker.core.attachment import Attachment
from outwiker.core.style import Style
from outwiker.gui.guiconfig import HtmlRenderConfig
from outwiker.pages.wiki.wikipage import WikiPageFactory
from outwiker.pages.wiki.emptycontent import EmptyContent
from outwiker.pages.wiki.wikiconfig import WikiConfig
from outwiker.pages.wiki.wikihashcalculator import WikiHashCalculator
from outwiker.tests.utils import removeDir
from outwiker.tests.basetestcases import BaseOutWikerMixin


class WikiHashTest (BaseOutWikerMixin, TestCase):
    def setUp(self):
        self.initApplication()

        self.filesPath = "testdata/samplefiles/"
        self.__createWiki()

        files = ["image.jpg", "dir"]

        fullFilesPath = [
            os.path.join(
                self.filesPath,
                fname) for fname in files]

        self.attach_page2 = Attachment(self.wikiroot["Страница 2"])

        # Прикрепим к двум страницам файлы
        Attachment(self.testPage).attach(fullFilesPath)

        self.wikitext = """Бла-бла-бла
        %thumb maxsize=250%Attach:image.jpg%%
        Бла-бла-бла"""

        self.testPage.content = self.wikitext

        self.__htmlconfig = HtmlRenderConfig(self.application.config)
        self.__setDefaultConfig()

    def __setDefaultConfig(self):
        self.__htmlconfig.userStyle.value = ""

        # Установим размер превьюшки, не совпадающий с размером по умолчанию
        self.application.config.set(WikiConfig.WIKI_SECTION,
                                    WikiConfig.THUMB_SIZE_PARAM,
                                    WikiConfig.THUMB_SIZE_DEFAULT)

        self.application.config.set(HtmlRenderConfig.HTML_SECTION,
                                    HtmlRenderConfig.FONT_FACE_NAME_PARAM,
                                    HtmlRenderConfig.FONT_NAME_DEFAULT)

    def __createWiki(self):
        # Здесь будет создаваться вики
        self.path = mkdtemp(prefix='Абырвалг абыр')

        self.wikiroot = createNotesTree(self.path)

        WikiPageFactory().create(self.wikiroot, "Страница 2", [])
        self.testPage = self.wikiroot["Страница 2"]

    def tearDown(self):
        self.destroyApplication()
        removeDir(self.path)

    def testHash1(self):
        # Только создали страницу, кешировать нельзя
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.testPage.content = "бла-бла-бла"
        hash2 = hashCalculator.getHash(self.testPage)

        self.assertNotEqual(hash_src, hash2)

        # Добавим файл
        attach = Attachment(self.testPage)
        attach.attach([os.path.join(self.filesPath, "add.png")])

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash_src, hash3)
        self.assertNotEqual(hash2, hash3)

    def testHash2(self):
        # Только создали страницу, кешировать нельзя
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.testPage.content = "бла-бла-бла"
        hash2 = hashCalculator.getHash(self.testPage)

        self.assertNotEqual(hash_src, hash2)

        self.testPage.content = self.wikitext

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash_src, hash3)
        self.assertNotEqual(hash2, hash3)

    def testHashRename(self):
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.testPage.title = "Новый заголовок"
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash_src, hash2)

        self.testPage.title = "Страница 2"
        hash3 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash_src, hash3)

    def testCacheEmpty(self):
        emptycontent = EmptyContent(self.application.config)
        self.testPage.content = ""

        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        # Страница пустая, изменился шаблон для путой записи
        emptycontent.content = "1111"
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash_src, hash2)

        # Изменилось содержимое страницы
        self.testPage.content = "Бла-бла-бла"
        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash3)
        self.assertNotEqual(hash_src, hash3)

        # Изменился шаблон страницы, но страница уже не пустая
        emptycontent.content = "2222"
        hash4 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash4, hash3)

    def testCacheSubdir(self):
        attach = Attachment(self.testPage)
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        # Добавим файл в dir
        with open(os.path.join(attach.getAttachPath(), "dir", "temp.tmp"), "w") as fp:
            fp.write("bla-bla-bla")

        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash_src, hash2)

        # Добавим еще одну вложенную директорию
        subdir = os.path.join(attach.getAttachPath(), "dir", "subdir_2")
        os.mkdir(subdir)

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash3)
        self.assertNotEqual(hash_src, hash3)

        # Добавим файл в dir/subdir_2
        with open(os.path.join(subdir, "temp2.tmp"), "w") as fp:
            fp.write("bla-bla-bla")

        hash4 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash3, hash4)
        self.assertNotEqual(hash2, hash4)
        self.assertNotEqual(hash_src, hash4)

    def testCacheSubpages(self):
        """
        Проверка кэширования при добавлении новых подстраниц
        """
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        # Добавляем новую подстраницу
        WikiPageFactory().create(self.testPage, "Подстраница 1", [])
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

        # Удалим новую страницу
        self.testPage["Подстраница 1"].remove()

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash3, hash_src)

    def testCacheStyle(self):
        """
        Проверка на то, что изменение стиля страницы сбрасывает кэш
        """
        style = Style()
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        exampleStyleDir = "testdata/styles/example_jblog/example_jblog"
        exampleStyleDir2 = "testdata/styles/example_jnet/example_jnet"

        # Изменим стиль страницы
        style.setPageStyle(self.testPage, exampleStyleDir)
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

        # Еще раз изменим стиль
        style.setPageStyle(self.testPage, exampleStyleDir2)
        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash3)
        self.assertNotEqual(hash3, hash_src)

        # Изменим стиль на тот же
        style.setPageStyle(self.testPage, exampleStyleDir2)
        hash4 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash4, hash3)

        # Установим стиль по умолчанию
        style.setPageStyleDefault(self.testPage)
        hash5 = hashCalculator.getHash(self.testPage)
        self.assertEqual(hash5, hash_src)

    def testCacheLoadPlugins1(self):
        """
        Проверка на то, что при изменении списка установленных плагинов не работает кэширование
        """
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        # Загрузили плагин. Кэш не должен сработать
        self.application.plugins.load(["testdata/plugins/testempty1"])
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

        # Загрузили еще один плагин
        self.application.plugins.load(["testdata/plugins/testempty2"])
        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash3, hash2)
        self.assertNotEqual(hash3, hash_src)

    def testCacheLoadPlugins2(self):
        """
        Проверка на то, что при изменении списка установленных плагинов не работает кэширование
        """
        self.application.plugins.clear()
        self.application.plugins.load(["testdata/plugins/testempty1"])
        self.application.plugins.load(["testdata/plugins/testempty2"])

        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.application.plugins.clear()
        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

        # Перезагрузим плагины в другом порядке
        self.application.plugins.load(["testdata/plugins/testempty1"])
        self.application.plugins.load(["testdata/plugins/testempty2"])

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash3, hash2)
        self.assertEqual(hash3, hash_src)

        self.application.plugins.clear()

    def testConfigThumbSizeCache(self):
        """
        Тест на то, что на кэширование влияет изменение размера превьюшки по умолчанию
        """
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.application.config.set(WikiConfig.WIKI_SECTION,
                                    WikiConfig.THUMB_SIZE_PARAM,
                                    WikiConfig.THUMB_SIZE_DEFAULT + 100)

        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

        self.application.config.set(WikiConfig.WIKI_SECTION,
                                    WikiConfig.THUMB_SIZE_PARAM,
                                    "Бла-бла-бла")

        hash3 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash3, hash2)
        self.assertEqual(hash3, hash_src)

    def testConfigFontNameCache(self):
        """
        Тест на то, что на кэширование влияет изменение размера превьюшки по умолчанию
        """
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.application.config.set(HtmlRenderConfig.HTML_SECTION,
                                    HtmlRenderConfig.FONT_FACE_NAME_PARAM,
                                    "Бла-бла-бла")

        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

    def testConfigUserStyle(self):
        """
        Тест на то, что на кэширование влияет изменение пользовательских стилей
        """
        hashCalculator = WikiHashCalculator(self.application)
        hash_src = hashCalculator.getHash(self.testPage)

        self.__htmlconfig.userStyle.value = "p {background-color: maroon; /* Цвет фона под текстом параграфа */ color: white; /* Цвет текста */ }"

        hash2 = hashCalculator.getHash(self.testPage)
        self.assertNotEqual(hash2, hash_src)

    def testInvalidFontSize(self):
        """
        Тест на корректную обработку некорректных настроек размера шрифта
        """
        hashCalculator = WikiHashCalculator(self.application)
        hashCalculator.getHash(self.testPage)

        self.application.config.set(HtmlRenderConfig.HTML_SECTION,
                                    HtmlRenderConfig.FONT_SIZE_PARAM,
                                    "Бла-бла-бла")

        hashCalculator.getHash(self.testPage)

    def testInvalidFontBold(self):
        """
        Тест на корректную обработку некорректных настроек шрифта
        """
        hashCalculator = WikiHashCalculator(self.application)
        hashCalculator.getHash(self.testPage)

        self.application.config.set(HtmlRenderConfig.HTML_SECTION,
                                    HtmlRenderConfig.FONT_BOLD_PARAM,
                                    "Бла-бла-бла")

        hashCalculator.getHash(self.testPage)

    def testInvalidFontItalic(self):
        """
        Тест на корректную обработку некорректных настроек шрифта
        """
        hashCalculator = WikiHashCalculator(self.application)
        hashCalculator.getHash(self.testPage)

        self.application.config.set(HtmlRenderConfig.HTML_SECTION,
                                    HtmlRenderConfig.FONT_ITALIC_PARAM,
                                    "Бла-бла-бла")

        hashCalculator.getHash(self.testPage)
