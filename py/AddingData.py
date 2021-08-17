# -*- coding: utf-8 -*-
import string
import random
import base64
import datetime
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import rsa
import py.MainMenu as MainMenu
import py.ui.AddingData_ui as AddingData_ui

checkbox_pass = False


class AddingData(QtWidgets.QDialog, AddingData_ui.Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.lineEdit_7 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout.addWidget(self.lineEdit_7, 0, 1, 1, 1)
        self.lineEdit_7.hide()
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_5.setEnabled(False)

        [lines], = MainMenu.cur.execute("SELECT Count(*) FROM account_information")
        self.lines = lines

        if self.lines != 0:
            self.srt_section_mm = MainMenu.srt_section
            for _item in self.srt_section_mm:
                self.comboBox.addItem("")
        else:
            self.add_section()

        self.checkBox.setText(f"на {MainMenu.buffer_del_sec} секунд")
        if self.lines != 0:
            for _indexItem, _section in enumerate(self.srt_section_mm):
                self.comboBox.setItemText(_indexItem, str(_section))

        self.pushButton.clicked.connect(self.add_section)
        self.pushButton_2.clicked.connect(self.generate_password)
        self.pushButton_3.clicked.connect(self.add_data)
        self.pushButton_4.clicked.connect(self.close)
        self.pushButton_5.clicked.connect(self.copy_pass)

        self.lineEdit_3.textChanged.connect(self.copy_pass_visible)

    @QtCore.pyqtSlot()
    def add_data(self):
        global checkbox_pass
        section = None
        if self.lineEdit_7.isVisible():
            section = self.lineEdit_7.text()
        elif self.comboBox.isVisible():
            section = self.comboBox.currentText()
        name = self.lineEdit.text()
        login = self.lineEdit_2.text()
        entered_password = self.lineEdit_3.text()
        password_bin = entered_password.encode()

        if MainMenu.choise_pubkey is not None:
            pubkey = MainMenu.choise_pubkey
        else:
            with open('{}_pubkey.pem'.format(MainMenu.db_dir[:-3]), 'rb') as pubfile:
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
                email = 'None'
            if entered_secret_word == '':
                secret_word = 'None'
            if url == '':
                url = 'None'
            if self.lines == 0:
                new_id = 1
                MainMenu.cur.execute("""INSERT INTO account_information
                                           (ID, section, name, login, pass, email, secret_word, url)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                     (new_id, section, name, login, password, email, secret_word, url))
                MainMenu.cur.execute("""INSERT INTO data_change_time
                                           (id, create_account)
                                           VALUES (?, ?)""",
                                     (new_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                if self.checkBox.isChecked():
                    MainMenu.buffer = QtWidgets.QApplication.clipboard()
                    MainMenu.buffer.setText(entered_password)
                    checkbox_pass = True
                self.close()
            else:
                MainMenu.cur.execute("SELECT name FROM account_information WHERE name='{}'".format(name))
                exists_name = MainMenu.cur.fetchone()    # TODO: Нужно передавать conn работать с ним и возвращать.
                MainMenu.cur.execute("SELECT login FROM account_information WHERE login='{}'".format(login))
                exists_login = MainMenu.cur.fetchone()
                if exists_name is not None and exists_login is not None:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setWindowTitle("Сообщение")
                    msg.setText("Такой аккаунт уже существует")
                    msg.exec_()
                else:
                    [maxid], = MainMenu.cur.execute("SELECT ID FROM account_information ORDER BY ID DESC LIMIT 1")
                    new_id = maxid + 1
                    MainMenu.cur.execute("""INSERT INTO account_information
                                               (id, section, name, login, pass, email, secret_word, url)
                                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                         (new_id, section, name, login, password, email, secret_word, url))
                    MainMenu.cur.execute("""INSERT INTO data_change_time
                                               (id, create_account)
                                               VALUES (?, ?)""",
                                         (new_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                    if self.checkBox.isChecked():
                        MainMenu.buffer = QtWidgets.QApplication.clipboard()
                        MainMenu.buffer.setText(entered_password)
                        checkbox_pass = True
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
            return ''.join(random.choice(chars) for _ in range(size))
        self.lineEdit_3.setText(gen_pass())

    def copy_pass(self):    # TODO: Сделать функцию таймера по времени и перенести в отдельный файл.
        buffer = QtWidgets.QApplication.clipboard()
        buffer.setText(self.lineEdit_3.text())

    def copy_pass_visible(self):
        if len(self.lineEdit_3.text()) > 0:
            self.pushButton_5.setEnabled(True)
        else:
            self.pushButton_5.setEnabled(False)
