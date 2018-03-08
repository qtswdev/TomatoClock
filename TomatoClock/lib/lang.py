# -*- coding:utf-8 -*-
#
# Copyright © 2016–2017 Liang Feng <finalion@gmail.com>
#
# Support: Report an issue at https://github.com/finalion/WordQuery/issues
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version; http://www.gnu.org/copyleft/gpl.html.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from anki.lang import currentLang

trans = {
    'TOMATO COLOCK': {'zh_CN': u'番茄时钟', 'en': u'Tomato Clock'},
    'IGNORE REST': {'zh_CN': u'跳过休息', 'en': u'Continue'},
    'REST': {'zh_CN': u"休息", 'en': u'Break'},
    'IGNORE REST QUESTION': {'zh_CN': u"跳过休息吗？", 'en': u'Ignore break and continue?'},
    'CANCEL': {'zh_CN': u"取消", 'en': u'Back'},
    '5 MINUTES': {'zh_CN': u"5分钟", 'en': u'5 Minutes'},
    '10 MINUTES': {'zh_CN': u"10分钟", 'en': u'10 Minutes'},
    '15 MINUTES': {'zh_CN': u"15分钟", 'en': u'15 Minutes'},
    '20 MINUTES': {'zh_CN': u"20分钟", 'en': u'20 Minutes'},
    '25 MINUTES': {'zh_CN': u"25分钟", 'en': u'25 Minutes'},
}

def _(key, lang=currentLang):
    key = key.upper().strip()
    if lang != 'zh_CN' and lang != 'en' and lang != 'fr':
        lang = 'en'  # fallback

    def disp(s):
        return s.lower().capitalize()

    if key not in trans or lang not in trans[key]:
        return disp(key)
    return trans[key][lang]


def _sl(key):
    return trans[key].values()
