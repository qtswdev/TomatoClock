# -*- coding: utf-8 -*-
# Created: 3/9/2018
# Project : TomatoClock
import json

from PyQt4.QtCore import Qt

import anki.lang
from ..lib.sounds import ABORT
from anki.lang import _
from anki.sound import play
from aqt import mw
from aqt.overview import Overview
from aqt.reviewer import Reviewer
from aqt.utils import askUser
from .constant import TIME_LIMIT
from .lang import _ as _2


class anki_overview(Overview):
    def __init__(self, tomato_dlg):
        super(anki_overview, self).__init__(mw)
        self.dlg = tomato_dlg

    def _linkHandler(self, url):
        if url == 'tomato_clock':
            # self.dlg.setWindowOpacity(0.9)
            self.dlg.btn_start.setText(anki.lang._("Study Now"))
            accepted = self.dlg.exec_()

            if accepted:
                url = "study"
        super(anki_overview, self)._linkHandler(url)

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


class anki_reviewer(Reviewer):

    def __init__(self, mode):
        super(anki_reviewer, self).__init__(mw)
        self.mode = mode

    def restore_layouts(self):
        mw.menuBar().show()
        mw.setWindowFlags(Qt.Window)
        mw.show()
        mw.activateWindow()
        mw.toolbar.web.show()

    def _showAnswerButton(self, ):
        if not self.mode:
            self._bottomReady = True
            if not self.typeCorrect:
                self.bottom.web.setFocus()
            middle = '''
    <span class=stattxt>%s</span><br>
    <button title="%s" id=ansbut onclick='py.link(\"ans\");'>%s</button>
    ''' % (
                self._remaining(), _("Shortcut key: %s") % _("Space"), _("Show Answer"))
            # wrap it in a table so it has the same top margin as the ease buttons
            middle = "<table cellpadding=0><tr><td class=stat2 align=center>%s</td></tr></table>" % middle

            self.bottom.web.eval("showQuestion(%s,%d);" % (
                json.dumps(middle), TIME_LIMIT))
        else:
            super(anki_reviewer, self)._showAnswerButton()

    def _answerCard(self, ease):
        super(anki_reviewer, self)._answerCard(ease)

    def _showAnswer(self):
        super(anki_reviewer, self)._showAnswer()
        if not self.mode:
            self.bottom.web.eval("stopTimer(%s);" % 0)

    def _linkHandler(self, url):
        if url == "decks":
            play(ABORT)
            if askUser(
                    _2("ABORT TOMATO"), mw
            ):
                mw.toolbar._linkHandler("decks")
        else:
            super(anki_reviewer, self)._linkHandler(url)

    def _bottomHTML(self):
        if not self.mode:
            mw.menuBar().hide()
            mw.toolbar.web.hide()
            mw.setWindowFlags(Qt.CustomizeWindowHint | Qt.Window)
            mw.show()
            mw.activateWindow()
            return """
            <style>
            body{font-family: 'Microsoft YaHei UI', serif;}
            .timer {font-family: 'Microsoft YaHei UI', serif;
                        color: #f0545e;font-weight: bold;font-size:15pt; 
                        padding-left: 5px; padding-right: 5px; white-space: nowrap; }
            </style>


            <table width=100%% cellspacing=0 cellpadding=0>
                <tr>

                <td align=left valign=center width = 20%%>
                    <table >
                    <tr>
                        <td width=50 align=center valign=center class=stat>
                            <input type=image value = "%(r)s" 
                                    onclick="py.link('decks');" 
                                    src="qrc:/icon/tomato.png" width=32 height=32 />
                        </td>
                        <td width=50 align=center valign=center class=stat>
                            %(timer)s
                        </td>
                    <tr>
                    </table>
                </td>

                <td align=center valign=top id=middle width = 60%%>

                </td>

                <td align=left valign=center width = 20%%>
                    <span></span>
                </td>

                </tr>
            </table>
            <script>
            var time = %(time)d;
            var maxTime = 0;
            $(function () {
            $("#ansbut").focus();
            updateTime();
            setInterval(function () { time += 1; updateTime() }, 1000);
            });

            var updateTime = function () {
                if (!maxTime) {
                    $("#time").text("");
                    return;
                }
                time = Math.min(maxTime, time);
                var m = Math.floor(time / 60);
                var s = time %% 60;
                if (s < 10) {
                    s = "0" + s;
                }
                var e = $("#time");
                if (maxTime == time) {
                    e.html("<font color=red>" + m + ":" + s + "</font>");
                } else {
                    e.text(m + ":" + s);
                }
            }

            function showQuestion(txt, maxTime_) {
              // much faster than jquery's .html()
              $("#middle")[0].innerHTML = txt;
              $("#ansbut").focus();
              time = 0;
              maxTime = maxTime_;
            }

            function showAnswer(txt) {
              $("#middle")[0].innerHTML = txt;
              $("#defease").focus();
            }

            function stopTimer(maxTime_){
                $("#time").text("");
                maxTime = maxTime_;
            }

            </script>
            """ % dict(r=_2("RETURN"),
                       timer="<span id=time class=timer></span>"
                       , rem=self._remaining(),
                       time=self.card.timeTaken() // 1000)
        return super(anki_reviewer, self)._bottomHTML()

    def _initWeb(self):
        super(anki_reviewer, self)._initWeb()

        # region ensure html  is shown ...

        self._showAnswerButton()

        # warning below is just an copy of _showQuestion function of anki2.0.48
        # to execute this because the reviewer and bottm html cannot be shown at the first time

        c = self.card
        # grab the question and play audio
        if c.isEmpty():
            q = _("""The front of this card is empty. Please run Tools>Empty Cards.""")
        else:
            q = c.q()
        # render & update bottom
        q = self._mungeQA(q)
        klass = "card card%d" % (c.ord + 1)
        self.web.eval("_updateQA(%s, false, '%s');" % (json.dumps(q), klass))

        # endregion
