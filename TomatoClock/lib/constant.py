# -*- coding: utf-8 -*-
# Created: 3/9/2018
# Project : TomatoClock
from anki.lang import currentLang

ADDON_CD = 1608644302
HAS_SET_UP = False
MIN_SECS = 60
__version__ = "0.1.7"

REST_MINS = 5
DEBUG = False

UPDATE_LOGS = (
    (
        "0.1.5", u"""
        <ol>
            <li>新增： 静音选项，详细见设置 > PlaySounds</li>
            <li>新增： 插件投票选项（窗口右上角） </li>
            <li>修复： 若干BUG</li>
            </ol>
        """ if currentLang == 'zh_CN' else """
        <ol>
            <li>Added: Mute for sounds, see in settings > PlaySounds </li>
            <li>Added: "Vote for Addon" button, at the top right corner of window </li>
            <li>Fixed: several bugs</li>
            </ol>"""
    ),
    (
        "0.1.6", u"""
        <ol>
            <li>新增： 番茄图表! (在设置中可以关闭)</li>
            </ol>
        """ if currentLang == 'zh_CN' else """
        <ol>
            <li>Added: Statics! (Switch off in settings) </li>
            </ol>"""
    ),
    (
        "0.1.7", u"""
        <ol>
            <li>修复： 番茄图表若干BUG</li>
            <li>新增： 动态加载代码（设置里关闭）</li>
            </ol>
        """ if currentLang == 'zh_CN' else """
        <ol>
            <li>Fixed: Reports bugs </li>
            <li>Added: Dynamically loading codes from github(Switch off in settings) </li>
            </ol>"""
    ),
)
