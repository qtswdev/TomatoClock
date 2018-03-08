# -*- coding: utf-8 -*-
# Created: 3/8/2018
# Project : OneClock
import re

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QListWidgetItem, QDialog

from ._OneClock import Ui_TomatoClockDlg
from ..lib.lang import _


class OneClock(QDialog, Ui_TomatoClockDlg):

    def __init__(self, parent):
        super(OneClock, self).__init__(parent)
        self.setupUi(self)
        self._adjust_ui()

    @property
    def _min_items(self):
        """

        :rtype: list of QListWidgetItem
        """
        return self.list_mis.findItems('\d.+', Qt.MatchRegExp)

    @property
    def min_item(self):
        return [i for i in self._min_items if i.isSelected()][0]

    @property
    def min(self):
        """

        :rtype: int
        """
        return int(re.match("\d+", self.min_item.text()).group())

    def _adjust_ui(self):
        self._adjust_min_list()
        self._adjust_dialog()

    def _adjust_dialog(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(_("TOMATO CLOCK"))

        self.btn_cancel.setText(_(self.btn_cancel.text()))
        list(
            map(
                lambda item:item.setText(_(item.text())),self._min_items
            )
        )

    def _adjust_min_list(self):
        # adjust item alignment
        list(map(
            lambda item: item.setTextAlignment(Qt.AlignCenter), self._min_items
        ))
        # set default item
        self._min_items[2].setSelected(True)
