# -*- coding: utf-8 -*-

import os.path
import base64
import random
import string
import datetime
from sys import platform
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtWidgets import QMessageBox
import rsa
import py.DatabaseCreation as DatabaseCreation
import py.AddingData as AddingData
import py.StartWindow
import py.res_rc
import py.LoadingDB as LoadingDB
import py.SyncDB as SyncDB
import py.PrintList as PrintList
import py.Change as Change
from py.waitingspinnerwidget import QtWaitingSpinner

if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

version = 'v 1.6'  # Версия программы
hide_password = True  # Показазь или скрыть пароли при запуске программы: True - скрыты / False - показанны
buffer_del_sec = 10  # Через сколько секунд будет удаляться буфер обмена после копирования пароля
new_rsa_bit = 4096  # Длина rsa ключа при создании новой базы (1024 / 2048 / 3072 / 4096)

db_dir = str()
db_name = None
pwd = None

buffer = None
choise_pubkey = None
choise_privkey = None
result_check_choise_privkey = None
result_check_choise_pubkey = None

srt_section = list()
cur = None
conn = None
privkey_dir = None


def show_msg(title="Сообщение",
             top_text="TopText",
             bottom_text="BottomText",
             window_type="Information",
             buttons="yes_no") -> int:
    """
    Создание и вывод окна.
    :param title: заголовок окна
    :param top_text: текст вверху
    :param bottom_text: текст внизу
    :param window_type: тип выводимого окна (Information, Warning, Critical)
    :param buttons: какие кнопки выводить
    :return: статус после закрытия окна
    """
    msg = QMessageBox()
    msg_icon = QtGui.QIcon()
    msg_icon.addPixmap(QtGui.QPixmap(":/resource/image/key.ico"))
    msg.setWindowIcon(msg_icon)
    if window_type == 'Information':
        msg.setIcon(QMessageBox.Information)
    elif window_type == 'Warning':
        msg.setIcon(QMessageBox.Warning)
    elif window_type == 'Critical':
        msg.setIcon(QMessageBox.Critical)
    if top_text == "TopText":
        pass
    else:
        msg.setText(top_text)
    if bottom_text == "BottomText":
        pass
    else:
        msg.setInformativeText(bottom_text)
    msg.setWindowTitle(title)
    if buttons == 'yes_no':
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    elif buttons == 'yes':
        msg.setStandardButtons(QMessageBox.Yes)
    elif buttons == 'ok':
        msg.setStandardButtons(QMessageBox.Ok)
    result = msg.exec_()
    return result


