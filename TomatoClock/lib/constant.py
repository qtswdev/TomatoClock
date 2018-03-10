# -*- coding: utf-8 -*-
# Created: 3/9/2018
# Project : TomatoClock
from anki.lang import currentLang

HAS_SET_UP = False
MIN_SECS = 60
__version__ = "0.1.3"

REST_MINS = 5

UPDATE_LOGS = (
    (
        "0.1.3", u"""
        <ol>
            <li>新增： 设置窗口，现在可以自定义卡片倒计时和休息时间了。</li>
            <li>新增： 若干音效 </li>
            <li>修复： 第一张卡片发音一直重复的问题</li>
            </ol>
        """ if currentLang =='zh_CN' else """
        <ol>
            <li>Added: Setting dialog, you can now change the minutes of card count down seconds and the rest/break minutes </li>
            <li>Added: Sounds effects </li>
            <li>Fixed: Lopping sound of cards on the first shown of question</li>
            </ol>"""
    ),
)
