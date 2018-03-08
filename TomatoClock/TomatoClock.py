# -*- coding: utf-8 -*-
# Created: 3/1/2018
# Project : OneClock
import os

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QDockWidget, QWidget

import anki.lang
from aqt import mw
from aqt.main import AnkiQt
from aqt.overview import Overview
from .ui.ClockProgress import ClockProgress
from .ui.ProgressCircle import RestDialog

HAS_SET_UP = False

from .ui.OneClock import OneClock

assert isinstance(mw, AnkiQt)


class overview(Overview):
    def __init__(self, tomato_dlg):
        super(overview, self).__init__(mw)
        self.dlg = tomato_dlg

    def _linkHandler(self, url):
        if url == 'tomato_clock':
            # self.dlg.setWindowOpacity(0.9)
            self.dlg.btn_start.setText(anki.lang._("Study Now"))
            accepted = self.dlg.exec_()

            if accepted:
                url = "study"
        super(overview, self)._linkHandler(url)

    def _table(self):
        counts = list(self.mw.col.sched.counts())
        finished = not sum(counts)
        for n in range(len(counts)):
            if counts[n] >= 1000:
                counts[n] = "1000+"
        but = self.mw.button
        if finished:
            return '<div style="white-space: pre-wrap;">%s</div>' % (
                self.mw.col.sched.finishedMsg())
        else:
            return '''
<table width=300 cellpadding=5>
<tr><td align=center valign=top>
<table cellspacing=5>
<tr><td>%s:</td><td><b><font color=#00a>%s</font></b></td></tr>
<tr><td>%s:</td><td><b><font color=#C35617>%s</font></b></td></tr>
<tr><td>%s:</td><td><b><font color=#0a0>%s</font></b></td></tr>
</table>
</td><td align=center>
%s</td></table>''' % (
                anki.lang._("New"), counts[0],
                anki.lang._("Learning"), counts[1],
                anki.lang._("To Review"), counts[2],
                but("tomato_clock", anki.lang._("Study Now"), id="study"),
            )


class Timer(QTimer):
    def __init__(self, parent):
        super(Timer, self).__init__(parent)
        self.setInterval(1000)


class OneClockAddon:

    def __init__(self):
        self.dlg = OneClock(mw)
        self.pb = None
        self._connect_slots()
        self._set_style_sheet(mw)
        self.tm = None
        self.dlg_rest = None

        self.setup_overview()

    def setup_overview(self):
        mw.overview = overview(self.dlg)

    def _set_style_sheet(self, obj):
        with open(os.path.join(os.path.dirname(__file__), "ui\designer\style.css"), "r") as f:
            obj.setStyleSheet(f.read())

    def _connect_slots(self):
        self.dlg.btn_start.clicked.connect(self.on_btn_start_clicked)

    def perform_hooks(self, func):
        func('reviewCleanup', self.on_reviewCleanup)

    def on_reviewCleanup(self):
        if self.tm and self.tm.isActive():
            self.tm.stop()
        if self.pb:
            self.pb.hide()
            self.pb.reset()

        if self.dlg_rest:
            self.dlg_rest.hide()

    def on_btn_start_clicked(self):
        assert isinstance(mw, AnkiQt)

        self.setup_progressbar()
        self.pb.set_seconds(self.dlg.min * 60)
        if not self.tm:
            self.tm = Timer(mw)
            self.tm.timeout.connect(self.on_timer)
        self.tm.start()

        # click study button
        mw.overview._linkHandler("study")

    def on_tomato(self):
        self.tm.stop()
        self.pb.hide()
        self.pb.reset()
        mw.moveToState("overview")
        if not self.dlg_rest:
            self.dlg_rest = RestDialog(mw)
            self._set_style_sheet(self.dlg_rest)
            self.dlg_rest.accepted.connect(self.on_dlg_rest_accepted)
            self.dlg_rest.rejected.connect(self.on_dlg_rest_rejected)
        self.dlg_rest.exec_()

    def on_dlg_rest_accepted(self):
        mw.overview._linkHandler("tomato_clock")

    def on_dlg_rest_rejected(self):
        pass

    def on_timer(self):
        if self.pb:
            self.pb.show()
            self.pb.on_timer()

    def setup_progressbar(self):

        dockArea = Qt.TopDockWidgetArea
        # dockArea = Qt.LeftDockWidgetArea
        # dockArea = Qt.BottomDockWidgetArea

        dock = QDockWidget()
        dock.setObjectName("progress_dock")
        if not self.pb:
            self.pb = ClockProgress(mw, dockArea)
            self.pb.tomato.connect(self.on_tomato)
        else:
            self.pb.reset()

        self.pb.set_seconds(self.dlg.min * 60)  # todo
        dock.setWidget(self.pb)
        dock.setTitleBarWidget(QWidget())

        ## Note: if there is another widget already in this dock position, we have to add ourself to the list

        # first check existing widgets
        existing_widgets = [widget for widget in mw.findChildren(QDockWidget) if mw.dockWidgetArea(widget) == dockArea]

        # then add ourselves
        mw.addDockWidget(dockArea, dock)

        # stack with any existing widgets
        if len(existing_widgets) > 0:
            mw.setDockNestingEnabled(True)

            if dockArea == Qt.TopDockWidgetArea or dockArea == Qt.BottomDockWidgetArea:
                stack_method = Qt.Vertical
            if dockArea == Qt.LeftDockWidgetArea or dockArea == Qt.RightDockWidgetArea:
                stack_method = Qt.Horizontal
            mw.splitDockWidget(existing_widgets[0], dock, stack_method)

        mw.web.setFocus()
        self._set_style_sheet(self.pb)
