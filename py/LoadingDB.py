# -*- coding: utf-8 -*-
import os
from sys import platform
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import py.MainMenu
import py.StartWindow
import py.ui.LoadingDB_ui as LoadingDB_ui
if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

Close = True


class LoadingDB(QtWidgets.QDialog, LoadingDB_ui.Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.name_bd = []
        data_files_name = os.listdir(path="data")
        self.name_bd.clear()
        for _name_bd in data_files_name:
            type_file = _name_bd[_name_bd.find("."):]
            if type_file == '.db':
                self.name_bd.append(_name_bd)
        path_dir = os.getcwd()
        for _addItem in self.name_bd:
            db_data = [path_dir + '\\data\\' + _addItem, _addItem]
            self.comboBox.addItem("", db_data)
        for _indexItem, _addItem in enumerate(self.name_bd):
            self.comboBox.setItemText(_indexItem, str(_addItem))
        self.setWindowIcon(QtGui.QIcon('resource/image/key.ico'))
        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton.clicked.connect(self.show_main_window)

    @QtCore.pyqtSlot()
    def push_tool_button(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox.clear()
            filename = ''
            for _letter in reversed(directory_name[0]):
                if _letter == '/':
                    break
                filename += _letter
            file_info = [filename[::-1], directory_name]
            db_data = [file_info[1][0], file_info[0]]
            self.comboBox.addItem("", db_data)
            self.comboBox.setItemText(0, file_info[0])

    @QtCore.pyqtSlot()
    def show_main_window(self):
        pwd = self.lineEdit.text()
        wrong_db_info = self.comboBox.currentData()
        wrong_db_info_new = ''
        db_info = list()
        for _item_db_info in range(len(wrong_db_info[0])):
            if wrong_db_info[0][_item_db_info] == '\\':
                wrong_db_info_new += '/'
            else:
                wrong_db_info_new += wrong_db_info[0][_item_db_info]
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
            py.MainMenu.cur.close()
            py.MainMenu.conn.close()
            py.MainMenu.db_dir = db_info[0]
            py.MainMenu.db_name = db_info[1]
            py.MainMenu.pwd = pwd
            del pwd
            py.MainMenu.connect_sql(start_or_load='load')
            global Close
            Close = False
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Ошибка входа")
            msg.setText("Неправильный пароль")
            msg.exec_()
            self.lineEdit.clear()
