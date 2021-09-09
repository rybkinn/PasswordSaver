#!/usr/bin/env python3
import os
from sys import platform

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import py.main_menu
import py.start_window
import py.ui.loading_db_ui as loading_db_ui
from py.show_msg import show_msg

if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X


class LoadingDB(QtWidgets.QDialog, loading_db_ui.Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.name_db = []
        data_files_name = os.listdir(path="data")
        self.name_db.clear()
        for name_db_ in data_files_name:
            type_file = name_db_[name_db_.find("."):]
            if type_file == '.db':
                self.name_db.append(name_db_)
        path_dir = os.getcwd()
        for name_db_item in self.name_db:
            db_data = [path_dir + '\\data\\' + name_db_item, name_db_item]
            self.comboBox.addItem(name_db_item, db_data)
        self.setWindowIcon(QtGui.QIcon(':/resource/image/key.ico'))
        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton.clicked.connect(self.show_main_window)

    @QtCore.pyqtSlot()
    def push_tool_button(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox.clear()
            filename = ''
            for letter in reversed(directory_name[0]):
                if letter == '/':
                    break
                filename += letter
            file_info = [filename[::-1], directory_name]
            db_data = [file_info[1][0], file_info[0]]
            self.comboBox.addItem(file_info[0], db_data)

    @QtCore.pyqtSlot()
    def show_main_window(self):
        pwd = self.lineEdit.text()
        wrong_db_info = self.comboBox.currentData()
        wrong_db_info_new = ''
        db_info = list()
        for item_db_info in range(len(wrong_db_info[0])):
            if wrong_db_info[0][item_db_info] == '\\':
                wrong_db_info_new += '/'
            else:
                wrong_db_info_new += wrong_db_info[0][item_db_info]
        db_info.append(wrong_db_info_new)
        db_info.append(wrong_db_info[1])

        conn_load = sqlite3.connect(db_info[0])
        cur_load = conn_load.cursor()
        cur_load.execute("PRAGMA key = '{}'".format(pwd))
        try:
            cur_load.execute("SELECT count(*) FROM account_information")
            cur_load.close()
            conn_load.close()
            result = bool(1)
        except sqlite3.DatabaseError:
            cur_load.close()
            conn_load.close()
            result = bool(0)
        if result:
            py.main_menu.cur.close()
            py.main_menu.conn.close()
            py.main_menu.db_dir = db_info[0]
            py.main_menu.db_name = db_info[1]
            py.main_menu.pwd = pwd
            del pwd
            py.main_menu.connect_sql()
            self.done(1)
        else:
            show_msg(title='Ошибка',
                     top_text='Неправильный пароль',
                     window_type='critical',
                     buttons='ok')
            self.lineEdit.clear()
