# -*- coding: utf-8 -*-
import perl

from outwiker.gui.baseaction import BaseAction
from outwiker.core.application import Application


class PerlAction (BaseAction):
    """
    выполнить перл-скрипт
    """
    stringId = u"PerlAction"

    def __init__(self, application):
        self._application = application

    @property
    def title(self):
        return _(u"perl")

    @property
    def description(self):
        return _(u"run perl")

    def run(self, params):
        perl.eval("""print $::cnt++,"\n" """)
        r = Application.wikiroot
        global p
        p = Application.selectedPage
        # 
        # Application.selectedPage (WikiWikiPage, outwiker.pages.wiki.wikipages)
        #  .path
        #  .subpath
        #  .content
        #  .contentFile
        #  .textContent
        #  .update()
