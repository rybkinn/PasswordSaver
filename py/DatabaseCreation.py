# -*- coding: utf-8 -*-

import os
import string
from sys import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import rsa
import py.MainMenu
if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

validate_password = None


def show_msg(value, text_show):
    if value:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text_show)
        msg.setWindowTitle("Сообщение")
        msg.exec()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text_show)
        msg.setWindowTitle("Ошибка")
        msg.exec()


class Ui_Dialog(object):
    def __init__(self):
        super().__init__()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setMinimumSize(QtCore.QSize(400, 300))
        Dialog.setMaximumSize(QtCore.QSize(400, 300))
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(140, 50, 121, 16))
        self.label_5.setObjectName("label_5")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(115, 20, 190, 30))
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
        self.formLayoutWidget = QtWidgets.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(70, 120, 251, 103))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")

        # self.lineEdit.setPlaceholderText('Введите название БД')

        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_2.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.lineEdit_2.setAutoFillBackground(False)
        self.lineEdit_2.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.label_6 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.pushButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.pushButton.setMaximumSize(QtCore.QSize(100, 25))
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pushButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.pushButton.clicked.connect(self.create_database)
        self.lineEdit.textChanged.connect(self.valid_namedb)
        self.lineEdit_2.textChanged.connect(self.valid_passwd)
        self.lineEdit_3.textChanged.connect(self.confirm_passwd)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Password Saver - Создание базы данных"))
        self.label_5.setText(_translate("Dialog", "Создание базы данных"))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.label_2.setText(_translate("Dialog", "Введите название"))
        self.label_3.setText(_translate("Dialog", "Введите пароль"))
        self.label_6.setText(_translate("Dialog", "Подтвердите пароль"))
        self.pushButton.setText(_translate("Dialog", "Создать"))

    @QtCore.pyqtSlot()
    def valid_namedb(self):
        data_files = os.listdir(path="data")
        name_db = self.lineEdit.text()
        new_name_bd = []
        for _name_bd in data_files:
            type_file = _name_bd[_name_bd.find("."):]
            if type_file == '.db':
                new_name_bd.append(_name_bd[:-3])
        for _name_bd_new in new_name_bd:
            if name_db == _name_bd_new:
                self.lineEdit.setStyleSheet("border: 1px solid red")
                break
            else:
                self.lineEdit.setStyleSheet("border: 1px solid green")
        if name_db == '':
            self.lineEdit.setStyleSheet("border: 1px solid red")

    @QtCore.pyqtSlot()
    def valid_passwd(self):
        global validate_password
        password = self.lineEdit_2.text()
        confirm_pass = self.lineEdit_3.text()
        if self.isvalid_pass(password):
            self.lineEdit_2.setStyleSheet("border: 1px solid green")
            validate_password = True
        else:
            self.lineEdit_2.setStyleSheet("border: 1px solid red")
            validate_password = False
        if confirm_pass == '':
            pass
        elif confirm_pass == password:
            self.lineEdit_3.setStyleSheet("border: 1px solid green")
        else:
            self.lineEdit_3.setStyleSheet("border: 1px solid red")

    @QtCore.pyqtSlot()
    def confirm_passwd(self):
        password = self.lineEdit_2.text()
        confirm_pass = self.lineEdit_3.text()
        if confirm_pass == password:
            self.lineEdit_3.setStyleSheet("border: 1px solid green")
        else:
            self.lineEdit_3.setStyleSheet("border: 1px solid red")

    @QtCore.pyqtSlot()
    def create_database(self):
        global validate_password
        data_files = os.listdir(path="data")
        name_db = self.lineEdit.text()
        pwd = self.lineEdit_2.text()
        pwd_re = self.lineEdit_3.text()
        if name_db != '':
            result = False
            new_name_bd = []
            for _name_bd in data_files:
                type_file = _name_bd[_name_bd.find("."):]
                if type_file == '.db':
                    new_name_bd.append(_name_bd[:-3])
            for _name_bd_new in new_name_bd:
                if name_db == _name_bd_new:
                    result = True
                    break
            if result:
                show_msg(0, 'Такая база данных уже существует')
                self.lineEdit.setStyleSheet("border: 1px solid red")
            elif pwd == '' and pwd_re == '':
                show_msg(0, 'Заполните поля ввода паролей')
                self.lineEdit_2.setStyleSheet("border: 1px solid red")
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
            elif pwd == '':
                show_msg(0, 'Поле введите пароль пустое')
                self.lineEdit_2.setStyleSheet("border: 1px solid red")
            elif validate_password is None or not validate_password:
                show_msg(0, 'Пароль должен быть больше 8 символов, верхний, нижний регистр и минимум 1 буква')
                self.lineEdit_2.setStyleSheet("border: 1px solid red")
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
            elif pwd_re == '':
                show_msg(0, 'Поле Подтвердите пароль пустое')
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
            elif pwd == pwd_re:
                conn = sqlite3.connect(r'data/' + name_db + '.db')
                cur = conn.cursor()
                cur.execute("PRAGMA key = '{}'".format(pwd))
                cur.execute("""CREATE TABLE IF NOT EXISTS account_information(
                    "ID" INTEGER NOT NULL UNIQUE,
                    "section" TEXT,
                    "name" TEXT,
                    "login" TEXT NOT NULL,
                    "pass" TEXT NOT NULL,
                    "email" TEXT,
                    "secret_word" TEXT,
                    "url" TEXT,
                    PRIMARY KEY("ID" AUTOINCREMENT))
                """)
                cur.execute("""CREATE TABLE IF NOT EXISTS db_information(
                    "name" TEXT,
                    "value" INTEGER)
                """)
                cur.execute("INSERT INTO db_information (name, value) VALUES ('rsa_bit', {})".format(py.MainMenu.new_rsa_bit))
                conn.commit()
                cur.close()
                conn.close()
                (pubkey, privkey) = rsa.newkeys(py.MainMenu.new_rsa_bit)
                pubkey_pem = pubkey.save_pkcs1('PEM')
                privkey_pem = privkey.save_pkcs1('PEM')
                with open('data/{0}_pubkey.pem'.format(name_db), mode='w+') as pubfile:
                    pubfile.write(pubkey_pem.decode())
                    pubfile.close()
                with open('data/{0}_privkey.pem'.format(name_db), mode='w+') as privatefile:
                    privatefile.write(privkey_pem.decode())
                    privatefile.close()

                self.lineEdit.clear()
                self.lineEdit_2.clear()
                self.lineEdit_3.clear()
                self.lineEdit.setStyleSheet("border: 1px solid gray")
                self.lineEdit_2.setStyleSheet("border: 1px solid gray")
                self.lineEdit_3.setStyleSheet("border: 1px solid gray")
                self.close()
                show_msg(1, 'База данных успешно созданна')
            else:
                show_msg(0, 'Пароли не совпадают')
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
        else:
            show_msg(0, 'Введите название БД')
            self.lineEdit.setStyleSheet("border: 1px solid red")

    def isvalid_pass(self, password):
        has_no = set(password).isdisjoint
        return not (len(password) < 8 or has_no(string.digits) or has_no(string.ascii_lowercase) or has_no(string.ascii_uppercase))