def record_change_time(cursor: sqlite3.Cursor, row: tuple, change_type: str) -> bool:
    """
    Записывает время изменения данных в БД.
    :param cursor: курсор текущего соединения
    :param row: кортеж значений из выделеной строки
    :param change_type: что меняем
    :return: результат выполнения True/False
    """
    try:
        acc_id = cursor.execute("""SELECT id
                                   FROM account_information
                                   WHERE name = ? AND
                                           login = ? AND
                                           email = ? AND
                                           url = ? """, (row[0][0], row[0][1], row[0][3], row[0][5])).fetchall()[0][0]
        cursor.execute(f"""UPDATE data_change_time
                           SET update_account = ?,
                               {change_type} = ?
                           WHERE id={acc_id}""", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        return True
    except sqlite3.Error:
        return False


class PrintThread(QtCore.QThread):
    def __init__(self, toolButton, treeWidget, pl, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.toolButton = toolButton
        self.treeWidget = treeWidget
        self.pl = pl

    def run(self):
        conn_t1 = sqlite3.connect(db_dir)
        cur_t1 = conn_t1.cursor()
        cur_t1.execute("PRAGMA key = '{}'".format(pwd))

        with open('{}_privkey.pem'.format(self.toolButton.text()[:-12]), 'rb') as privfile:
            keydata_priv = privfile.read()
            privfile.close()
        privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')

        data = []
        treewidget_item_count = 0
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item.text(0) == '':
                data.append([item.text(1)])
                for i in range(2, 7):
                    if item.text(i) == 'None':
                        data[-1].append('')
                    elif i == 3 and item.text(i) == '**********':
                        data3_item = cur_t1.execute(
                            "SELECT pass FROM account_information WHERE name='{}' AND login='{}' AND email='{}' AND url='{}'".format(
                                item.text(1), item.text(2), item.text(4), item.text(6))).fetchall()
                        password_bin = (data3_item[0][0]).encode()
                        password_dec = base64.b64decode(password_bin)
                        decrypto = rsa.decrypt(password_dec, privkey)
                        password = decrypto.decode()
                        data[-1].append(password)
                    elif i == 5 and item.text(i) == '**********':
                        data5_item = cur_t1.execute(
                            "SELECT secret_word FROM account_information WHERE name='{}' AND login='{}' AND email='{}' AND url='{}'".format(
                                item.text(1), item.text(2), item.text(4), item.text(6))).fetchall()
                        secret_bin = (data5_item[0][0]).encode()
                        secret_dec = base64.b64decode(secret_bin)
                        decrypto = rsa.decrypt(secret_dec, privkey)
                        secret = decrypto.decode()
                        if secret == 'None':
                            data[-1].append('')
                        else:
                            data[-1].append(secret)
                    else:
                        data[-1].append(item.text(i))
            if item.parent():
                if item.parent():
                    treewidget_item_count += 1
            else:
                treewidget_item_count += 1
            iterator += 1
        self.pl.data = data

        columnWidths = []
        for i in range(1, self.treeWidget.headerItem().columnCount()):
            columnWidths.append(180)
        self.pl.columnWidths = columnWidths

        headers = []
        for i in range(1, self.treeWidget.headerItem().columnCount()):
            item = self.treeWidget.headerItem().text(i)
            headers.append(item)
        self.pl.headers = headers

        cur_t1.close()
        conn_t1.close()


class ShowPassThread(QtCore.QThread):
    response = QtCore.pyqtSignal(dict)

    def __init__(self, acc_secret_info, privkey):
        super().__init__()
        self.acc_secret_info = acc_secret_info
        self.privkey = privkey

    def run(self):
        acc_secret_info_result = dict()
        for _key, _value in self.acc_secret_info.items():
            password_bin = (_value[0]).encode()
            password_dec = base64.b64decode(password_bin)
            try:
                decrypto = rsa.decrypt(password_dec, self.privkey)
                password = decrypto.decode()
            except rsa.pkcs1.DecryptionError:
                password = '##ERRORPUBKEY##'

            secret_word_bin = (_value[1]).encode()

            secret_word_dec = base64.b64decode(secret_word_bin)
            try:
                decrypto_secret = rsa.decrypt(secret_word_dec, self.privkey)
                secret_word = decrypto_secret.decode()
            except rsa.pkcs1.DecryptionError:
                secret_word = '##ERRORPUBKEY##'
            acc_secret_info_result[_key] = password, secret_word
        self.response.emit(acc_secret_info_result)


def connect_sql(start_or_load=None):  # TODO: убрать глобалы и должна возвращать sqlite3.connect
    global conn
    global cur
    global rsa_length
    conn = sqlite3.connect(db_dir)
    cur = conn.cursor()
    if start_or_load == 'load':
        cur.execute("PRAGMA key = '{}'".format(pwd))
    else:
        cur.execute("PRAGMA key = '{}'".format(pwd))
    rsa_bit = cur.execute("SELECT value FROM db_information WHERE name='rsa_bit'").fetchone()[0]
    if rsa_bit == 4096:  # TODO: Отдельная функция input->rsa_bit / output->rsa_length
        rsa_length = 684
    elif rsa_bit == 3072:
        rsa_length = 512
    elif rsa_bit == 2048:
        rsa_length = 344
    elif rsa_bit == 1024:
        rsa_length = 172
    else:
        rsa_length = 'error'


class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.create_db = None
        self.loading_db = None
        self.addingdata = None
        self.sdb = None
        self.timer = None
        self.timer_sec = None
        self.step = None
        self.show_pass_thread = None
        self.print_thread = None
        self.acc_info_list = list()
        self.acc_secret_info_result = dict()
        lines = 0
        self.pubkey_file = os.path.isfile("data/{}_pubkey.pem".format(
            db_name[:-3]))  # True если есть в директории data/   если нету False
        self.privkey_file = os.path.isfile("data/{}_privkey.pem".format(
            db_name[:-3]))  # True если есть в директории data/   если нету False

    def setupUi(self, MainWindow):
        MainWindow.resize(870, 600)
        MainWindow.setMinimumSize(QtCore.QSize(870, 600))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 5)

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setMinimumSize(QtCore.QSize(152, 23))
        self.gridLayout.addWidget(self.pushButton_2, 1, 4, 1, 1)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setMinimumSize(QtCore.QSize(152, 23))
        self.gridLayout.addWidget(self.pushButton_3, 2, 3, 1, 1)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setMinimumSize(QtCore.QSize(152, 23))
        self.gridLayout.addWidget(self.pushButton, 2, 4, 1, 1)

        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
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

        self.gridLayout.addWidget(self.treeWidget, 3, 0, 1, 5)

        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setMinimumSize(QtCore.QSize(152, 23))
        self.gridLayout.addWidget(self.pushButton_4, 1, 3, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setMinimumSize(QtCore.QSize(152, 23))
        self.gridLayout.addWidget(self.pushButton_5, 1, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.label_2, 4, 4, 1, 1)
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.toolButton_2 = QtWidgets.QToolButton(self.centralwidget)
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
        icon.addPixmap(QtGui.QPixmap(":/resource/image/cross.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/resource/image/checkmark.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.toolButton_2.setIcon(icon)
        self.toolButton_2.setAutoRepeat(False)
        self.toolButton_2.setAutoExclusive(False)
        self.toolButton_2.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolButton_2.setAutoRaise(True)
        self.toolButton_2.setObjectName("toolButton_2")
        self.gridLayout.addWidget(self.toolButton_2, 1, 0, 1, 2)
        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.toolButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resource/image/cross.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/resource/image/checkmark.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolButton.setAutoRaise(True)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 2, 0, 1, 2)
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
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_3.setIcon(QtGui.QIcon('resource/image/save.ico'))
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_4.setIcon(QtGui.QIcon('resource/image/add_db.ico'))
        self.action_5 = QtWidgets.QAction(MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_5.setIcon(QtGui.QIcon('resource/image/search_db.ico'))
        self.action_6 = QtWidgets.QAction(MainWindow)
        self.action_6.setObjectName("action_6")
        self.action_6.setIcon(QtGui.QIcon('resource/image/sync_db.ico'))
        self.action_6.setEnabled(False)
        self.action_7 = QtWidgets.QAction(MainWindow)
        self.action_7.setObjectName("action_6")
        self.action_7.setIcon(QtGui.QIcon('resource/image/print.ico'))
        self.action_8 = QtWidgets.QAction(MainWindow)
        self.action_8.setObjectName("action_7")
        self.action_8.setIcon(QtGui.QIcon('resource/image/exit.ico'))
        self.menu.addAction(self.action_3)
        self.menu.addAction(self.action_4)
        self.menu.addAction(self.action_5)
        self.menu.addAction(self.action_6)
        self.menu.addAction(self.action_7)
        self.menu.addSeparator()
        self.menu.addAction(self.action_8)
        self.menubar.addAction(self.menu.menuAction())

        MainWindow.setWindowIcon(QtGui.QIcon('resource/image/key.ico'))

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 1)
        self.progressBar.hide()
        self.statusbar.addPermanentWidget(self.progressBar)
        self.statusbar.addPermanentWidget(self.label_2)

        self.spinner = QtWaitingSpinner(self, centerOnParent=True, disableParentWhenSpinning=True)
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

        self.result_check_privkey()
        self.result_check_pubkey()

        if hide_password:
            self.pushButton_4.hide()
        else:
            self.pushButton_5.hide()

        self.button_state()

        if not self.toolButton.isEnabled() and not self.toolButton_2.isEnabled():
            self.action_6.setEnabled(True)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.action_3.triggered.connect(self.save_db)
        self.action_4.triggered.connect(self.show_create_db)
        self.action_5.triggered.connect(self.show_load_db)
        self.action_6.triggered.connect(self.sync_db)
        self.action_7.triggered.connect(self.print)
        self.action_8.triggered.connect(self.close)
        self.pushButton.clicked.connect(self.delete_data)
        self.pushButton_2.clicked.connect(self.show_addingdata)
        self.pushButton_3.clicked.connect(self.show_hide_all_sections)
        self.pushButton_4.clicked.connect(self.password_hide)
        self.pushButton_5.clicked.connect(self.password_show)
        self.toolButton.clicked.connect(self.choise_privkey)
        self.toolButton_2.clicked.connect(self.choise_pubkey)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextuelAlbum)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Password Saver - Главная | {}".format(db_name)))
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
        self.pushButton_3.setText(_translate("MainWindow", "Развернуть все разделы"))
        self.pushButton.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        self.pushButton_4.setText(_translate("MainWindow", "Скрыть пароли"))
        self.pushButton_5.setText(_translate("MainWindow", "Показать пароли"))
        self.label_2.setText(_translate("MainWindow", "{}".format(version)))
        if self.pubkey_file and result_check_pubkey == 'ok':
            self.toolButton_2.setText(_translate("MainWindow", pubkey_dir))
        elif self.pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_2.setText(_translate("MainWindow", 'Ключ не подходит. Укажите pubkey.pem'))
        elif self.pubkey_file and result_check_pubkey is None:
            self.toolButton_2.setText(_translate("MainWindow", pubkey_dir))
        elif self.pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_2.setText(_translate("MainWindow", 'Сначало укажите privkey.pem'))
        else:
            self.toolButton_2.setText(_translate("MainWindow", "Укажите pubkey.pem"))

        if self.privkey_file and result_check_privkey == 'ok':
            global privkey_dir
            privkey_dir = os.path.abspath("data/{}_privkey.pem".format(db_name[:-3]))
            self.toolButton.setText(_translate("MainWindow", privkey_dir))
        elif self.privkey_file and result_check_privkey == '!ok':
            self.toolButton.setText(_translate("MainWindow", "Ключ не подходит. Укажите privkey.pem"))
        elif self.privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton.setText(_translate("MainWindow", "Ключи разные. Укажите правильный privkey.pem"))
            self.toolButton_2.setText(_translate("MainWindow", "Ключи разные. Укажите правильный pubkey.pem"))
        elif self.privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton.setText(_translate("MainWindow", "Сначало укажите pubkey.pem"))
        else:
            self.toolButton.setText(_translate("MainWindow", "Укажите privkey.pem"))

        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.action.setText(_translate("MainWindow", "Выход"))
        self.action_3.setText(_translate("MainWindow", "Сохранить"))
        self.action_4.setText(_translate("MainWindow", "Создать новую БД"))
        self.action_5.setText(_translate("MainWindow", "Загрузить БД"))
        self.action_6.setText(_translate("MainWindow", "Синхронизировать с БД"))
        self.action_7.setText(_translate("MainWindow", "Печать"))
        self.action_8.setText(_translate("MainWindow", "Выход"))
        self.progressBar.setFormat(_translate("MainWindow", ""))

    @QtCore.pyqtSlot()
    def print(self):
        if not self.toolButton.isEnabled():
            pl = PrintList.PrintList()
            layout = QtGui.QPageLayout(QtGui.QPageSize(QtGui.QPageSize.A4),
                                       QtGui.QPageLayout.Landscape,
                                       QtCore.QMarginsF(5, 5, 5, 5),
                                       units=QtGui.QPageLayout.Millimeter)
            pl.printer.setPageLayout(layout)
            pd = QtPrintSupport.QPrintDialog(pl.printer, parent=None)
            result = pd.exec_()

            if result == 1:
                self.print_thread = PrintThread(toolButton=self.toolButton, treeWidget=self.treeWidget, pl=pl)
                self.print_thread.started.connect(self.print_spinner_started)
                self.print_thread.finished.connect(lambda: self.print_spinner_finished(pl=self.print_thread.pl))
                self.print_thread.start()
        else:
            show_msg(title='Нельзя распечатать',
                     top_text='Сначало укажите privkey.pem',
                     window_type='Critical',
                     buttons='ok')

    @QtCore.pyqtSlot()
    def print_spinner_started(self):
        self.spinner.start()
        self.statusbar.showMessage("Готовлюсь к печати...")

    @QtCore.pyqtSlot()
    def print_spinner_finished(self, pl):
        pl.printData()
        self.spinner.stop()
        self.statusbar.showMessage("Печать завершена.")

    @QtCore.pyqtSlot()
    def show_pass_spinner_started(self):
        self.spinner.start()
        self.statusbar.showMessage("Расшифровываю пароли...")

    @QtCore.pyqtSlot()
    def show_pass_spinner_finished(self):
        section_iter = 0
        for _data_section in self.acc_info_list:
            item_iter = 0
            for _data_item in _data_section:
                if _data_item[1] in self.acc_secret_info_result:
                    self.treeWidget.topLevelItem(section_iter).child(item_iter).setText(
                        3, self.acc_secret_info_result[_data_item[1]][0])
                item_iter += 1
            section_iter += 1

        self.pushButton_5.hide()
        self.pushButton_4.show()
        self.acc_info_list.clear()
        self.spinner.stop()
        self.statusbar.showMessage("Пароли расшифрованы.", msecs=10000)

    def show_pass_response(self, acc_secret_info_result):
        self.acc_secret_info_result = acc_secret_info_result

    @QtCore.pyqtSlot()
    def save_db(self):
        result = show_msg(title='Сохранение изменений',
                          top_text='Вы действительно хотите сохранить изменения в базе данных?'
                          )
        if result == QMessageBox.Yes:
            conn.commit()
            show_msg(title='Password Saver',
                     top_text='База данных сохранена',
                     buttons='ok')
        elif result == QMessageBox.No:
            pass

    @QtCore.pyqtSlot()
    def show_create_db(self):
        self.create_db = DatabaseCreation.CreateDB()
        self.create_db.exec_()

    @QtCore.pyqtSlot()
    def show_load_db(self):
        self.loading_db = LoadingDB.LoadingDB()
        self.loading_db.exec()
        if not py.LoadingDB.Close:
            py.LoadingDB.Close = True
            self.pubkey_file = os.path.isfile("data/{}_pubkey.pem".format(
                db_name[:-3]))
            self.privkey_file = os.path.isfile("data/{}_privkey.pem".format(
                db_name[:-3]))
            self.refresh_treewidget()
            self.result_check_privkey()
            self.result_check_pubkey()
            self.button_state()
            self.retranslateUi(self)

    @QtCore.pyqtSlot()
    def sync_db(self):
        self.sdb = SyncDB.SyncDB(self.toolButton.text(), self.toolButton_2.text())
        self.sdb.exec()
        if py.SyncDB.finish_sync:
            py.SyncDB.finish_sync = False
            self.refresh_treewidget()

    @QtCore.pyqtSlot()
    def show_addingdata(self):
        global hide_password
        if not hide_password:
            self.password_hide()
        self.addingdata = AddingData.AddingData()
        self.addingdata.exec_()
        self.refresh_treewidget()

        if lines != 0 and self.privkey_file and result_check_privkey == 'ok' or lines != 0 and result_check_choise_privkey == 'ok':
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
        elif lines != 0 and self.privkey_file and result_check_privkey == '!ok' or lines != 0 and result_check_choise_privkey == '!ok':
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
        elif lines == 0:
            self.pushButton.setEnabled(False)
        else:
            self.pushButton.setEnabled(True)

        if py.AddingData.checkbox_pass is True:
            self.delete_buffer()
            py.AddingData.checkbox_pass = False

    @QtCore.pyqtSlot()
    def show_hide_all_sections(self):
        __text = self.pushButton_3.text()
        if __text == 'Развернуть все разделы':
            self.treeWidget.expandAll()
            self.pushButton_3.setText('Свернуть все разделы')
        else:
            self.treeWidget.collapseAll()
            self.pushButton_3.setText('Развернуть все разделы')

    @QtCore.pyqtSlot()
    def copy_buffer(self):
        global buffer
        row = self.current_row()
        if row[1] == 'item_1':
            buffer = QtWidgets.QApplication.clipboard()
            if buffer is not None:
                data_one_section = cur.execute(
                    "SELECT pass FROM account_information WHERE name='{}' AND login='{}' AND email='{}' AND url='{}'".format(
                        row[0][0], row[0][1], row[0][3], row[0][5])).fetchall()
                if choise_privkey is not None:
                    privkey = choise_privkey
                else:
                    with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                        keydata_priv = privfile.read()
                        privfile.close()
                    privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                password_bin = data_one_section[0][0].encode()
                password_dec = base64.b64decode(password_bin)
                decrypto = rsa.decrypt(password_dec, privkey)
                password = decrypto.decode()
                buffer.setText(password)
                self.delete_buffer()

    @QtCore.pyqtSlot()
    def delete_data(self):
        row = self.current_row()
        if row[1] == 'item_0 first' or row[1] == 'item_0':
            show_msg(title='Ошибка',
                     top_text='Нельзя удалить раздел.',
                     bottom_text='Если хотите удалить раздел, то удалите все аккаунты в нём.',
                     window_type='Critical',
                     buttons='ok'
                     )
        elif row[1] == 'item_1':
            result = show_msg(title='Удаление аккаунта',
                              top_text=f'Данные аккаунта <b>{row[0][0]}</b> с логином <b>{row[0][1]}</b> будут удалены',
                              bottom_text='Вы уверенны?'
                              )
            if result == QMessageBox.Yes:
                acc_id = cur.execute("""SELECT id
                                        FROM account_information
                                        WHERE name = ? AND
                                              login = ? AND
                                              email = ? AND
                                              url = ? """,
                                     (row[0][0], row[0][1], row[0][3], row[0][5])).fetchall()[0][0]
                cur.execute("""DELETE FROM data_change_time WHERE id = ?""", (str(acc_id),))
                cur.execute("""DELETE FROM account_information
                               WHERE name = ? AND
                                     login = ? AND
                                     email = ? AND
                                     url = ? """,
                            (row[0][0], row[0][1], row[0][3], row[0][5]))
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

        if lines != 0:
            if choise_privkey is not None:
                privkey = choise_privkey
            else:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')

            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(
                    srt_section[_data_section])).fetchall()
                acc_info = []
                for _item in data_one_section:
                    acc_info.append(list(_item[2:]))

                self.acc_info_list.append(acc_info)

            __acc_secret_info = dict()
            for _data_section in self.acc_info_list:
                for _data_item in _data_section:
                    __acc_secret_info[_data_item[1]] = _data_item[2], _data_item[4]

            self.show_pass_thread = ShowPassThread(__acc_secret_info, privkey)
            self.show_pass_thread.started.connect(self.show_pass_spinner_started)
            self.show_pass_thread.response.connect(self.show_pass_response)
            self.show_pass_thread.finished.connect(self.show_pass_spinner_finished)
            self.show_pass_thread.start()

    @QtCore.pyqtSlot()
    def password_hide(self):
        global hide_password
        hide_password = True
        top_level_item_iter = -1
        if lines != 0:
            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(
                    srt_section[_data_section])).fetchall()
                acc_info = []
                for item in data_one_section:
                    acc_info.append(item[2:])
                self.treeWidget.topLevelItem(_data_section).setText(0, str(srt_section[_data_section]))
                top_level_item_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if text_iter == 3:
                            self.treeWidget.topLevelItem(top_level_item_iter).child(child_iter).setText(text_iter,
                                                                                                        '**********')
        self.pushButton_4.hide()
        self.pushButton_5.show()

    @QtCore.pyqtSlot()
    def choise_pubkey(self):
        global choise_pubkey
        global result_check_choise_pubkey
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Укажите публичный ключ-файл (.pem)',
            os.getcwd(),
            '{}_pubkey.pem;;*_pubkey.pem'.format(db_name[:-3])
        )
        if directory_name[0] != '' and directory_name[1] != '':
            with open(directory_name[0], 'rb') as pubfile:
                keydata_pub = pubfile.read()
                pubfile.close()
            choise_pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
            self.toolButton_2.setEnabled(False)
            self.toolButton_2.setText(directory_name[0])
            self.pushButton_2.setEnabled(True)

            if not self.toolButton.isEnabled():
                try:
                    with open(self.toolButton.text(), 'rb') as privfile:
                        keydata_priv = privfile.read()
                        privfile.close()
                    selftest_privfile = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                    chars = string.ascii_letters + string.digits
                    rnd_text = ''.join(random.choice(chars) for x in range(20))
                    rnd_text = rnd_text.encode()
                    crypto_text = rsa.encrypt(rnd_text, choise_pubkey)
                    selftest_decrypto = rsa.decrypt(crypto_text, selftest_privfile)
                    result_check_choise_pubkey = 'ok'
                    self.action_6.setEnabled(True)
                except rsa.pkcs1.DecryptionError:
                    self.toolButton_2.setEnabled(True)
                    self.toolButton_2.setText('Опять неправильный. Укажите pubkey.pem')
                    self.pushButton_2.setEnabled(False)
                    result_check_choise_pubkey = '!ok'

    @QtCore.pyqtSlot()
    def choise_privkey(self):
        global choise_privkey
        global result_check_choise_privkey
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None,
            'Укажите приватный ключ-файл (.pem)',
            os.getcwd(),
            '{}_privkey.pem;;*_privkey.pem'.format(db_name[:-3])
        )
        if directory_name[0] != '' and directory_name[1] != '':
            with open(directory_name[0], 'rb') as privfile:
                keydata_priv = privfile.read()
                privfile.close()
            choise_privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            if lines != 0:
                try:
                    first_pass = cur.execute("SELECT pass FROM account_information ORDER BY ID ASC LIMIT 1")
                    first_pass = cur.fetchall()
                    password_bin = (first_pass[0][0]).encode()
                    password_dec = base64.b64decode(password_bin)
                    decrypto = rsa.decrypt(password_dec, choise_privkey)
                    password = decrypto.decode()
                    result_check_choise_privkey = 'ok'
                except rsa.pkcs1.DecryptionError:
                    result_check_choise_privkey = '!ok'
                if result_check_choise_privkey == 'ok':
                    self.toolButton.setEnabled(False)
                    self.toolButton.setText(directory_name[0])
                    self.pushButton_5.setEnabled(True)
                    self.pushButton_4.setEnabled(True)
                    self.pushButton_3.setEnabled(True)
                    if not self.toolButton_2.isEnabled():
                        try:
                            with open(self.toolButton_2.text(), 'rb') as pubfile:
                                keydata_pub = pubfile.read()
                                pubfile.close()
                            selftest_pubfile = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                            chars = string.ascii_letters + string.digits
                            rnd_text = ''.join(random.choice(chars) for x in range(20))
                            rnd_text = rnd_text.encode()
                            crypto_text = rsa.encrypt(rnd_text, selftest_pubfile)
                            selftest_decrypto = rsa.decrypt(crypto_text, choise_privkey)
                            self.action_6.setEnabled(True)
                        except rsa.pkcs1.DecryptionError:
                            self.toolButton_2.setEnabled(True)
                            self.toolButton_2.setText('Ключ неправильный. Укажите pubkey.pem')
                            self.pushButton_2.setEnabled(False)

                elif result_check_choise_privkey == '!ok':
                    self.toolButton.setText('Ключ не подходит. Выберете правильный privkey')

            elif lines == 0:
                self.toolButton.setEnabled(False)
                self.toolButton.setText(directory_name[0])
                result_check_choise_privkey = 'ok'
                if not self.toolButton_2.isEnabled():
                    self.action_6.setEnabled(True)

    def result_check_privkey(self):
        global result_check_privkey
        if lines != 0 and self.privkey_file:
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
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
            except rsa.pkcs1.DecryptionError:
                result_check_privkey = '!ok'
        elif lines == 0 and self.privkey_file and self.pubkey_file:
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(db_dir[:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for x in range(20))
                rnd_pass = rnd_pass.encode()
                crypto_pass = rsa.encrypt(rnd_pass, pubkey)
                decrypto = rsa.decrypt(crypto_pass, privkey)
                result_check_privkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                result_check_privkey = 'privkey != pubkey'
        elif lines == 0 and self.privkey_file and not self.pubkey_file:
            result_check_privkey = 'not pubkey'
        else:
            result_check_privkey = None

    def result_check_pubkey(self):
        global result_check_pubkey
        if self.pubkey_file and self.privkey_file and result_check_privkey == 'ok':
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(db_dir[:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for x in range(20))
                rnd_pass = rnd_pass.encode()
                crypto_pass = rsa.encrypt(rnd_pass, pubkey)
                decrypto = rsa.decrypt(crypto_pass, privkey)
                result_check_pubkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                result_check_pubkey = '!ok'
        else:
            result_check_pubkey = None

    def button_state(self):
        icon = QtGui.QIcon()
        icon1 = QtGui.QIcon()
        if self.pubkey_file and result_check_pubkey == 'ok':
            global pubkey_dir
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(db_name[:-3]))
            self.toolButton_2.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey is None:
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(db_name[:-3]))
            self.toolButton_2.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_2.setEnabled(False)
            icon.addPixmap(QtGui.QPixmap(":/resource/image/cross.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
            self.toolButton_2.setIcon(icon)
        else:
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)

        if self.privkey_file and result_check_privkey == 'ok':
            self.toolButton.setEnabled(False)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)
        elif self.privkey_file and result_check_privkey == '!ok':
            self.toolButton.setEnabled(True)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
        elif self.privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton.setEnabled(True)
            self.toolButton_2.setEnabled(True)
            self.pushButton_2.setEnabled(False)
        elif self.privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton.setEnabled(False)
            icon1.addPixmap(QtGui.QPixmap(":/resource/image/cross.ico"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
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

    def delete_buffer(self):
        global buffer_del_sec
        self.timer = QtCore.QBasicTimer()
        self.timer_sec = QtCore.QTimer()
        self.step = 0
        self.statusbar.showMessage("Данные будут удалены с буфера обмена через {} секунд".format(buffer_del_sec))
        timer_del = buffer_del_sec * 10
        if self.timer_sec.isActive():
            self.timer_sec.stop()
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(timer_del, self)
            self.progressBar.show()
            self.start_timer(self.timer_func, buffer_del_sec)

    def timerEvent(self, e):
        global buffer_del_sec
        if self.step >= 100:
            self.timer.stop()
            buffer.clear()
            self.statusbar.showMessage("Данные удалены с буфера обмена.")
            return
        else:
            self.step += 1
            self.progressBar.setValue(self.step)

    def start_timer(self, slot, count=0, interval=1000):
        global buffer_del_sec
        counter = buffer_del_sec

        def handler():
            nonlocal counter
            counter -= 1
            slot(counter)
            if counter >= count:
                self.timer_sec.stop()
                self.timer_sec.deleteLater()

        self.timer_sec.timeout.connect(handler)
        self.timer_sec.start(interval)

    def timer_func(self, count):
        global buffer_del_sec
        self.statusbar.showMessage("Данные будут удалены с буфера обмена через {} секунд".format(count))
        if count <= 0:
            self.timer_sec.stop()

    def menuContextuelAlbum(self, event):
        global buffer
        global result_check_privkey
        global result_check_pubkey
        row = self.current_row()
        if row[1] == 'item_1':
            self.menu_contextuelAlb = QtWidgets.QMenu(self.treeWidget)

            rsubmenu_copy_log = self.menu_contextuelAlb.addMenu("Копировать")
            rsubmenu_change_log = self.menu_contextuelAlb.addMenu("Изменить")
            rsubmenu_transfer_acc = self.menu_contextuelAlb.addMenu("Переместить в")

            rmenu_copy_log = rsubmenu_copy_log.addAction("Копировать логин")
            rmenu_copy_pass = rsubmenu_copy_log.addAction("Копировать пароль")
            rmenu_copy_email = rsubmenu_copy_log.addAction("Копировать почту")
            rmenu_copy_secret = rsubmenu_copy_log.addAction("Копировать секретное слово")
            rmenu_copy_url = rsubmenu_copy_log.addAction("Копировать url")

            if result_check_privkey == 'ok' or result_check_choise_privkey == 'ok':
                rmenu_copy_pass.setEnabled(True)
                rmenu_copy_secret.setEnabled(True)
            else:
                rmenu_copy_pass.setEnabled(False)
                rmenu_copy_secret.setEnabled(False)

            rmenu_change_log = rsubmenu_change_log.addAction("Изменить логин")
            rmenu_change_pass = rsubmenu_change_log.addAction("Изменить пароль")
            rmenu_change_email = rsubmenu_change_log.addAction("Изменить почту")
            rmenu_change_secret = rsubmenu_change_log.addAction("Изменить секретное слово")
            rmenu_change_url = rsubmenu_change_log.addAction("Изменить url")

            sect_list = []
            section = cur.execute("SELECT section FROM account_information GROUP BY section ORDER BY id").fetchall()
            for section_item in section:
                sect_list.append(rsubmenu_transfer_acc.addAction(section_item[0]))

            if not self.toolButton_2.isEnabled():
                rmenu_change_log.setEnabled(True)
                rmenu_change_pass.setEnabled(True)
                rmenu_change_email.setEnabled(True)
                rmenu_change_secret.setEnabled(True)
                rmenu_change_url.setEnabled(True)
            else:
                rmenu_change_log.setEnabled(False)
                rmenu_change_pass.setEnabled(False)
                rmenu_change_email.setEnabled(False)
                rmenu_change_secret.setEnabled(False)
                rmenu_change_url.setEnabled(False)

            action2 = self.menu_contextuelAlb.exec_(self.treeWidget.mapToGlobal(event))
            if action2 is not None:
                if action2 == rmenu_copy_log:
                    buffer = QtWidgets.QApplication.clipboard()
                    if buffer is not None:
                        buffer.setText(row[0][1])
                        self.delete_buffer()
                elif action2 == rmenu_copy_email:
                    buffer = QtWidgets.QApplication.clipboard()
                    if buffer is not None:
                        if row[0][3] == 'None':
                            show_msg(title='Ошибка',
                                     top_text='На этом аккаунте нету почты',
                                     window_type='Critical',
                                     buttons='ok')
                        else:
                            buffer.setText(row[0][3])
                            self.delete_buffer()
                elif action2 == rmenu_copy_url:
                    buffer = QtWidgets.QApplication.clipboard()
                    if buffer is not None:
                        if row[0][5] == 'None':
                            show_msg(title='Ошибка',
                                     top_text='На этом аккаунте не указан url',
                                     window_type='Critical',
                                     buttons='ok')
                        else:
                            buffer.setText(row[0][5])
                            self.delete_buffer()
                elif action2 == rmenu_copy_pass:
                    self.copy_buffer()
                elif action2 == rmenu_copy_secret:
                    buffer = QtWidgets.QApplication.clipboard()
                    if buffer is not None:
                        data_one_section = cur.execute(
                            "SELECT secret_word FROM account_information WHERE name='{}' AND login='{}' AND email='{}' AND url='{}'".format(
                                row[0][0], row[0][1], row[0][3], row[0][5])).fetchall()
                        if choise_privkey is not None:
                            privkey = choise_privkey
                        else:
                            with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                                keydata_priv = privfile.read()
                                privfile.close()
                            privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                        secret_bin = data_one_section[0][0].encode()
                        secret_dec = base64.b64decode(secret_bin)
                        decrypto = rsa.decrypt(secret_dec, privkey)
                        secret = decrypto.decode()
                        if secret == 'None':
                            show_msg(title='Ошибка',
                                     top_text='На этом аккаунте не указанно секретное слово',
                                     window_type='Critical',
                                     buttons='ok')
                        else:
                            buffer.setText(secret)
                            self.delete_buffer()
                elif action2 == rmenu_change_log:
                    self.change = Change.Change('Изменение логина', 'Введите новый логин', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        login = self.change.lineEdit.text()
                        if login != '':
                            record_change_time(cur, row, 'change_login')
                            cur.execute("""UPDATE account_information
                                           SET login = ?
                                           WHERE name = ? AND
                                                 login = ? AND
                                                 email = ? AND
                                                 url = ? """,
                                        (login, row[0][0], row[0][1], row[0][3], row[0][5]))
                            self.refresh_treewidget()
                        else:
                            show_msg(title='Ошибка',
                                     top_text='Нельзя изменить на пустой логин',
                                     window_type='Critical',
                                     buttons='ok')
                elif action2 == rmenu_change_pass:
                    self.change = Change.Change('Изменение пароля', 'Введите новый пароль', True)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        if self.change.lineEdit.text() == '':
                            show_msg(title='Ошибка',
                                     top_text='Нельзя изменить на пустой пароль',
                                     window_type='Critical',
                                     buttons='ok')
                        else:
                            if not self.toolButton_2.isEnabled():
                                path_to_pubkey = self.toolButton_2.text()
                            else:
                                path_to_pubkey = f"{db_dir[:-3]}_pubkey.pem"
                            with open(path_to_pubkey, 'rb') as pubfile:
                                keydata_pub = pubfile.read()
                                pubfile.close()
                            pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                            pass_bin = self.change.lineEdit.text().encode()
                            crypto_pass = rsa.encrypt(pass_bin, pubkey)
                            password = base64.b64encode(crypto_pass).decode()
                            record_change_time(cur, row, 'change_pass')
                            cur.execute("""UPDATE account_information
                                           SET pass = ?
                                           WHERE name = ? AND
                                                 login = ? AND
                                                 email = ? AND
                                                 url= ? """,
                                        (password, row[0][0], row[0][1], row[0][3], row[0][5]))
                            self.refresh_treewidget()
                elif action2 == rmenu_change_email:
                    self.change = Change.Change('Изменение почты', 'Введите новую почту', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        email = self.change.lineEdit.text()
                        if email == '':
                            email = None
                        record_change_time(cur, row, 'change_email')
                        cur.execute("""UPDATE account_information
                                       SET email = ?
                                       WHERE name = ? AND
                                             login = ? AND
                                             email = ? AND
                                             url = ? """,
                                    (email, row[0][0], row[0][1], row[0][3], row[0][5]))
                        self.refresh_treewidget()
                elif action2 == rmenu_change_secret:
                    self.change = Change.Change('Изменение секретного слова', 'Введите новое секретное слово', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        secret_text = self.change.lineEdit.text()
                        if secret_text == '':
                            secret_text = 'None'
                        if not self.toolButton_2.isEnabled():
                            path_to_pubkey = self.toolButton_2.text()
                        else:
                            path_to_pubkey = f"{db_dir[:-3]}_pubkey.pem"
                        with open(path_to_pubkey, 'rb') as pubfile:
                            keydata_pub = pubfile.read()
                            pubfile.close()
                        pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                        secret_bin = secret_text.encode()
                        crypto_secret = rsa.encrypt(secret_bin, pubkey)
                        secret = base64.b64encode(crypto_secret).decode()
                        record_change_time(cur, row, 'change_secret_word')
                        cur.execute("""UPDATE account_information
                                       SET secret_word = ?
                                       WHERE name = ? AND
                                             login = ? AND
                                             email = ? AND
                                             url = ? """,
                                    (secret, row[0][0], row[0][1], row[0][3], row[0][5]))
                        self.refresh_treewidget()
                elif action2 == rmenu_change_url:
                    self.change = Change.Change('Изменение url', 'Введите новый url', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        url = self.change.lineEdit.text()
                        if url == '':
                            url = None
                        record_change_time(cur, row, 'change_url')
                        cur.execute("""UPDATE account_information
                                       SET url = ?
                                       WHERE name = ? AND
                                             login = ? AND
                                             email = ? AND
                                             url = ? """,
                                    (url, row[0][0], row[0][1], row[0][3], row[0][5]))
                        self.refresh_treewidget()

                for item_type in sect_list:
                    if action2 is not None and action2 == item_type:
                        record_change_time(cur, row, 'change_section')
                        cur.execute("""UPDATE account_information
                                       SET section = ?
                                       WHERE name = ? AND
                                             login = ? AND
                                             email = ? AND
                                             url = ? """,
                                    (item_type.text(), row[0][0], row[0][1], row[0][3], row[0][5]))
                        self.refresh_treewidget()

    def add_treewidget_item(self):
        global lines
        [lines], = cur.execute("SELECT Count(*) FROM account_information")
        global amount_item_0
        amount_item_0 = 0
        amount_item_1 = lines
        section = []
        if lines != 0:
            for _line in range(1, lines + 1):
                [_current_id], = cur.execute("SELECT ID FROM account_information LIMIT 1 OFFSET {}".format(_line - 1))
                [_current_section], = cur.execute(
                    "SELECT section FROM account_information WHERE ID='{}'".format(_current_id))
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
                    data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(
                        srt_section[_data_section])).fetchall()
                else:
                    data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(
                        srt_section[_data_section])).fetchall()
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

            if self.privkey_file:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            elif choise_privkey:
                privkey = choise_privkey

            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("SELECT * FROM account_information WHERE section='{}'".format(
                    srt_section[_data_section])).fetchall()
                acc_info = []
                for item in data_one_section:
                    acc_info.append(item[2:])
                exec('self.treeWidget.topLevelItem(%d).setText(0, _translate("MainWindow", "%s"))' % (
                    _data_section, srt_section[_data_section]))
                toplevelitem_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if (text_iter == 3 and hide_password) or (text_iter == 5 and hide_password):
                            exec(
                                'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                toplevelitem_iter, child_iter, text_iter, '**********'))
                        elif _value is None:
                            value = None
                            exec(
                                'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                    toplevelitem_iter, child_iter, text_iter, value))
                        elif len(_value) == rsa_length:
                            value_bin = _value.encode()
                            value_dec = base64.b64decode(value_bin)
                            try:
                                decrypto_value = rsa.decrypt(value_dec, privkey)
                                value = decrypto_value.decode()
                                exec(
                                    'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                    toplevelitem_iter, child_iter, text_iter, value))
                            except rsa.pkcs1.DecryptionError:
                                value = '##ERRORPUBKEY##'
                                exec(
                                    'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                    toplevelitem_iter, child_iter, text_iter, value))
                        elif (text_iter == 3 and rsa_length == 'error') or (text_iter == 5 and rsa_length == 'error'):
                            value = '##ERRORKEYLENGTH##'
                            exec(
                                'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                toplevelitem_iter, child_iter, text_iter, value))
                        else:
                            exec(
                                'self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (
                                toplevelitem_iter, child_iter, text_iter, _value))

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
        close = show_msg(title='Выход',
                         top_text='Все несохраненные изменения будут потеряны.\n\n'
                                  'Все ровно выйти?')
        if close == QtWidgets.QMessageBox.Yes:
            if buffer is not None:
                buffer.clear()
            cur.close()
            conn.close()
            event.accept()
        else:
            event.ignore()
