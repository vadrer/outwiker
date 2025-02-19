# -*- coding: utf-8 -*-

from outwiker.pages.wiki.parser.command import Command
from outwiker.pages.wiki.parser.htmlelements import create_link_to_page
import outwiker.core.cssclasses as css


class SimpleView:
    """
    Класс для простого представления списка дочерних страниц - каждая страница
    на отдельной строке
    """
    @staticmethod
    def make(title, children, parser, params) -> str:
        """
        children - список упорядоченных дочерних страниц
        """
        if not children:
            return ''

        links = [create_link_to_page('page://{}'.format(page.title),
                                     page.display_title)
                for page in children]
        items = [f'<li class="{css.CSS_ATTACH_LIST_ITEM}">{link}</li>'
                 for link in links]
        all_items_str = ''.join(items)
        result = f'<ul class="{css.CSS_CHILD_LIST}"><span class="{css.CSS_CHILD_LIST_TITLE}">{title}</span><ul class="{css.CSS_CHILD_LIST}">{all_items_str}</ul></ul>'

        return result


class ChildListCommand(Command):
    """
    Команда для вставки списка дочерних команд.
    Синтсаксис: (:childlist [params...]:)
    Параметры:
        sort=name - сортировка по имени
        sort=descendname - сортировка по имени в обратном порядке
        sort=descendorder - сортировка по положению страницы в обратном порядке
        sort=edit - сортировка по дате редактирования
        sort=descendedit - сортировка по дате редактирования в обратном порядке
        sort=creation - сортировка по дате создания
        sort=descendcreation - сортировка по дате создания в обратном порядке
    """

    def __init__(self, parser):
        Command.__init__(self, parser)

    @property
    def name(self):
        return "childlist"

    def execute(self, params, content):
        params_dict = Command.parseParams(params)

        children = self.parser.page.children
        title = self.parser.page.display_title
        self._sortChildren(children, params_dict)

        return SimpleView.make(title, children, self.parser, params)

    def _sortByNameKey(self, page):
        return page.display_title.lower()

    def _sortByEditDate(self, page):
        return page.datetime

    def _sortByCreationDate(self, page):
        return page.creationdatetime

    def _sortByOrder(self, page):
        return page.order

    def _sortChildren(self, children, params_dict):
        """
        Отсортировать дочерние страницы, если нужно
        """
        if "sort" not in params_dict:
            return

        sort = params_dict["sort"].lower()

        # Ключ - название сортировки,
        # значение - кортеж из (функция ключа сортировки, reverse)
        sortdict = {
            "name":             (self._sortByNameKey, False),
            "descendname":      (self._sortByNameKey, True),
            "order":            (self._sortByOrder, False),
            "descendorder":     (self._sortByOrder, True),
            "edit":             (self._sortByEditDate, False),
            "descendedit":      (self._sortByEditDate, True),
            "creation":         (self._sortByCreationDate, False),
            "descendcreation":  (self._sortByCreationDate, True),
        }

        if sort in sortdict:
            func, reverse = sortdict[sort]
            children.sort(key=func, reverse=reverse)
