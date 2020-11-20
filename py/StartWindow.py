# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import os
import py.MainMenu
import py.DatabaseCreation


class Ui_Dialog(object):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        self.setupUi(self)

        self.mainwindow = mainwindow()
        self.createdb = createdb()

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
        self.comboBox_2.setCurrentText("")
        self.comboBox_2.setObjectName("comboBox_2")
        global new_name_bd
        new_name_bd = []
        for _name_bd in data_files:
            type_file = _name_bd[_name_bd.find("."):]
            if type_file == '.db':
                new_name_bd.append(_name_bd)
        for _addItem in new_name_bd:
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

        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton_3.clicked.connect(self.show_mainwindow)
        self.pushButton_2.clicked.connect(self.show_createdb)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Password Saver - Вход"))
        self.label_5.setText(_translate("Dialog", "Вход"))
        self.pushButton_2.setText(_translate("Dialog", "Создать базу"))
        self.label_4.setText(_translate("Dialog", "v 0.2"))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.pushButton_3.setText(_translate("Dialog", "Войти"))
        self.label_6.setText(_translate("Dialog", "Выберете базу"))
        self.label_7.setText(_translate("Dialog", "Введите пароль"))
        _indexItem = 0
        for _addItem in new_name_bd:
            exec('self.comboBox_2.setItemText(%d, _translate("Dialog", "%s"))' % (_indexItem, _addItem))
            _indexItem += 1
        self.toolButton.setText(_translate("Dialog", "..."))

    @QtCore.pyqtSlot()
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
            file_info = [filename[::-1], directory_name]
            self.comboBox_2.addItem("")
            self.comboBox_2.setItemText(0, file_info[0])

    @QtCore.pyqtSlot()
    def show_mainwindow(self):
        iw = bool(1)
        if iw:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Оповещение")
            msg.setText("Успешный вход")
            msg.exec_()
            self.mainwindow.show()
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Ошибка входа")
            msg.setText("Неправильный пароль")
            msg.exec_()

    @QtCore.pyqtSlot()
    def show_createdb(self):
        # self.hide()
        self.createdb.show()


class mainwindow(QtWidgets.QMainWindow, py.MainMenu.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class createdb(QtWidgets.QDialog, py.DatabaseCreation.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
