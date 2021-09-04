#!/usr/bin/env python3
#############################################
# Password Saver by Rybkin Nikita Igorevich #
#############################################
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox

import py.start_window as start_window


class Interface(QtWidgets.QDialog, start_window.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    lock_file = None
    try:
        app = QtWidgets.QApplication(sys.argv)
        lock_file = QtCore.QLockFile("password_saver.lock")

        if lock_file.tryLock():
            window = Interface()
            window.show()

            sys.exit(app.exec_())
        else:
            icon_ps = QtGui.QIcon()
            icon_ps.addPixmap(
                QtGui.QPixmap(":/resource/image/key.ico"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
            msg_lock = QMessageBox()
            msg_lock.setWindowIcon(icon_ps)
            msg_lock.setIcon(QMessageBox.Warning)
            msg_lock.setWindowTitle("Ошибка")
            msg_lock.setText("Программа уже запущена.")
            msg_lock.setStandardButtons(QMessageBox.Ok)
            msg_lock.exec_()
    finally:
        lock_file.unlock()
