#!/usr/bin/env python3
#############################################
# Password Saver by Rybkin Nikita Igorevich #
#############################################
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import py.start_window as start_window
from py.show_msg import show_msg


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
            show_msg(title='Ошибка',
                     top_text='Программа уже запущена',
                     window_type='warning',
                     buttons='ok')
    finally:
        lock_file.unlock()
