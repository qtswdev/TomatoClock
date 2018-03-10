# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QDockWidget, QWidget, QIcon

from anki.sound import play
from aqt import mw
from aqt.main import AnkiQt
from .lib.component import anki_overview, anki_reviewer
from .lib.config import ProfileConfig
from .lib.constant import MIN_SECS
from .lib.sounds import BREAK
from .ui.BreakDialog import RestDialog
from .ui.OneClock import OneClock
from .ui.ProgressBar import ClockProgress


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
        self.pb_w = None

        self.replace_mw_overview()
        self.replace_mw_reviewer()

    def replace_mw_overview(self):
        mw.overview = anki_overview(self.dlg)

    def replace_mw_reviewer(self):
        mw.reviewer = anki_reviewer(self.dlg.mode)

    @staticmethod
    def _set_style_sheet(obj):
        with open(os.path.join(os.path.dirname(__file__), "ui", "designer", "style.css"), "r") as f:
            obj.setStyleSheet(f.read())

    def _connect_slots(self):
        self.dlg.btn_start.clicked.connect(self.on_btn_start_clicked)

    def perform_hooks(self, func):
        func('reviewCleanup', self.on_review_cleanup)
        func('profileLoaded', self.on_profile_loaded)

    def on_profile_loaded(self):
        ProfileConfig.donate_alerted = False

    def on_review_cleanup(self):
        mw.setWindowIcon(QIcon(":/icons/anki.png"))
        if self.tm and self.tm.isActive():
            self.tm.stop()
        if self.pb:
            self.pb_w.hide()
            self.pb.reset()

        if self.dlg_rest:
            self.dlg_rest.hide()

        mw.reviewer.restore_layouts()

    def on_btn_start_clicked(self):
        self.replace_mw_reviewer()
        mw.setWindowIcon(QIcon(":/icon/tomato.png"))
        assert isinstance(mw, AnkiQt)

        self.setup_progressbar()
        self.pb.set_seconds(self.dlg.min * MIN_SECS)
        if not self.tm:
            self.tm = Timer(mw)
            self.tm.timeout.connect(self.on_timer)
        self.tm.start()

        # click study button
        mw.overview._linkHandler("study")

    def on_tomato(self):
        self.tm.stop()
        self.pb_w.hide()
        self.pb.reset()
        mw.moveToState("overview")
        if not self.dlg_rest:
            self.dlg_rest = RestDialog(mw)
            self._set_style_sheet(self.dlg_rest)
            self.dlg_rest.accepted.connect(self.on_dlg_rest_accepted)
            self.dlg_rest.rejected.connect(self.on_dlg_rest_rejected)
        play(BREAK)
        self.dlg_rest.exec_(self.dlg.min)

    @staticmethod
    def on_dlg_rest_accepted():
        mw.overview._linkHandler("tomato_clock")

    def on_dlg_rest_rejected(self):
        pass

    def on_timer(self):
        if self.pb:
            self.pb_w.show()
            self.pb.on_timer()

    def setup_progressbar(self):

        dockArea = Qt.TopDockWidgetArea
        # dockArea = Qt.LeftDockWidgetArea
        # dockArea = Qt.BottomDockWidgetArea

        self.pb_w = QDockWidget(mw)
        self.pb_w.setObjectName("progress_dock")
        if not self.pb:
            self.pb = ClockProgress(mw, dockArea)
            self.pb.tomato.connect(self.on_tomato)
        else:
            self.pb.reset()

        self.pb.set_seconds(self.dlg.min * MIN_SECS)
        self.pb_w.setWidget(self.pb)
        w = QWidget(self.pb_w)
        w.setFixedHeight(self.pb.height())
        self.pb_w.setTitleBarWidget(w)
        self.pb_w.setFeatures(QDockWidget.NoDockWidgetFeatures)

        ## Note: if there is another widget already in this dock position, we have to add ourself to the list

        # first check existing widgets
        existing_widgets = [widget for widget in mw.findChildren(QDockWidget) if mw.dockWidgetArea(widget) == dockArea]

        # then add ourselves
        mw.addDockWidget(dockArea, self.pb_w)

        # stack with any existing widgets
        if len(existing_widgets) > 0:
            mw.setDockNestingEnabled(True)

            if dockArea == Qt.TopDockWidgetArea or dockArea == Qt.BottomDockWidgetArea:
                stack_method = Qt.Vertical
            if dockArea == Qt.LeftDockWidgetArea or dockArea == Qt.RightDockWidgetArea:
                stack_method = Qt.Horizontal
            mw.splitDockWidget(existing_widgets[0], self.pb_w, stack_method)

        mw.web.setFocus()
        self._set_style_sheet(self.pb)
