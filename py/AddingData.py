# -*- coding: utf-8 -*-

import string
import random
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import rsa
import py.MainMenu
import py.StartWindow
import base64


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setMinimumSize(QtCore.QSize(400, 300))
        Dialog.setMaximumSize(QtCore.QSize(400, 300))
        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(50, 20, 301, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout.addWidget(self.lineEdit_5, 5, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout.addWidget(self.lineEdit_3, 3, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 3, 2, 1, 1)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout.addWidget(self.lineEdit_4, 4, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridLayout.addWidget(self.lineEdit_6, 6, 1, 1, 1)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_7.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit_7, 0, 1, 1, 1)
        self.lineEdit_7.hide()
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(179, 260, 171, 25))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_4 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)

        global lines
        [lines], = py.MainMenu.cur.execute("SELECT Count(*) FROM account_information")

        if lines != 0:
            global srt_section_mm
            srt_section_mm = py.MainMenu.srt_section
            for _item in srt_section_mm:
                exec('self.comboBox.addItem("")')
        else:
            self.add_section()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.lineEdit, self.lineEdit_2)
        Dialog.setTabOrder(self.lineEdit_2, self.lineEdit_3)
        Dialog.setTabOrder(self.lineEdit_3, self.lineEdit_4)
        Dialog.setTabOrder(self.lineEdit_4, self.lineEdit_5)
        Dialog.setTabOrder(self.lineEdit_5, self.lineEdit_6)
        Dialog.setTabOrder(self.lineEdit_6, self.comboBox)
        Dialog.setTabOrder(self.comboBox, self.pushButton)
        Dialog.setTabOrder(self.pushButton, self.pushButton_2)
        Dialog.setTabOrder(self.pushButton_2, self.pushButton_4)
        Dialog.setTabOrder(self.pushButton_4, self.pushButton_3)

        self.pushButton.clicked.connect(self.add_section)
        self.pushButton_2.clicked.connect(self.generate_password)
        self.pushButton_3.clicked.connect(self.add_data)
        self.pushButton_4.clicked.connect(self.close)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Password Saver - Добавление данных"))
        self.label_6.setText(_translate("Dialog", "Секретное слово"))
        self.pushButton.setText(_translate("Dialog", "Создать"))
        self.label_3.setText(_translate("Dialog", "Логин*"))
        self.label.setText(_translate("Dialog", "Раздел*"))
        self.label_2.setText(_translate("Dialog", "Название*"))
        self.label_4.setText(_translate("Dialog", "Пароль*"))
        self.label_5.setText(_translate("Dialog", "Почта"))
        self.pushButton_2.setText(_translate("Dialog", "Сгенерировать"))
        self.label_7.setText(_translate("Dialog", "URL"))
        self.pushButton_4.setText(_translate("Dialog", "Отмена"))
        self.pushButton_3.setText(_translate("Dialog", "Добавить"))

        if lines != 0:
            _indexItem = 0
            for _section in srt_section_mm:
                exec('self.comboBox.setItemText(%d, _translate("Dialog", "%s"))' % (_indexItem, _section))
                _indexItem += 1

    @QtCore.pyqtSlot()
    def add_data(self):
        if self.lineEdit_7.isVisible():
            section = self.lineEdit_7.text()
        elif self.comboBox.isVisible():
            section = self.comboBox.currentText()
        name = self.lineEdit.text()
        login = self.lineEdit_2.text()
        entered_password = self.lineEdit_3.text()
        password_bin = entered_password.encode()

        with open('{}_pubkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as pubfile:
            keydata_pub = pubfile.read()
            pubfile.close()
        pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')

        crypto_password = rsa.encrypt(password_bin, pubkey)
        password = (base64.b64encode(crypto_password)).decode()

        email = self.lineEdit_4.text()
        entered_secret_word = self.lineEdit_5.text()
        if entered_secret_word == '':
            entered_secret_word = 'None'

        secret_word_bin = entered_secret_word.encode()
        crypto_secret = rsa.encrypt(secret_word_bin, pubkey)
        secret_word = (base64.b64encode(crypto_secret)).decode()

        url = self.lineEdit_6.text()
        if section == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Сообщение")
            msg.setText("Введите раздел")
            msg.exec_()
        elif name == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Сообщение")
            msg.setText("Введите название")
            msg.exec_()
        elif login == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Сообщение")
            msg.setText("Введите логин")
            msg.exec_()
        elif entered_password == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Сообщение")
            msg.setText("Введите пароль")
            msg.exec_()
        else:
            if email == '':
                email = None
            if entered_secret_word == '':
                secret_word = None
            if url == '':
                url = None
            if lines != 0:
                exists_name = py.MainMenu.cur.execute("SELECT name FROM account_information WHERE name='{}'".format(name))
                exists_name = py.MainMenu.cur.fetchone()
                exists_login = py.MainMenu.cur.execute("SELECT login FROM account_information WHERE login='{}'".format(login))
                exists_login = py.MainMenu.cur.fetchone()
                if exists_name is not None and exists_login is not None:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setWindowTitle("Сообщение")
                    msg.setText("Такой аккаунт уже существует")
                    msg.exec_()
                else:
                    [maxid], = py.MainMenu.cur.execute("SELECT ID FROM account_information ORDER BY ID DESC LIMIT 1")
                    maxid += 1
                    py.MainMenu.cur.execute(
                        "INSERT INTO account_information (ID, section, name, login, pass, email, secret_word, url) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                            maxid, section, name, login, password, email, secret_word, url))
                    self.close()
            else:
                maxid = 1
                py.MainMenu.cur.execute(
                    "INSERT INTO account_information (ID, section, name, login, pass, email, secret_word, url) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                        maxid, section, name, login, password, email, secret_word, url))
                self.close()

    @QtCore.pyqtSlot()
    def add_section(self):
        self.comboBox.hide()
        self.pushButton.hide()
        self.lineEdit_7.show()

    @QtCore.pyqtSlot()
    def generate_password(self):
        def gen_pass():
            chars = string.ascii_letters + string.digits + '_' + '!' + '?' + '@'
            size = random.randint(8, 12)
            return ''.join(random.choice(chars) for x in range(size))
        self.lineEdit_3.setText(gen_pass())
