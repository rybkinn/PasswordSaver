#!/usr/bin/env python3
import string
import random
import base64
import datetime
import rsa

from PyQt5 import QtCore, QtWidgets, QtGui

import py.main_menu as main_menu
import py.ui.adding_data_ui as adding_data_ui
from py.show_msg import show_msg


class AddingData(QtWidgets.QDialog, adding_data_ui.Ui_Dialog):

    def __init__(self, srt_section, choice_pubkey, db_dir):
        super().__init__()
        self.setupUi(self)

        self.db_dir = db_dir

        self.choice_pubkey = choice_pubkey

        self.checkbox_copy_buffer = 0

        self.lineEdit_7 = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout.addWidget(self.lineEdit_7, 0, 1, 1, 1)
        self.lineEdit_7.hide()
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_5.setEnabled(False)

        [lines], = main_menu.cur.execute(
            "SELECT Count(*) FROM account_information")
        self.lines = lines

        if self.lines != 0:
            self.srt_section_main_menu = srt_section
            for _ in self.srt_section_main_menu:
                self.comboBox.addItem("")
        else:
            self.add_section()

        self.checkBox.setText(f"на {main_menu.BUFFER_DEL_SEC} секунд")
        if self.lines != 0:
            for index_item, section in enumerate(
                    self.srt_section_main_menu):
                self.comboBox.setItemText(index_item, str(section))

        self.pushButton.clicked.connect(self.add_section)
        self.pushButton_2.clicked.connect(self.generate_password)
        self.pushButton_3.clicked.connect(self.add_data)
        self.pushButton_4.clicked.connect(self.close)
        self.pushButton_5.clicked.connect(self.copy_password)

        self.lineEdit_3.textChanged.connect(self.copy_password_visible)

    @QtCore.pyqtSlot()
    def add_data(self):
        section = None
        if self.lineEdit_7.isVisible():
            section = self.lineEdit_7.text()
        elif self.comboBox.isVisible():
            section = self.comboBox.currentText()
        name = self.lineEdit.text()
        login = self.lineEdit_2.text()
        entered_password = self.lineEdit_3.text()
        password_bin = entered_password.encode()

        if self.choice_pubkey is not None:
            pubkey = self.choice_pubkey
        else:
            with open('{}_pubkey.pem'.format(self.db_dir[:-3]), 'rb') \
                    as pubfile:
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
            show_msg(title='Ошибка',
                     top_text='Введите раздел',
                     window_type='critical',
                     buttons='ok')
        elif name == '':
            show_msg(title='Ошибка',
                     top_text='Введите название',
                     window_type='critical',
                     buttons='ok')
        elif login == '':
            show_msg(title='Ошибка',
                     top_text='Введите логин',
                     window_type='critical',
                     buttons='ok')
        elif entered_password == '':
            show_msg(title='Ошибка',
                     top_text='Введите пароль',
                     window_type='critical',
                     buttons='ok')
        else:
            if email == '':
                email = 'None'
            if entered_secret_word == '':
                secret_word = 'None'
            if url == '':
                url = 'None'
            if self.lines == 0:
                new_id = 1
                main_menu.cur.execute("""
                    INSERT INTO account_information
                    (ID, section, name, login, pass, email, secret_word, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                        new_id, section, name, login, password,
                        email, secret_word, url))
                main_menu.cur.execute("""
                    INSERT INTO data_change_time
                    (id, create_account)
                    VALUES (?, ?)""", (
                        new_id,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                if self.checkBox.isChecked():
                    main_menu.buffer = QtWidgets.QApplication.clipboard()
                    main_menu.buffer.setText(entered_password)
                    self.checkbox_copy_buffer = 1
                self.close()
            else:
                main_menu.cur.execute("""
                    SELECT name 
                    FROM account_information 
                    WHERE name='{}'""".format(name))
                # TODO: Нужно передавать conn работать с ним и возвращать.
                exists_name = main_menu.cur.fetchone()
                main_menu.cur.execute("""
                    SELECT login 
                    FROM account_information 
                    WHERE login='{}'""".format(login))
                exists_login = main_menu.cur.fetchone()
                if exists_name is not None and exists_login is not None:
                    show_msg(title='Ошибка',
                             top_text='Такой аккаунт уже существует',
                             window_type='critical',
                             buttons='ok')
                else:
                    [max_id], = main_menu.cur.execute("""
                        SELECT ID 
                        FROM account_information 
                        ORDER BY ID 
                        DESC LIMIT 1""")
                    new_id = max_id + 1
                    main_menu.cur.execute("""
                        INSERT INTO account_information
                        (id, section, name, login, 
                        pass, email, secret_word, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                            new_id, section, name, login, password,
                            email, secret_word, url))
                    main_menu.cur.execute("""
                        INSERT INTO data_change_time
                        (id, create_account)
                        VALUES (?, ?)""", (
                            new_id,
                            datetime.datetime.now().strftime(
                                '%Y-%m-%d %H:%M:%S')))

                    if self.checkBox.isChecked():
                        main_menu.buffer = QtWidgets.QApplication.clipboard()
                        main_menu.buffer.setText(entered_password)
                        self.checkbox_copy_buffer = 1
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

    # TODO: Сделать функцию таймера по времени и перенести в отдельный файл.
    def copy_password(self):
        buffer = QtWidgets.QApplication.clipboard()
        buffer.setText(self.lineEdit_3.text())

    def copy_password_visible(self):
        if len(self.lineEdit_3.text()) > 0:
            self.pushButton_5.setEnabled(True)
        else:
            self.pushButton_5.setEnabled(False)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.done(self.checkbox_copy_buffer)
