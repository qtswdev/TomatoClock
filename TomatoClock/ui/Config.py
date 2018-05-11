from PyQt4.QtGui import QDialog

from ._Config import Ui_dlg_config


class ConfigDialog(QDialog, Ui_dlg_config):
    def __init__(self, parent):
        super(ConfigDialog, self).__init__(parent)
        self.setupUi(self)
