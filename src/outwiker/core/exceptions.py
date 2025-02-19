# -*- coding: utf-8 -*-


class OutWikerException(Exception):
    """
    Базовый класс для исключений, специфических для OutWiker
    """


class TreeException(OutWikerException):
    """
    Исключение бросается при ошибке, возникающей при построении дерева
    """

    def __init__(self):
        OutWikerException.__init__(self)


class RootFormatError(TreeException):
    """
    Исключение бросается при ошибке чтения файла __page.opt корня вики
    """

    def __init__(self):
        TreeException.__init__(self)


class ClearConfigError(TreeException):
    """
    Исключение бросается, когда не удается сбросить файл __page.opt
    """

    def __init__(self):
        TreeException.__init__(self)


class DuplicateTitle(TreeException):
    """
    Исключение бросается при попытке создать страницу с именем,
    которое уже есть в текущей директории
    """

    def __init__(self):
        TreeException.__init__(self)


class ReadonlyException(OutWikerException):
    """
    Исключение бросается при попытке изменить страницу,
    открытую в режиме "только для чтения"
    """

    def __init__(self):
        OutWikerException.__init__(self)


class PreferencesException(OutWikerException):
    """
    Исключение связано с ошибками в настройках
    """

    def __init__(self):
        OutWikerException.__init__(self)


class InvalidImageFormat(OutWikerException):
    """
    An exception is thrown when the image format is incorrect
    """

    def __init__(self, filename):
        self.filename = filename
