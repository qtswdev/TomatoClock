# coding=utf-8
import os
from urllib import urlretrieve

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QPushButton, QIcon, QLabel, QPixmap, QDialog, QVBoxLayout

from anki.lang import currentLang

_style = u"""
<style>

* {
    font-family: 'Microsoft YaHei UI', Consolas, serif;
}

</style>

"""

trans = {
    'WECHAT CHANNEL': {'zh_CN': u'微信公众号: Anki干货铺', 'en': u'WeChat Channel'},
    'CLICK CLOSE': {'zh_CN': u'点击关闭此窗口', 'en': u'Click to close'},
    'WECHART CHANNEL WELCOME': {'zh_CN': _style + u'<center>微信扫一扫关注“Anki干货铺”！QQ群：723233740</center>',
                                'en': _style + u'<center>Subscribe Anki365</center>'},
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


# region Dialogs
class QRDialog(QDialog):
    def __init__(self, parent, qr_file):
        super(QRDialog, self).__init__(parent)
        self.l = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        self.l.addWidget(self.image_label)
        self.l.addWidget(QLabel(_("WECHART CHANNEL WELCOME"), self))
        self.setToolTip(_("CLICK CLOSE"))
        self.set_qr(qr_file)

    def set_qr(self, qr_file):
        pix = QPixmap()
        pix.load(qr_file)
        self.image_label.setPixmap(pix)

    def mousePressEvent(self, evt):
        self.accept()


# endregion

class _ImageButton(QPushButton):
    def __init__(self, parent, icon_url):
        super(_ImageButton, self).__init__(parent)
        self.setIcon(QIcon(icon_url))
        self.set_size(30, 30)
        self.setText("")

    def set_size(self, width, height):
        self.setFixedSize(QSize(width, height))


class WeChatButton(_ImageButton):
    def __init__(self, parent):
        super(WeChatButton, self).__init__(parent, ":/icon/wechat.png")
        self.setObjectName("btn_wechat")
        self.setToolTip(_("WECHAT CHANNEL"))
        self.setWhatsThis(self.toolTip())
        self.clicked.connect(self.on_clicked)
        self._qr_file_nm = "_anki365qr.jpg"

    def ensure_qr(self):
        if not os.path.isfile(self._qr_file_nm):
            qr_url = "https://raw.githubusercontent.com/upday7/LiveCodeHub/master/WeChartQR.jpg"
            urlretrieve(qr_url, self._qr_file_nm)

    def on_clicked(self):
        self.ensure_qr()
        dlg = QRDialog(self, self._qr_file_nm)
        self.parent().hide()
        dlg.exec_()
        self.parent().show()
