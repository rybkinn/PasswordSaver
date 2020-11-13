#!/usr/bin/python3
# Password Saver by Rybkin Nikita Igorevich
# -*- coding: utf-8 -*-
# v 0.1

from PyQt5 import QtCore, QtGui, QtWidgets
import os, sqlite3
from py import DatabaseCreation

class Ui_Dialog(object):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        self.setupUi(Dialog)
        self.DatabaseCreation = _DatabaseCreation()

    def setupUi(self, Dialog):
        global data_files
        data_files = os.listdir(path="data")
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setMinimumSize(QtCore.QSize(400, 300))
        Dialog.setMaximumSize(QtCore.QSize(400, 300))
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(180, 40, 31, 16))
        self.label_5.setObjectName("label_5")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 270, 101, 23))
        self.pushButton_2.setObjectName("pushButton_2")
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
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_3.setMaximumSize(QtCore.QSize(100, 25))
        self.pushButton_3.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton_3.setBaseSize(QtCore.QSize(0, 0))
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox_2.setObjectName("comboBox_2")
        for _addItem in data_files:
            exec('self.comboBox_2.addItem("")')
        self.gridLayout.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.toolButton = QtWidgets.QToolButton(self.gridLayoutWidget)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.pushButton_2.clicked.connect(self.create_new_db)
        self.pushButton_3.clicked.connect(self.enter)
        self.toolButton.clicked.connect(self.push_tool_button)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Password Saver - Вход"))
        self.label_5.setText(_translate("Dialog", "Вход"))
        self.pushButton_2.setText(_translate("Dialog", "Создать базу"))
        self.label_4.setText(_translate("Dialog", "v 0.1"))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.pushButton_3.setText(_translate("Dialog", "Войти"))
        self.label_6.setText(_translate("Dialog", "Выберете базу"))
        self.label_7.setText(_translate("Dialog", "Введите пароль"))
        if 'file_info' in globals():
            self.comboBox_2.setItemText(0, _translate("Dialog", filename[::-1]))
        else:
            _indexItem = 0
            for _addItem in data_files:
                exec('self.comboBox_2.setItemText(%d, _translate("Dialog", "%s"))' % (_indexItem, _addItem))
                _indexItem += 1
        self.toolButton.setText(_translate("Dialog", "..."))

    def enter(self):
        password = self.lineEdit_2.text()
        print('password - ' + password)

    def push_tool_button(self):
        global directory_name
        global filename
        global file_info
        directory_name = QtWidgets.QFileDialog.getOpenFileName(None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox_2.clear()
            filename = ''
            for _letter in reversed(directory_name[0]):
                if _letter == '/':
                    break
                filename += _letter
            file_info = []
            file_info.append(filename[::-1])
            file_info.append(directory_name)
            self.comboBox_2.addItem("")
            self.retranslateUi(Dialog)

    def create_new_db(self):
        self.DatabaseCreation.show()


class _DatabaseCreation(QtWidgets.QDialog, DatabaseCreation.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())