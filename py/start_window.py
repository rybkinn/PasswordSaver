#!/usr/bin/env python3
import datetime
import os
from sys import platform

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import py.main_menu
import py.database_creation as database_creation
from py.show_msg import show_msg

if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X


def check_database(connect: sqlite3.Connection, pwd: str) -> tuple:
    """
    Validates the database and returns a tuple.

    :param connect: sqlite3.Connection object
    :param pwd: pragma key password
    :return: tuple(sqlite3.Connection, bool)
    """
    cur_check_db = connect.cursor()
    cur_check_db.execute(f"PRAGMA key = '{pwd}'")
    try:
        account_information = cur_check_db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND
        name='account_information'""").fetchall()
        data_change_time = cur_check_db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND
        name='data_change_time'""").fetchall()
        db_information = cur_check_db.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND
        name='db_information'""").fetchall()
        if len(data_change_time) == 0:
            cur_check_db.execute("""
            CREATE TABLE IF NOT EXISTS data_change_time(
                "id" INTEGER NOT NULL UNIQUE 
                    REFERENCES account_information (id) ON DELETE CASCADE 
                                                        ON UPDATE CASCADE,
                "create_account" TEXT NOT NULL,
                "update_account" TEXT DEFAULT 'NULL',
                "change_section" TEXT DEFAULT 'NULL',
                "change_login" TEXT DEFAULT 'NULL',
                "change_pass" TEXT DEFAULT 'NULL',
                "change_email" TEXT DEFAULT 'NULL',
                "change_secret_word" TEXT DEFAULT 'NULL',
                "change_url" TEXT DEFAULT 'NULL')""")
            if len(account_information) == 1:
                id_account_information = cur_check_db.execute("""
                SELECT id FROM account_information""").fetchall()
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for id_ in id_account_information:
                    cur_check_db.execute("""
                    INSERT INTO data_change_time (id, create_account) 
                    VALUES (?,?)""", (id_[0], now_time))
        if len(account_information) == 0:
            cur_check_db.execute("""
            CREATE TABLE IF NOT EXISTS account_information(
                "id" INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
                "section" TEXT NOT NULL,
                "name" TEXT NOT NULL,
                "login" TEXT NOT NULL,
                "pass" TEXT NOT NULL,
                "email" TEXT DEFAULT 'NULL',
                "secret_word" TEXT DEFAULT 'NULL',
                "url" TEXT DEFAULT 'NULL')""")
        if len(db_information) == 0:
            cur_check_db.execute("""
            CREATE TABLE IF NOT EXISTS db_information(
                "name" TEXT NOT NULL,
                "value" INTEGER NOT NULL)""")
            cur_check_db.execute("""
            INSERT INTO db_information (name, value) 
            VALUES (?, ?)""", ('rsa_bit', py.main_menu.NEW_RSA_BIT))
    except sqlite3.DatabaseError as error:
        show_msg(title='Ошибка',
                 top_text='Ошибка проверки базы данных',
                 bottom_text=str(error),
                 window_type='critical',
                 buttons='ok')
        cur_check_db.close()
        return connect, False
    cur_check_db.close()
    connect.commit()
    return connect, True


class Ui_Dialog(object):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.create_db = None
        self.names_db = []

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setMinimumSize(QtCore.QSize(400, 300))
        Dialog.setMaximumSize(QtCore.QSize(400, 300))
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(180, 40, 31, 16))
        self.label_5.setObjectName("label_5")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(350, 270, 47, 13))
        self.label_4.setObjectName("label_4")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(105, 10, 190, 30))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(70, 90, 251, 121))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_3 = QtWidgets.QPushButton(self.gridLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_3.setMaximumSize(QtCore.QSize(100, 25))
        self.pushButton_3.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton_3.setBaseSize(QtCore.QSize(0, 0))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 270, 101, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_3, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox_2.setCurrentText("")
        self.comboBox_2.setObjectName("comboBox_2")

        self.updates_list_db()

        self.gridLayout.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.toolButton = QtWidgets.QToolButton(self.gridLayoutWidget)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        Dialog.setWindowIcon(QtGui.QIcon(':/resource/image/key.ico'))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.pushButton_3, self.comboBox_2)
        Dialog.setTabOrder(self.comboBox_2, self.toolButton)
        Dialog.setTabOrder(self.toolButton, self.lineEdit_2)
        Dialog.setTabOrder(self.lineEdit_2, self.pushButton_2)

        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton_3.clicked.connect(self.show_main_window)
        self.pushButton_2.clicked.connect(self.show_create_db)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Password Saver - Вход"))
        self.label_5.setText(_translate("Dialog", "Вход"))
        self.pushButton_2.setText(_translate("Dialog", "Создать базу"))
        self.label_4.setText(_translate("Dialog", str(py.main_menu.VERSION)))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.pushButton_3.setText(_translate("Dialog", "Войти"))
        self.label_6.setText(_translate("Dialog", "Выберете базу"))
        self.label_7.setText(_translate("Dialog", "Введите пароль"))
        self.toolButton.setText(_translate("Dialog", "..."))

    def updates_list_db(self):
        self.names_db.clear()
        self.comboBox_2.clear()

        path_dir = os.getcwd()
        data_files_name = os.listdir(path="data")
        for file_name in data_files_name:
            type_file = file_name[file_name.find("."):]
            if type_file == '.db':
                self.names_db.append(file_name)
        for name_db in self.names_db:
            db_data = [path_dir + '\\data\\' + name_db, name_db]
            self.comboBox_2.addItem(name_db, db_data)

    @QtCore.pyqtSlot()
    def push_tool_button(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox_2.clear()
            filename = ''
            for letter in reversed(directory_name[0]):
                if letter == '/':
                    break
                filename += letter
            file_info = [filename[::-1], directory_name]
            db_data = [file_info[1][0], file_info[0]]
            self.comboBox_2.addItem(file_info[0], db_data)

    @QtCore.pyqtSlot()
    def show_main_window(self):
        if self.comboBox_2.currentIndex() == -1:
            show_msg(title='Ошибка',
                     top_text='Не выбрана база данных',
                     window_type='critical',
                     buttons='ok')
        else:
            pwd = self.lineEdit_2.text()
            wrong_db_info = self.comboBox_2.currentData()

            wrong_db_info_new = ''
            for _item_db_info in range(len(wrong_db_info[0])):
                if wrong_db_info[0][_item_db_info] == '\\':
                    wrong_db_info_new += '/'
                else:
                    wrong_db_info_new += wrong_db_info[0][_item_db_info]

            db_info = [wrong_db_info_new, wrong_db_info[1]]

            conn_start_window = sqlite3.connect(db_info[0])
            cur_start_window = conn_start_window.cursor()
            cur_start_window.execute("PRAGMA key = '{}'".format(pwd))
            try:
                cur_start_window.execute(
                    "SELECT count(*) FROM account_information")
                result = bool(1)
                cur_start_window.close()
            except sqlite3.DatabaseError:
                result = bool(0)
                cur_start_window.close()
                conn_start_window.close()
            if result:
                conn_start_window, check_result = check_database(
                    conn_start_window, pwd)
                conn_start_window.close()
                if check_result:
                    py.main_menu.db_dir = db_info[0]
                    py.main_menu.db_name = db_info[1]
                    py.main_menu.pwd = pwd
                    del pwd
                    py.main_menu.connect_sql()
                    self.main_window = MainWindow()
                    self.main_window.show()
                    self.close()
            else:
                show_msg(title='Ошибка',
                         top_text='Неправильный пароль',
                         window_type='critical',
                         buttons='ok')
                self.lineEdit_2.clear()

    @QtCore.pyqtSlot()
    def show_create_db(self):
        self.create_db = database_creation.CreateDB()
        self.create_db.exec_()
        self.updates_list_db()


class MainWindow(QtWidgets.QMainWindow, py.main_menu.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
