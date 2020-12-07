# -*- coding: utf-8 -*-

import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import rsa
import base64
import random
import string
import py.DatabaseCreation
import py.AddingData
import py.StartWindow
import py.res_rc

import pprint

version = 'v 0.2'        # Версия программы
hide_password = True     # Показазь или скрыть пароли при запуске программы: True - пароли скрыты / False - пароли показанны
buffer = None


def show_msg(top_text, bottom_text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(top_text)
    msg.setInformativeText(bottom_text)
    msg.setWindowTitle("Сообщение")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = msg.exec_()
    return result


class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.createdb = createdb()
        lines = 0
        global pubkey_file
        global privkey_file
        pubkey_file = os.path.isfile("data/{}_pubkey.pem".format(py.StartWindow.db_info[1][:-3]))   # True если есть в директории data/   если нету False
        privkey_file = os.path.isfile("data/{}_privkey.pem".format(py.StartWindow.db_info[1][:-3]))  # True если есть в директории data/   если нету False

    def connect_sql(self, connected):
        if connected:
            global conn
            global cur
            conn = sqlite3.connect(py.StartWindow.db_info[0])
            cur = conn.cursor()
            return True
        else:
            return False

    def setupUi(self, MainWindow):
        MainWindow.resize(870, 600)
        MainWindow.setMinimumSize(QtCore.QSize(870, 600))
        MainWindow.setMaximumSize(QtCore.QSize(870, 600))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(340, 0, 190, 30))
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
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 80, 830, 451))
        self.treeWidget.setAnimated(True)
        self.treeWidget.setObjectName("treeWidget")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(0, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(1, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(2, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(3, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(4, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(5, font)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.treeWidget.headerItem().setFont(6, font)
        self.add_treewidget_item()
        self.treeWidget.header().setDefaultSectionSize(118)
        self.treeWidget.header().setMinimumSectionSize(50)
        self.treeWidget.header().setStretchLastSection(True)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(530, 50, 311, 25))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_3 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(690, 20, 151, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(530, 20, 151, 23))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(530, 20, 151, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(810, 540, 31, 20))
        self.label_2.setObjectName("label_2")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 320, 65))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolButton_2 = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(22)
        sizePolicy.setVerticalStretch(29)
        sizePolicy.setHeightForWidth(self.toolButton_2.sizePolicy().hasHeightForWidth())
        self.toolButton_2.setSizePolicy(sizePolicy)
        self.toolButton_2.setMinimumSize(QtCore.QSize(23, 31))
        self.toolButton_2.setSizeIncrement(QtCore.QSize(55, 15))
        self.toolButton_2.setBaseSize(QtCore.QSize(24, 22))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        self.toolButton_2.setFont(font)
        self.toolButton_2.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.toolButton_2.setAcceptDrops(False)
        self.toolButton_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.toolButton_2.setStyleSheet("")
        self.toolButton_2.setInputMethodHints(QtCore.Qt.ImhNone)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/image/image/cross.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/image/image/checkmark.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.toolButton_2.setIcon(icon)
        self.toolButton_2.setAutoRepeat(False)
        self.toolButton_2.setAutoExclusive(False)
        self.toolButton_2.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolButton_2.setAutoRaise(True)
        self.toolButton_2.setObjectName("toolButton_2")
        self.verticalLayout.addWidget(self.toolButton_2)
        self.toolButton = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolButton.sizePolicy().hasHeightForWidth())
        self.toolButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.toolButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/image/image/cross.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/image/image/checkmark.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolButton.setAutoRaise(True)
        self.toolButton.setObjectName("toolButton")
        self.verticalLayout.addWidget(self.toolButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 870, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_5 = QtWidgets.QAction(MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_7 = QtWidgets.QAction(MainWindow)
        self.action_7.setObjectName("action_7")
        self.menu.addAction(self.action_3)
        self.menu.addAction(self.action_4)
        self.menu.addAction(self.action_5)
        self.menu.addSeparator()
        self.menu.addAction(self.action_7)
        self.menubar.addAction(self.menu.menuAction())

        global result_check_privkey
        if lines != 0 and privkey_file:
            try:
                with open('{}_privkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                first_pass = cur.execute("SELECT pass FROM account_information ORDER BY ID ASC LIMIT 1")
                first_pass = cur.fetchall()
                password_bin = (first_pass[0][0]).encode()
                password_dec = base64.b64decode(password_bin)
                decrypto = rsa.decrypt(password_dec, privkey)
                password = decrypto.decode()
                result_check_privkey = 'ok'
                print('Приватный ключ правильный')
            except rsa.pkcs1.DecryptionError:
                result_check_privkey = '!ok'
                print('Приватный ключ неправильный')
        elif lines == 0 and privkey_file and pubkey_file:
            try:
                with open('{}_privkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for x in range(20))
                rnd_pass = rnd_pass.encode()
                crypto_pass = rsa.encrypt(rnd_pass, pubkey)
                decrypto = rsa.decrypt(crypto_pass, privkey)
                print('Ключи в норме')
                result_check_privkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                print('Укажите правильные ключи, они разные')
                result_check_privkey = 'privkey != pubkey'
        elif lines == 0 and privkey_file and not pubkey_file:
            print('Укажите сначало публичный ключ')
            result_check_privkey = 'not pubkey'
        else:
            result_check_privkey = None

        global result_check_pubkey
        if pubkey_file and privkey_file and result_check_privkey == 'ok':
            try:
                with open('{}_privkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for x in range(20))
                rnd_pass = rnd_pass.encode()
                crypto_pass = rsa.encrypt(rnd_pass, pubkey)
                decrypto = rsa.decrypt(crypto_pass, privkey)
                print('Публичный ключ правильный')
                result_check_pubkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                print('Неправильный публичный ключ')
                result_check_pubkey = '!ok'
        elif lines != 0 and pubkey_file and privkey_file and result_check_privkey == '!ok':
            result_check_pubkey = 'not privkey'
        else:
            result_check_pubkey = None

        if hide_password:
            self.pushButton_4.hide()
        else:
            self.pushButton_5.hide()

        if pubkey_file and result_check_pubkey == 'ok':
            global pubkey_dir
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(py.StartWindow.db_info[1][:-3]))
            self.toolButton_2.setEnabled(False)
        elif pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)
        elif pubkey_file and result_check_pubkey is None:
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(py.StartWindow.db_info[1][:-3]))
            self.toolButton_2.setEnabled(False)
        elif pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_2.setEnabled(False)
            icon.addPixmap(QtGui.QPixmap(":/image/image/cross.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
            self.toolButton_2.setIcon(icon)
        else:
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)

        if privkey_file and result_check_privkey == 'ok':
            self.toolButton.setEnabled(False)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
        elif privkey_file and result_check_privkey == '!ok':
            self.toolButton.setEnabled(True)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
        elif privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton.setEnabled(True)
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)
        elif privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton.setEnabled(False)
            icon1.addPixmap(QtGui.QPixmap(":/image/image/cross.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
            self.toolButton.setIcon(icon1)
        else:
            self.toolButton.setEnabled(True)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)

        if lines == 0:
            self.pushButton.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.action_3.triggered.connect(self.savebd)
        self.action_4.triggered.connect(self.show_createdb)
        self.action_5.triggered.connect(self.loadbd)
        self.action_7.triggered.connect(self.close)
        self.pushButton.clicked.connect(self.delete_data)
        self.pushButton_2.clicked.connect(self.show_addingdata)
        self.pushButton_3.clicked.connect(self.copy_buffer)
        self.pushButton_4.clicked.connect(self.password_hide)
        self.pushButton_5.clicked.connect(self.password_show)
        self.toolButton.clicked.connect(self.choise_privkey)
        self.toolButton_2.clicked.connect(self.choise_pubkey)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextuelAlbum)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Password Saver - Главная | {}".format(py.StartWindow.db_info[1])))
        self.label.setText(_translate("MainWindow", "Password Saver"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Раздел"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Название"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Логин"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Пароль"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "Почта"))
        self.treeWidget.headerItem().setText(5, _translate("MainWindow", "Секретное слово"))
        self.treeWidget.headerItem().setText(6, _translate("MainWindow", "URL"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.add_treewidget_item_text()
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.pushButton_3.setText(_translate("MainWindow", "Копировать пароль в буфер"))
        self.pushButton.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        self.pushButton_4.setText(_translate("MainWindow", "Скрыть пароли"))
        self.pushButton_5.setText(_translate("MainWindow", "Показать пароли"))
        self.label_2.setText(_translate("MainWindow", "{}".format(version)))

        if pubkey_file and result_check_pubkey == 'ok':
            self.toolButton_2.setText(_translate("MainWindow", pubkey_dir))
        elif pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_2.setText(_translate("MainWindow", 'Ключ не подходит. Укажите pubkey.pem'))
        elif pubkey_file and result_check_pubkey is None:
            self.toolButton_2.setText(_translate("MainWindow", pubkey_dir))
        elif pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_2.setText(_translate("MainWindow", 'Сначало укажите privkey.pem'))
        else:
            self.toolButton_2.setText(_translate("MainWindow", "Укажите pubkey.pem"))

        # print(result_check_privkey)
        if privkey_file and result_check_privkey == 'ok':
            privkey_dir = os.path.abspath("data/{}_privkey.pem".format(py.StartWindow.db_info[1][:-3]))
            self.toolButton.setText(_translate("MainWindow", privkey_dir))
        elif privkey_file and result_check_privkey == '!ok':
            self.toolButton.setText(_translate("MainWindow", "Ключ не подходит. Укажите privkey.pem"))
        elif privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton.setText(_translate("MainWindow", "Ключи разные. Укажите павильный privkey.pem"))
            self.toolButton_2.setText(_translate("MainWindow", "Ключи разные. Укажите правильный pubkey.pem"))
        elif privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton.setText(_translate("MainWindow", "Сначало укажите pubkey.pem"))
        else:
            self.toolButton.setText(_translate("MainWindow", "Укажите privkey.pem"))

        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.action.setText(_translate("MainWindow", "Выход"))
        self.action_2.setText(_translate("MainWindow", "Сохранить"))
        self.action_3.setText(_translate("MainWindow", "Сохранить"))
        self.action_4.setText(_translate("MainWindow", "Создать новую БД"))
        self.action_5.setText(_translate("MainWindow", "Загрузить БД"))
        self.action_7.setText(_translate("MainWindow", "Выход"))

    @QtCore.pyqtSlot()
    def savebd(self):
        result = show_msg('Вы действительно хотите сохранить изменения в базе данных?', '')
        if result == QMessageBox.Yes:
            conn.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Сообщение")
            msg.setText("База данных сохранена")
            msg.exec_()
        elif result == QMessageBox.No:
            pass

    @QtCore.pyqtSlot()
    def show_createdb(self):
        self.createdb.show()

    @QtCore.pyqtSlot()
    def loadbd(self):
        print('loadbd')

    @QtCore.pyqtSlot()
    def show_addingdata(self):
        self.addingdata = addingdata()
        self.addingdata.exec_()
        self.refresh_treewidget()

        if lines != 0 and privkey_file and result_check_privkey == 'ok':
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
        elif lines != 0 and privkey_file and result_check_privkey == '!ok':
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
        elif lines == 0:
            self.pushButton.setEnabled(False)
        else:
            self.pushButton.setEnabled(True)

    @QtCore.pyqtSlot()
    def copy_buffer(self):  # TODO: сделать удаление буфера при закрытии программы с диспетчера задач
        global buffer
        row = self.current_row()    # TODO: сделать копирование расшифрованного пароля при скрытом отображении
        if row[1] == 'item_1':
            buffer = QtWidgets.QApplication.clipboard()
            if buffer is not None:
                buffer.setText(row[0][2])
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Сообщение")
                msg.setText("Пароль скопирован")
                msg.exec_()

    @QtCore.pyqtSlot()
    def delete_data(self):
        row = self.current_row()
        if row[1] == 'item_0 first' or row[1] == 'item_0':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Сообщение")
            msg.setText("Нельзя удалить раздел")
            msg.setInformativeText("Если хотите удалить раздел, то удалите все аккаунты в нём")
            msg.exec_()
        elif row[1] == 'item_1':
            result = show_msg('Данные аккаунта <b>{}</b> с логином <b>{}</b> будут удалены.'.format(row[0][0], row[0][1]), 'Вы уверенны?')
            if result == QMessageBox.Yes:
                cur.execute("DELETE FROM account_information WHERE name='{}' AND login='{}' AND email='{}' AND url='{}'".format(row[0][0], row[0][1], row[0][3], row[0][5]))
                self.refresh_treewidget()
            elif result == QMessageBox.No:
                pass
        if lines == 0:
            self.pushButton.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)

    @QtCore.pyqtSlot()
    def password_show(self):
        global hide_password
        hide_password = False
        _translate = QtCore.QCoreApplication.translate
        toplevelitem_iter = -1
        child_iter = -1
        text_iter = 0
        if lines != 0:
            with open('{}_privkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as privfile:
                keydata_priv = privfile.read()
                privfile.close()
            privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(srt_section[_data_section]))
                data_one_section = cur.fetchall()
                acc_info = []
                for _item in data_one_section:
                    acc_info.append(list(_item[2:]))
                for _i in acc_info:
                    password_bin = (_i[2]).encode()
                    password_dec = base64.b64decode(password_bin)
                    try:
                        decrypto = rsa.decrypt(password_dec, privkey)
                        password = decrypto.decode()
                    except rsa.pkcs1.DecryptionError:
                        password = '##ERRORPUBKEY##'
                    _i[2] = password

                    secret_word_bin = (_i[4]).encode()

                    secret_word_dec = base64.b64decode(secret_word_bin)
                    try:
                        decrypto_secret = rsa.decrypt(secret_word_dec, privkey)
                        secret_word = decrypto_secret.decode()
                    except rsa.pkcs1.DecryptionError:
                        secret_word = '##ERRORPUBKEY##'

                    _i[4] = secret_word
                exec('self.treeWidget.topLevelItem(%d).setText(0, _translate("MainWindow", "%s"))' % (_data_section, srt_section[_data_section]))
                toplevelitem_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if text_iter == 3 or text_iter == 5:
                            exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, _value))

        self.pushButton_5.hide()
        self.pushButton_4.show()

    @QtCore.pyqtSlot()
    def password_hide(self):
        global hide_password
        hide_password = True
        _translate = QtCore.QCoreApplication.translate
        toplevelitem_iter = -1
        child_iter = -1
        text_iter = 0
        if lines != 0:
            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(srt_section[_data_section]))
                data_one_section = cur.fetchall()
                acc_info = []
                for item in data_one_section:
                    acc_info.append(item[2:])
                exec('self.treeWidget.topLevelItem(%d).setText(0, _translate("MainWindow", "%s"))' % (_data_section, srt_section[_data_section]))
                toplevelitem_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if text_iter == 3 or text_iter == 5:
                            exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, '**********'))

        self.pushButton_4.hide()
        self.pushButton_5.show()

    @QtCore.pyqtSlot()
    def choise_pubkey(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(None, 'Укажите файл {}_pubkey.pem'.format(py.StartWindow.db_info[1][:-3]), os.getcwd(), 'key({}_pubkey.pem)'.format(py.StartWindow.db_info[1][:-3]))
        print(directory_name)
        pass

    @QtCore.pyqtSlot()
    def choise_privkey(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(None, 'Укажите файл {}_privkey.pem'.format(py.StartWindow.db_info[1][:-3]), os.getcwd(), 'key({}_privkey.pem)'.format(py.StartWindow.db_info[1][:-3]))
        print(directory_name)
        pass

    def menuContextuelAlbum(self, event):
        self.menu_contextuelAlb = QtWidgets.QMenu(self.treeWidget)
        rmenu_copy_log = self.menu_contextuelAlb.addAction("Копировать логин")
        rmenu_copy_pass = self.menu_contextuelAlb.addAction("Копировать пароль")
        rmenu_copy_email = self.menu_contextuelAlb.addAction("Копировать почту")
        rmenu_copy_secret = self.menu_contextuelAlb.addAction("Копировать секретное слово")
        rmenu_copy_url = self.menu_contextuelAlb.addAction("Копировать url")
        action2 = self.menu_contextuelAlb.exec_(self.treeWidget.mapToGlobal(event))
        if action2 is not None:
            if action2 == rmenu_copy_log:
                print('Копировать логин')
            elif action2 == rmenu_copy_pass:
                print('Копировать пароль')
            elif action2 == rmenu_copy_email:
                print('Копировать почту')
            elif action2 == rmenu_copy_secret:
                print('Копировать секретное слово')
            elif action2 == rmenu_copy_url:
                print('Копировать url')

    def add_treewidget_item(self):
        global lines
        [lines], = cur.execute("SELECT Count(*) FROM account_information")
        global amount_item_0
        amount_item_0 = 0
        amount_item_1 = lines
        section = []
        if lines != 0:
            for _line in range(1, lines + 1):
                [_current_id], = cur.execute("SELECT ID FROM account_information LIMIT 1 OFFSET {}".format(_line-1))
                [_current_section], = cur.execute("SELECT section FROM account_information WHERE ID='{}'".format(_current_id))
                section.append(_current_section)
            global srt_section
            srt_section = list(dict.fromkeys(section))
            amount_item_0 = len(list(set(section)))
            for _data_section in range(amount_item_0):
                if _data_section == 0:
                    item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(0, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(1, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(2, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(3, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(4, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(5, brush)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    item_0.setBackground(6, brush)
                    data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(srt_section[_data_section]))
                    data_one_section = cur.fetchall()
                else:
                    data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(srt_section[_data_section]))
                    data_one_section = cur.fetchall()
                    item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
                for _value in range(len(data_one_section)):
                    item_1 = QtWidgets.QTreeWidgetItem(item_0)

    def delete_treewidget_item(self):
        self.treeWidget.clear()

    def add_treewidget_item_text(self):
        _translate = QtCore.QCoreApplication.translate
        toplevelitem_iter = -1
        child_iter = -1
        text_iter = 0
        if lines != 0:
            if privkey_file:
                with open('{}_privkey.pem'.format(py.StartWindow.db_info[0][:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(srt_section[_data_section]))
                data_one_section = cur.fetchall()
                acc_info = []
                for item in data_one_section:
                    acc_info.append(item[2:])
                exec('self.treeWidget.topLevelItem(%d).setText(0, _translate("MainWindow", "%s"))' % (_data_section, srt_section[_data_section]))
                toplevelitem_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if (text_iter == 3 and hide_password) or (text_iter == 5 and hide_password):
                            exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, '**********'))
                        elif len(_value) == 172:
                                value_bin = (_value).encode()
                                value_dec = base64.b64decode(value_bin)
                                try:
                                    decrypto_value = rsa.decrypt(value_dec, privkey)
                                    value = decrypto_value.decode()
                                    exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, value))
                                except rsa.pkcs1.DecryptionError:
                                    value = '##ERRORPUBKEY##'
                                    exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, value))
                        else:
                            exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, _value))

    def refresh_treewidget(self):
        self.delete_treewidget_item()
        self.add_treewidget_item()
        self.add_treewidget_item_text()
        self.treeWidget.expandAll()

    def current_row(self):
        index = self.treeWidget.selectedIndexes()
        row_data = []
        iter_number = 0
        item_type = None
        for _index_item in index:
            values_dict = _index_item.model().itemData(_index_item)
            if iter_number == 0:
                if len(values_dict) == 0:
                    item_type = 'item_1'
                elif len(values_dict) == 1:
                    item_type = 'item_0'
                elif len(values_dict) == 2:
                    item_type = 'item_0 first'
            for key, value in values_dict.items():
                if value is None:
                    continue
                row_data.append(value)
            iter_number += 1
        return row_data, item_type

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self, "Выход", "Все несохраненные изменения будут потеряны.\nВсе ровно выйти?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            if buffer is not None:
                buffer.clear()
            event.accept()
        else:
            event.ignore()


class createdb(QtWidgets.QDialog, py.DatabaseCreation.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class addingdata(QtWidgets.QDialog, py.AddingData.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
