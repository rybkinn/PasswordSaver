# -*- coding: utf-8 -*-
import base64
import os
from sys import platform

import PyQt5.Qt
import rsa
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from py.waitingspinnerwidget import QtWaitingSpinner

if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
#     OS X
from pysqlcipher3.dbapi2 import Error
import py.MainMenu

finish_sync = False


class MyThread(QtCore.QThread):
    def __init__(self, path, pwd, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.path = path
        self.pwd = pwd

    def run(self):  # TODO: добавить очистку sync БД и копирование всех данных с main БД в sync БД.
        added_acc_count = 0
        tread_conn_main = sqlite3.connect(py.MainMenu.db_dir)
        tread_cur_main = tread_conn_main.cursor()
        tread_cur_main.execute("PRAGMA key = '{}'".format(self.pwd))
        rows_main_db = tread_cur_main.execute('SELECT * FROM account_information').fetchall()
        rows_main_db_without_id = []
        last_id_main = tread_cur_main.execute('SELECT MAX(id) FROM account_information').fetchall()[0][0]
        new_id_main = last_id_main + 1

        for row_main in rows_main_db:
            rows_main_db_without_id.append(row_main[1:])

        tread_conn_sync = sqlite3.connect(self.path)
        tread_cur_sync = tread_conn_sync.cursor()
        tread_cur_sync.execute("PRAGMA key = '{}'".format(self.pwd))
        rows_sync_db = tread_cur_sync.execute('SELECT * FROM account_information').fetchall()

        for row_sync in rows_sync_db:
            if row_sync[1:] in rows_main_db_without_id:
                continue
            else:
                row_sync_new_id = (new_id_main, ) + row_sync[1:]
                tread_cur_main.execute('INSERT INTO account_information VALUES (?,?,?,?,?,?,?,?)', row_sync_new_id)
                new_id_main += 1
                added_acc_count += 1

        tread_conn_main.commit()
        tread_cur_main.close()
        tread_cur_sync.close()
        tread_conn_main.close()
        tread_conn_sync.close()


def create_and_check_connection(path: str, pwd: str) -> sqlite3.Connection or None:
    """
    Соединяется с БД и проверяет пароль. Возврощает None или объект соединения.
    :param path: path to database file
    :param pwd: input password for database
    :return: sqlite3.Connection object / None
    """
    try:
        conn_sync = sqlite3.connect(path)
        cur_sync = conn_sync.cursor()
        cur_sync.execute("PRAGMA key = '{}'".format(pwd))
        cur_sync.execute("SELECT name from account_information WHERE id=1")
        cur_sync.close()
        return conn_sync
    except Error as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка синхронизации")
        msg.setText("Неправильный пароль")
        msg.exec_()
        conn_sync = None
        return conn_sync


def execute_read_query(conn_sync: sqlite3.Connection, query: str) -> list:
    """
    Выполняет переданный sql запрос к БД и возврощает результат.
    :param conn_sync: sqlite3.Connection object
    :param query: sql query string
    :return: list
    """
    result = []
    cur_sync = conn_sync.cursor()
    try:
        cur_sync.execute(query)
        result = cur_sync.fetchall()
        cur_sync.close()
        return result
    except Error as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка синхронизации")
        msg.setText(f"Ошибка выполнения запроса: ({e})")
        msg.exec_()
        cur_sync.close()
        return result


def decrypt(crypt_s: str) -> str:
    """
    Расшифровывает строку по приватному ключу и возврощает её.
    :param crypt_s: Input crypto string
    :return: Output decrypt string or 'error'
    """
    if py.MainMenu.result_check_choise_privkey == 'ok':
        privkey = py.MainMenu.choise_privkey
    else:
        with open(py.MainMenu.privkey_dir, 'rb') as privfile:
            keydata_priv = privfile.read()
            privfile.close()
        privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
    password_bin = crypt_s.encode()
    password_dec = base64.b64decode(password_bin)
    try:
        decrypto = rsa.decrypt(password_dec, privkey)
        result = decrypto.decode()
        return result
    except rsa.pkcs1.DecryptionError:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка синхронизации")
        msg.setText("password decode error")
        msg.exec_()
        return 'error'


class Ui_Dialog(object):
    def __init__(self):
        self.databases_from_dir = []

    def setupUi(self, Dialog):
        path_dir = os.getcwd()
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 450)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(400, 450))
        Dialog.setMaximumSize(QtCore.QSize(400, 450))
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(30, 10, 30, 50)
        self.gridLayout.setHorizontalSpacing(30)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setStyleSheet("padding-bottom: 70px;")
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 3)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setMinimumSize(QtCore.QSize(150, 35))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setStyleSheet("")
        self.gridLayout.addWidget(self.lineEdit, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setStyleSheet("margin: 5px 0px 5px 0px;")
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 8, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setMinimumSize(QtCore.QSize(20, 20))
        self.label_7.setMaximumSize(QtCore.QSize(20, 20))
        self.label_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_7.setAutoFillBackground(False)
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        self.label_7.setScaledContents(True)
        self.label_7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_7.setWordWrap(False)
        self.label_7.setOpenExternalLinks(False)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 9, 0, 1, 1, QtCore.Qt.AlignRight)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setMinimumSize(QtCore.QSize(20, 20))
        self.label_6.setMaximumSize(QtCore.QSize(20, 20))
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAutoFillBackground(False)
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        self.label_6.setScaledContents(True)
        self.label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_6.setWordWrap(False)
        self.label_6.setOpenExternalLinks(False)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 8, 0, 1, 1, QtCore.Qt.AlignRight)
        self.label_3 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setStyleSheet("margin: 5px 0px 5px 0px;")
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 7, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 10, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(150, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(190, 30))
        self.pushButton.setSizeIncrement(QtCore.QSize(0, 0))
        self.pushButton.setBaseSize(QtCore.QSize(0, 0))
        self.pushButton.setStyleSheet("")
        self.pushButton.setAutoDefault(False)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 5, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setMinimumSize(QtCore.QSize(20, 20))
        self.label_5.setMaximumSize(QtCore.QSize(20, 20))
        self.label_5.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_5.setAutoFillBackground(False)
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        self.label_5.setScaledContents(True)
        self.label_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_5.setWordWrap(False)
        self.label_5.setIndent(-1)
        self.label_5.setOpenExternalLinks(False)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setStyleSheet("margin: 5px 0px 5px 0px;")
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 9, 1, 1, 1)
        self.toolButton = QtWidgets.QToolButton(Dialog)
        self.toolButton.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 3, 2, 1, 1)
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
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 3)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMinimumSize(QtCore.QSize(150, 35))
        self.comboBox.setCurrentText("")
        self.comboBox.setInsertPolicy(QtWidgets.QComboBox.InsertAtBottom)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setStyleSheet("")
        data_files_name = os.listdir(path="data")
        self.databases_from_dir.clear()
        for _name_db in data_files_name:
            type_file = _name_db[_name_db.find("."):]
            if type_file == '.db':
                self.databases_from_dir.append(_name_db)
        for _addItem in self.databases_from_dir:
            path_to_db = [path_dir + '/data/' + _addItem, _addItem]  # changed \\data\\ => /data/ from linux
            exec('self.comboBox.addItem("", path_to_db)')
        self.gridLayout.addWidget(self.comboBox, 3, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setStyleSheet("")
        self.label_11.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.label_11.setWordWrap(False)
        self.label_11.setIndent(-1)
        self.label_11.setOpenExternalLinks(False)
        self.label_11.setObjectName("label_11")
        self.label_11.setHidden(True)
        self.gridLayout.addWidget(self.label_11, 13, 0, 1, 3, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        self.spinner = QtWaitingSpinner(self, centerOnParent=False, disableParentWhenSpinning=True)
        self.spinner.setGeometry(QtCore.QRect(180, 240, 121, 16))
        self.spinner.setRoundness(70.0)
        self.spinner.setMinimumTrailOpacity(15.0)
        self.spinner.setTrailFadePercentage(70.0)
        self.spinner.setNumberOfLines(12)
        self.spinner.setLineLength(10)
        self.spinner.setLineWidth(5)
        self.spinner.setInnerRadius(10)
        self.spinner.setRevolutionsPerSecond(1)
        self.spinner.setColor(QtGui.QColor(0, 0, 0))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.pushButton, self.comboBox)
        Dialog.setTabOrder(self.comboBox, self.toolButton)
        Dialog.setTabOrder(self.toolButton, self.lineEdit)

        self.toolButton.clicked.connect(self.push_tool_button)
        self.pushButton.clicked.connect(self.start_sync)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Синхронизация БД"))
        self.label_2.setText(_translate("Dialog", "Синхронизация базы данных"))
        self.label_9.setText(_translate("Dialog", "БД не пустая"))
        self.label_3.setText(_translate("Dialog", "Выберете базу"))
        self.label_8.setText(_translate("Dialog", "Пароль подходит"))
        self.pushButton.setText(_translate("Dialog", "Синхронизировать"))
        self.label_4.setText(_translate("Dialog", "Введите пароль"))
        self.label_10.setText(_translate("Dialog", "Совпадают ключи"))
        self.toolButton.setText(_translate("Dialog", "..."))
        self.label.setText(_translate("Dialog", "Password Saver"))
        self.label_11.setText(_translate("Dialog", "Добавлено 0 аккаунтов"))
        _indexItem = 0
        for _addItem in self.databases_from_dir:
            exec('self.comboBox.setItemText(%d, _translate("Dialog", "%s"))' % (_indexItem, _addItem))
            _indexItem += 1

    @QtCore.pyqtSlot()
    def push_tool_button(self):
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Открытие базы данных', os.getcwd(), 'database files(*.db)')
        if directory_name[0] != '':
            self.comboBox.clear()
            filename = ''
            for _letter in reversed(directory_name[0]):
                if _letter == '/':
                    break
                filename += _letter
            file_info = [filename[::-1], directory_name]
            db_data = [file_info[1][0], file_info[0]]
            self.comboBox.addItem("", db_data)
            self.comboBox.setItemText(0, file_info[0])

    @QtCore.pyqtSlot()
    def start_sync(self):
        self.label_5.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        self.label_6.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        self.label_7.setPixmap(QtGui.QPixmap("resource/image/question.ico"))
        path = self.comboBox.currentData()[0]
        pwd = self.lineEdit.text()
        conn_sync = create_and_check_connection(path, pwd)
        if conn_sync is not None:
            self.label_5.setPixmap(QtGui.QPixmap("resource/image/checkmark.ico"))
            check_empty = "SELECT * from account_information"
            rows = execute_read_query(conn_sync, check_empty)
            if len(rows) != 0:
                self.label_6.setPixmap(QtGui.QPixmap("resource/image/checkmark.ico"))
                decrypt_result = decrypt(rows[0][4])
                if decrypt_result != 'error':
                    self.label_7.setPixmap(QtGui.QPixmap("resource/image/checkmark.ico"))
                else:
                    self.label_7.setPixmap(QtGui.QPixmap("resource/image/cross.ico"))
                self.mythread = MyThread(path, pwd)
                self.mythread.started.connect(self.spinner_started)
                self.mythread.finished.connect(self.spinner_finished)
                self.mythread.start()
            else:
                self.label_6.setPixmap(QtGui.QPixmap("resource/image/cross.ico"))
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Ошибка синхронизации")
                msg.setText("База данных пустая")
                msg.exec_()
            conn_sync.close()
        else:
            self.label_5.setPixmap(QtGui.QPixmap("resource/image/cross.ico"))
            self.lineEdit.clear()

    @QtCore.pyqtSlot()
    def spinner_started(self):
        self.spinner.start()
        self.label_11.setText("Синхронизирую...")
        self.label_11.show()

    @QtCore.pyqtSlot()
    def spinner_finished(self):
        self.spinner.stop()
        self.label_11.setText("Синхронизация завершена")
        self.label_11.setStyleSheet("font-weight: 900; font-size: 16px")
        self.pushButton.setEnabled(False)
        global finish_sync
        finish_sync = True
