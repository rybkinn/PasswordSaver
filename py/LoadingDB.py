# -*- coding: utf-8 -*-

import os
from sys import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import py.MainMenu
import py.StartWindow
if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

name_bd = []


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        path_dir = os.getcwd()
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(400, 300))
        Dialog.setMaximumSize(QtCore.QSize(400, 300))
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(30, 10, 30, 50)
        self.gridLayout.setHorizontalSpacing(30)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_3.setMaximumSize(QtCore.QSize(173, 25))
        self.pushButton_3.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton_3.setBaseSize(QtCore.QSize(0, 0))
        self.pushButton_3.setStyleSheet("margin-right: 50px;")
        self.pushButton_3.setAutoDefault(False)
        self.pushButton_3.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton_3, 5, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setStyleSheet("padding-bottom: 70px;")
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 3)
        self.comboBox_2 = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setCurrentText("")
        self.comboBox_2.setInsertPolicy(QtWidgets.QComboBox.InsertAtBottom)
        self.comboBox_2.setObjectName("comboBox")
        global name_bd
        data_files_name = os.listdir(path="data")
        name_bd.clear()
        for _name_bd in data_files_name:
            type_file = _name_bd[_name_bd.find("."):]
            if type_file == '.db':
                name_bd.append(_name_bd)
        for _addItem in name_bd:
            db_data = [path_dir + '\\data\\' + _addItem, _addItem]
            exec('self.comboBox_2.addItem("", db_data)')
        self.gridLayout.addWidget(self.comboBox_2, 3, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit_2, 4, 1, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.toolButton = QtWidgets.QToolButton(Dialog)
        self.toolButton.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 3, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.pushButton_3, self.comboBox_2)
        Dialog.setTabOrder(self.comboBox_2, self.toolButton)
        Dialog.setTabOrder(self.toolButton, self.lineEdit_2)

        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton_3.clicked.connect(self.show_mainwindow)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Загрузка базы данных"))
        self.label_3.setText(_translate("Dialog", "Выберете базу"))
        self.pushButton_3.setText(_translate("Dialog", "Войти"))
        self.label_2.setText(_translate("Dialog", "Загрузка базы данных"))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.label_4.setText(_translate("Dialog", "Введите пароль"))
        _indexItem = 0
        for _addItem in name_bd:
            exec('self.comboBox_2.setItemText(%d, _translate("Dialog", "%s"))' % (_indexItem, _addItem))
            _indexItem += 1
        self.toolButton.setText(_translate("Dialog", "..."))

    @QtCore.pyqtSlot()
    def push_tool_button(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox_2.clear()
            filename = ''
            for _letter in reversed(directory_name[0]):
                if _letter == '/':
                    break
                filename += _letter
            file_info = [filename[::-1], directory_name]
            db_data = [file_info[1][0], file_info[0]]
            self.comboBox_2.addItem("", db_data)
            self.comboBox_2.setItemText(0, file_info[0])

    @QtCore.pyqtSlot()
    def show_mainwindow(self):
        global pwd
        global db_info
        pwd = self.lineEdit_2.text()
        wrong_db_info = self.comboBox_2.currentData()
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
            py.MainMenu.Ui_MainWindow.connect_sql(self, True, start_or_load='load')
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Ошибка входа")
            msg.setText("Неправильный пароль")
            msg.exec_()
