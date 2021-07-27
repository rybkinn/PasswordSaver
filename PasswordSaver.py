# Password Saver by Rybkin Nikita Igorevich
# -*- coding: utf-8 -*-
# v 1.4

import sys
from PyQt5 import QtWidgets
import py.StartWindow


class Interface(QtWidgets.QDialog, py.StartWindow.Ui_Dialog):
    def __init__(self):
        super(Interface, self).__init__()
        self.setupUi(self)

    def InitUI(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec_())
