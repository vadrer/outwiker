# coding: utf-8

import wx

from outwiker.api.gui.dialogs.messagebox import MessageBox
from outwiker.api.services.messages import showError
from outwiker.core.attachment import Attachment
from outwiker.gui.baseaction import BaseAction


class RemoveAttachesActionForAttachPanel(BaseAction):
    """
    Remove attached files.

    Hidden action.
    """
    stringId = "RemoveAttachesForAttachPanel"

    def __init__(self, application):
        self._application = application

    @property
    def title(self):
        return _("Remove attached files")

    @property
    def description(self):
        return _("Remove attached files. Action for attach panel")

    def run(self, params):
        attachPanel = self._application.mainWindow.attachPanel.panel

        if self._application.selectedPage is not None:
            files = attachPanel.getSelectedFiles()

            if len(files) == 0:
                showError(self._application.mainWindow,
                          _("You did not select any file to remove"))
                return

            files_str = '\n'.join(files)
            text = _("Remove selected files?") + '\n\n' + files_str

            if MessageBox(text,
                          _("Removing attachments"),
                          wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                try:
                    Attachment(
                        self._application.selectedPage).removeAttach(files)
                except IOError as e:
                    showError(self._application.mainWindow, str(e))

                attachPanel.updateAttachments()
