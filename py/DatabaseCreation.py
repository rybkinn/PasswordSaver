# -*- coding: utf-8 -*-
import os
import string
from sys import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import rsa
import py.MainMenu
from py.waitingspinnerwidget import QtWaitingSpinner
import py.ui.DatabaseCreation_ui as DatabaseCreation_ui
if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

validate_password = None
name_created_database = None


def show_msg(value, text_show, add_fields=False, informative_text=None, detailed_text=None):
    width = 500
    if value:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        if add_fields:
            msg.setText(text_show + ' ' * width)
        else:
            msg.setText(text_show)
        msg.setWindowTitle("Успех")
        if add_fields:
            msg.setInformativeText(informative_text)
            msg.setDetailedText(detailed_text)
        msg.exec()
        result = True
        return result
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text_show)
        msg.setWindowTitle("Ошибка")
        if add_fields:
            msg.setInformativeText(informative_text)
            msg.setDetailedText(detailed_text)
        msg.exec()
        result = False
        return result


class ThreadCreateKeys(QtCore.QThread):
    def __init__(self, name_db, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.name_db = name_db

    def run(self):
        (pubkey, privkey) = rsa.newkeys(py.MainMenu.new_rsa_bit)
        pubkey_pem = pubkey.save_pkcs1('PEM')
        privkey_pem = privkey.save_pkcs1('PEM')
        with open('data/{0}_pubkey.pem'.format(self.name_db), mode='w+') as pubfile:
            pubfile.write(pubkey_pem.decode())
            pubfile.close()
        with open('data/{0}_privkey.pem'.format(self.name_db), mode='w+') as privfile:
            privfile.write(privkey_pem.decode())
            privfile.close()


class CreateDB(QtWidgets.QDialog, DatabaseCreation_ui.Ui_Dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.label_6.hide()

        # self.lineEdit.setPlaceholderText('Введите название БД')

        self.spinner = QtWaitingSpinner(self, centerOnParent=False, disableParentWhenSpinning=True)
        self.spinner.setGeometry(QtCore.QRect(180, 230, 121, 16))
        self.spinner.setRoundness(70.0)
        self.spinner.setMinimumTrailOpacity(15.0)
        self.spinner.setTrailFadePercentage(70.0)
        self.spinner.setNumberOfLines(12)
        self.spinner.setLineLength(10)
        self.spinner.setLineWidth(5)
        self.spinner.setInnerRadius(10)
        self.spinner.setRevolutionsPerSecond(1)
        self.spinner.setColor(QtGui.QColor(0, 0, 0))

        self.setWindowIcon(QtGui.QIcon('resource/image/key.ico'))

        self.pushButton.clicked.connect(self.create_database)
        self.lineEdit.textChanged.connect(self.valid_namedb)
        self.lineEdit_2.textChanged.connect(self.valid_passwd)
        self.lineEdit_3.textChanged.connect(self.confirm_passwd)

        self.create_keys = None

    @QtCore.pyqtSlot()
    def valid_namedb(self):
        data_files = os.listdir(path="data")
        name_db = self.lineEdit.text()
        new_name_bd = []
        for _name_bd in data_files:
            type_file = _name_bd[_name_bd.find("."):]
            if type_file == '.db':
                new_name_bd.append(_name_bd[:-3])
        if len(new_name_bd) == 0:
            self.lineEdit.setStyleSheet("border: 1px solid green")
        else:
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
        if self._isvalid_pass(password):
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
                show_msg(0, 'Неправильный пароль',
                         add_fields=True,
                         informative_text='- 8 символов или больше\n'
                                          '- Верхний и нижний регистр\n'
                                          '- Минимум 1 цифра\n'
                                          '- Не может быть русскими буквами')
                self.lineEdit_2.setStyleSheet("border: 1px solid red")
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
            elif pwd_re == '':
                show_msg(0, 'Поле Подтвердите пароль пустое')
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
            elif pwd == pwd_re:
                conn = sqlite3.connect(r'data/' + name_db + '.db')
                cur = conn.cursor()
                cur.execute("PRAGMA key = '{}'".format(pwd))
                cur.execute("PRAGMA foreign_keys = ON")
                cur.execute("""CREATE TABLE IF NOT EXISTS account_information(
                    "id" INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
                    "section" TEXT NOT NULL,
                    "name" TEXT NOT NULL,
                    "login" TEXT NOT NULL,
                    "pass" TEXT NOT NULL,
                    "email" TEXT DEFAULT 'NULL',
                    "secret_word" TEXT DEFAULT 'NULL',
                    "url" TEXT DEFAULT 'NULL')
                """)
                cur.execute("""CREATE TABLE IF NOT EXISTS db_information(
                    "name" TEXT NOT NULL,
                    "value" INTEGER NOT NULL)
                """)
                cur.execute("""CREATE TABLE IF NOT EXISTS data_change_time(
                    "id" INTEGER NOT NULL UNIQUE REFERENCES account_information (id) ON DELETE CASCADE 
                                                                                     ON UPDATE CASCADE,
                    "create_account" TEXT NOT NULL,
                    "update_account" TEXT DEFAULT 'NULL',
                    "change_section" TEXT DEFAULT 'NULL',
                    "change_login" TEXT DEFAULT 'NULL',
                    "change_pass" TEXT DEFAULT 'NULL',
                    "change_email" TEXT DEFAULT 'NULL',
                    "change_secret_word" TEXT DEFAULT 'NULL',
                    "change_url" TEXT DEFAULT 'NULL')
                """)
                cur.execute("INSERT INTO db_information (name, value) VALUES ('rsa_bit', {})".format(
                    py.MainMenu.new_rsa_bit))
                conn.commit()
                cur.close()
                conn.close()
                self.create_keys = ThreadCreateKeys(name_db=self.lineEdit.text())
                self.create_keys.started.connect(self.spinner_started)
                self.create_keys.finished.connect(self.spinner_finished)
                self.create_keys.start()
            else:
                show_msg(0, 'Пароли не совпадают')
                self.lineEdit_3.setStyleSheet("border: 1px solid red")
        else:
            show_msg(0, 'Введите название БД')
            self.lineEdit.setStyleSheet("border: 1px solid red")

    @QtCore.pyqtSlot()
    def spinner_started(self):
        self.spinner.start()
        self.label_6.show()

    @QtCore.pyqtSlot()
    def spinner_finished(self):
        self.spinner.stop()
        self.label_6.hide()
        created_db = show_msg(1, 'База данных успешно создана.',
                              add_fields=True,
                              informative_text='Более подробно по нажатию кнопки "Show Details..."',
                              detailed_text='- База данных: \n' + os.getcwd() + '\\data\\' + self.lineEdit.text() +
                                            '.db' + '\n\n'
                                                    
                                            '- Публичный ключ: \n' + os.getcwd() + '\\data\\' + self.lineEdit.text() +
                                            '_pubkey.pem' + '\n\n'
                                                            
                                            '- Приватный ключ: \n' + os.getcwd() + '\\data\\' + self.lineEdit.text() +
                                            '_privkey.pem')
        if created_db:
            global name_created_database
            name_created_database = self.lineEdit.text()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit.setStyleSheet("border: 1px solid gray")
        self.lineEdit_2.setStyleSheet("border: 1px solid gray")
        self.lineEdit_3.setStyleSheet("border: 1px solid gray")
        self.close()

    @staticmethod
    def _isvalid_pass(password):
        has_no = set(password).isdisjoint
        return not (len(password) < 8 or
                    has_no(string.digits) or
                    has_no(string.ascii_lowercase) or
                    has_no(string.ascii_uppercase))
