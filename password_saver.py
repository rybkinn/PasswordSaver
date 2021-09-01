#!/usr/bin/env python3
#############################################
# Password Saver by Rybkin Nikita Igorevich #
#############################################
import sys

from PyQt5 import QtWidgets

import py.start_window as start_window


class Interface(QtWidgets.QDialog, start_window.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Interface()
    window.show()
    sys.exit(app.exec_())
