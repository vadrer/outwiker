# -*- coding: utf-8 -*-
import perl
import re
import inspect
from pprint import pprint

from outwiker.gui.baseaction import BaseAction
from outwiker.core.application import Application
from outwiker.core.system import getCurrentDir


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
        cd = getCurrentDir()
        p = Application.selectedPage
        # get TextPageEditor, 
        #def SetCursorPosition(self, position):
        #def GetCursorPosition(self):
        #print(p.getTextEditor().GetCursorPosition)
        c0 = p.content
        c1 = perl.eval("""$s = <<'___EOS___';
""" + c0 + """
___EOS___
$s=~s/(<!--:(.*?)-->).*?(<!--\/-->)/my $r=$2;$1.eval("$r").$3/gesr;
""")
        if c0 != c1:
            p.content = c1
        #print $::cnt++, q("+p.path+" ; "+p.content+"),qq/\n/ """)
        r = Application.wikiroot
        # 
        # Application.selectedPage (WikiWikiPage, outwiker.pages.wiki.wikipages)
        #  .path
        #  .subpath
        #  .content
        #  .contentFile
        #  .textContent
        #  .update()

class PythonAction (BaseAction):
    """
    выполнить питон-скрипт
    """
    stringId = u"PythonAction"

    def __init__(self, application):
        self._application = application

    @property
    def title(self):
        return _(u"python")

    @property
    def description(self):
        return _(u"run python")

    def run(self, params):
        cd = getCurrentDir()
        p = Application.selectedPage
        # get TextPageEditor, 
        #def SetCursorPosition(self, position):
        #def GetCursorPosition(self):
        #print(p.getTextEditor().GetCursorPosition)
        c0 = p.content
        #print("eval py")
        # выделить подстроку ... и eval её
        m = re.search('^p> (.*?)^__',c0,re.M+re.S)
        if m is None:
            print("nope")
            return
        print(m.group(1))
        ret = eval(m.group(1))
        print("ret=",ret)

