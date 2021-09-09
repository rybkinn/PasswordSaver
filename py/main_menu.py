#!/usr/bin/env python3
import os.path
import base64
import random
import string
import datetime
import rsa
from sys import platform

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtPrintSupport

import py.res_rc    # required for loading resource files. Do not delete
import py.database_creation as database_creation
import py.adding_data as adding_data
import py.loading_db as loading_db
import py.sync_db as sync_db
import py.print_list as print_list
import py.change as change
import py.ui.main_menu_ui as main_menu_ui
from py.show_msg import show_msg
from py.spinner_widget import QtWaitingSpinner

if platform == "linux" or platform == "linux2":
    from pysqlcipher3 import dbapi2 as sqlite3
elif platform == "win32":
    import sqlite3
# elif platform == "darwin":
    # OS X

# Version program
VERSION = 'v 1.6.4'
# Show or hide passwords when starting the program
HIDE_PASSWORD = True
# How many seconds will the clipboard be deleted after copying the password
BUFFER_DEL_SEC = 10
# Rsa key length when creating a new base (1024/2048/3072/4096)
NEW_RSA_BIT = 4096

rsa_length = int()
db_dir = str()
db_name = None
pwd = None

lines = None
amount_item_0 = 0

buffer = None
choice_pubkey = None
choice_privkey = None
result_check_choice_privkey = None
result_check_choice_pubkey = None
result_check_privkey = None
result_check_pubkey = None
pubkey_dir = None
privkey = None

srt_section = list()
privkey_dir = None
cur = None
conn = None


def record_change_time(cursor: sqlite3.Cursor,
                       row: tuple,
                       change_type: str
                       ) -> bool:
    """
    Records the time of data change in the database.

    :param cursor: current cursor
    :param row: a tuple of values from the selected row
    :param change_type: what changing
    :return: execution result
    """
    try:
        acc_id = cursor.execute("""SELECT id
                                   FROM account_information
                                   WHERE name = ? AND
                                           login = ? AND
                                           email = ? AND
                                           url = ? """, (row[0][0],
                                                         row[0][1],
                                                         row[0][3],
                                                         row[0][5])
                                ).fetchall()[0][0]
        cursor.execute(f"""UPDATE data_change_time
                           SET update_account = ?,
                               {change_type} = ?
                           WHERE id={acc_id}""",
                       (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        return True
    except sqlite3.Error as sqlite_error:
        show_msg(title='Ошибка',
                 top_text='Ошибка выполнения record_change_time()',
                 bottom_text=str(sqlite_error),
                 window_type='critical',
                 buttons='ok')
        return False


class PrintThread(QtCore.QThread):
    def __init__(self, tool_button, tree_widget, pl, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.toolButton = tool_button
        self.treeWidget = tree_widget
        self.pl = pl

    def run(self):
        conn_print_thread = sqlite3.connect(db_dir)
        cur_print_thread = conn_print_thread.cursor()
        cur_print_thread.execute("PRAGMA key = '{}'".format(pwd))

        with open('{}_privkey.pem'.format(self.toolButton.text()[:-12]), 'rb') \
                as privfile:
            keydata_priv = privfile.read()
            privfile.close()
        privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')

        data = []
        tree_widget_item_count = 0
        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item.text(0) == '':
                data.append([item.text(1)])
                for index in range(2, 7):
                    if item.text(index) == 'None':
                        data[-1].append('')
                    elif index == 3 and item.text(index) == '**********':
                        data3_item = cur_print_thread.execute("""
                        SELECT pass
                        FROM account_information
                        WHERE name='{}' AND
                              login='{}' AND
                              email='{}' AND
                              url='{}'""".format(item.text(1),
                                                 item.text(2),
                                                 item.text(4),
                                                 item.text(6))).fetchall()
                        password_bin = (data3_item[0][0]).encode()
                        password_dec = base64.b64decode(password_bin)
                        decrypto = rsa.decrypt(password_dec, privkey)
                        password = decrypto.decode()
                        data[-1].append(password)
                    elif index == 5 and item.text(index) == '**********':
                        data5_item = cur_print_thread.execute("""
                        SELECT secret_word
                        FROM account_information
                        WHERE name='{}' AND
                              login='{}' AND
                              email='{}' AND
                              url='{}'""".format(item.text(1),
                                                 item.text(2),
                                                 item.text(4),
                                                 item.text(6))).fetchall()
                        secret_bin = (data5_item[0][0]).encode()
                        secret_dec = base64.b64decode(secret_bin)
                        decrypto = rsa.decrypt(secret_dec, privkey)
                        secret = decrypto.decode()
                        if secret == 'None':
                            data[-1].append('')
                        else:
                            data[-1].append(secret)
                    else:
                        data[-1].append(item.text(index))
            if item.parent():
                if item.parent():
                    tree_widget_item_count += 1
            else:
                tree_widget_item_count += 1
            iterator += 1
        self.pl.data = data

        column_widths = []
        for _ in range(1, self.treeWidget.headerItem().columnCount()):
            column_widths.append(180)
        self.pl.columnWidths = column_widths

        headers = []
        for index in range(1, self.treeWidget.headerItem().columnCount()):
            item = self.treeWidget.headerItem().text(index)
            headers.append(item)
        self.pl.headers = headers

        cur_print_thread.close()
        conn_print_thread.close()


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


def calc_rsa_length(rsa_bit: int) -> int:
    """
    Calculates the length of the RSA key.

    :param rsa_bit: indicates how many bits of rsa
    :return: returns the length of the rsa key. If -1 means an error.
    """
    if rsa_bit == 4096:
        length = 684
    elif rsa_bit == 3072:
        length = 512
    elif rsa_bit == 2048:
        length = 344
    elif rsa_bit == 1024:
        length = 172
    else:
        length = -1
    return length


def connect_sql():  # TODO: убрать глобалы и должна возвращать sqlite3.connect
    global conn
    global cur
    global rsa_length
    conn = sqlite3.connect(db_dir)
    cur = conn.cursor()
    cur.execute("PRAGMA key = '{}'".format(pwd))
    rsa_bit = cur.execute("""
    SELECT value
    FROM db_information
    WHERE name='rsa_bit'""").fetchone()[0]
    rsa_length = calc_rsa_length(int(rsa_bit))


class MainMenu(QtWidgets.QMainWindow, main_menu_ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.create_db = None
        self.loading_db = None
        self.adding_data = None
        self.sync_db = None
        self.timer = None
        self.timer_sec = None
        self.step = None
        self.show_pass_thread = None
        self.print_thread = None
        self.acc_info_list = list()
        self.acc_secret_info_result = dict()
        self.menu_context_alb = None
        self.change = None
        self.pubkey_file = os.path.isfile(f"{db_dir[:-3]}_pubkey.pem")
        self.privkey_file = os.path.isfile(f"{db_dir[:-3]}_privkey.pem")

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        for header_item_index in range(0, 7):
            self.treeWidget.headerItem().setFont(header_item_index, font)
        self.add_tree_widget_item()

        self.progressBar.hide()
        self.statusbar.addPermanentWidget(self.progressBar)
        self.statusbar.addPermanentWidget(self.label_version)

        self.spinner = QtWaitingSpinner(self, centerOnParent=True,
                                        disableParentWhenSpinning=True)
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

        if HIDE_PASSWORD:
            self.pushButton_showPass.setText('Показать пароли')
        else:
            self.pushButton_showPass.setText('Скрыть пароли')

        self.button_state()

        if not self.toolButton_privkey.isEnabled() \
                and not self.toolButton_pubkey.isEnabled():
            self.action_syncDb.setEnabled(True)

        self.retranslate_ui_main()

        self.action_saveDb.triggered.connect(self.save_db)
        self.action_createDb.triggered.connect(self.show_create_db)
        self.action_loadDb.triggered.connect(self.show_load_db)
        self.action_syncDb.triggered.connect(self.show_sync_db)
        self.action_print.triggered.connect(self.print_db)
        self.action_exit.triggered.connect(self.close)
        self.pushButton_delete.clicked.connect(self.delete_data)
        self.pushButton_addingData.clicked.connect(self.show_adding_data)
        self.pushButton_showHideSections.clicked.connect(
            self.show_hide_all_sections)
        self.pushButton_showPass.clicked.connect(self.password_hide_show)
        self.toolButton_pubkey.clicked.connect(self.choice_pubkey)
        self.toolButton_privkey.clicked.connect(self.choice_privkey)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(
            self.menu_context_album)

    def retranslate_ui_main(self):
        self.setWindowTitle(f"Password Saver - Главная | {db_name}")
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.add_tree_widget_item_text()
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.label_version.setText(VERSION)

        if self.pubkey_file and result_check_pubkey == 'ok':
            self.toolButton_pubkey.setText(pubkey_dir)
        elif self.pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_pubkey.setText('Ключ не подходит. Укажите pubkey.pem')
        elif self.pubkey_file and result_check_pubkey is None:
            self.toolButton_pubkey.setText(pubkey_dir)
        elif self.pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_pubkey.setText('Сначало укажите privkey.pem')
        else:
            self.toolButton_pubkey.setText("Укажите pubkey.pem")

        if self.privkey_file and result_check_privkey == 'ok':
            global privkey_dir
            privkey_dir = os.path.abspath("data/{}_privkey.pem".format(
                db_name[:-3]))
            self.toolButton_privkey.setText(privkey_dir)
        elif self.privkey_file and result_check_privkey == '!ok':
            self.toolButton_privkey.setText("Ключ не подходит. Укажите privkey.pem")
        elif self.privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton_privkey.setText("Ключи разные. Укажите правильный privkey.pem")
            self.toolButton_pubkey.setText("Ключи разные. Укажите правильный pubkey.pem")
        elif self.privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton_privkey.setText("Сначало укажите pubkey.pem")
        else:
            self.toolButton_privkey.setText("Укажите privkey.pem")

        self.progressBar.setFormat("")

    @QtCore.pyqtSlot()
    def print_db(self):
        if not self.toolButton_privkey.isEnabled():
            pl = print_list.PrintList()
            layout = QtGui.QPageLayout(QtGui.QPageSize(QtGui.QPageSize.A4),
                                       QtGui.QPageLayout.Landscape,
                                       QtCore.QMarginsF(5, 5, 5, 5),
                                       units=QtGui.QPageLayout.Millimeter)
            pl.printer.setPageLayout(layout)
            pd = QtPrintSupport.QPrintDialog(pl.printer, parent=None)
            result = pd.exec_()

            if result == 1:
                self.print_thread = PrintThread(tool_button=self.toolButton_privkey,
                                                tree_widget=self.treeWidget,
                                                pl=pl)
                self.print_thread.started.connect(self.print_spinner_started)
                self.print_thread.finished.connect(
                    lambda: self.print_spinner_finished(self.print_thread.pl))
                self.print_thread.start()
        else:
            show_msg(title='Ошибка',
                     top_text='Не указан privkey.pem',
                     window_type='critical',
                     buttons='ok')

    @QtCore.pyqtSlot()
    def print_spinner_started(self):
        self.spinner.start()
        self.statusbar.showMessage("Готовлюсь к печати...")

    @QtCore.pyqtSlot()
    def print_spinner_finished(self, pl):
        pl.print_data()
        self.spinner.stop()
        show_msg(title='Успех',
                 top_text='Печать завершена',
                 window_type='information',
                 buttons='ok')
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
                    self.treeWidget.topLevelItem(section_iter).child(
                        item_iter).setText(
                        3, self.acc_secret_info_result[_data_item[1]][0])
                item_iter += 1
            section_iter += 1

        self.pushButton_showPass.setText('Скрыть пароли')
        self.acc_info_list.clear()
        self.spinner.stop()
        self.statusbar.showMessage("Пароли расшифрованы.", msecs=10000)

    def show_pass_response(self, acc_secret_info_result):
        self.acc_secret_info_result = acc_secret_info_result

    @QtCore.pyqtSlot()
    def save_db(self):
        result = show_msg(title='Сохранение изменений',
                          top_text='Вы действительно хотите сохранить '
                                   'изменения в базе данных?',
                          window_type='information',
                          buttons='yes_no')
        if result == QtWidgets.QMessageBox.Yes:
            conn.commit()
            show_msg(title='Успех',
                     top_text='База данных сохранена',
                     buttons='ok')

    @QtCore.pyqtSlot()
    def show_create_db(self):
        self.create_db = database_creation.CreateDB()
        self.create_db.exec_()

    @QtCore.pyqtSlot()
    def show_load_db(self):
        self.loading_db = loading_db.LoadingDB()
        status_load_db = self.loading_db.exec()
        if status_load_db:
            self.pubkey_file = os.path.isfile(f"{db_dir[:-3]}_pubkey.pem")
            self.privkey_file = os.path.isfile(f"{db_dir[:-3]}_privkey.pem")
            self.refresh_tree_widget(load=True)
            self.result_check_privkey()
            self.result_check_pubkey()
            self.button_state()
            self.retranslate_ui_main()
            if result_check_pubkey:
                self.pushButton_addingData.setEnabled(True)
            [lines], = cur.execute("SELECT Count(*) FROM account_information")
            if lines == 0:
                self.pushButton_showHideSections.setEnabled(False)
                self.pushButton_showHideSections.setText(
                    "Развернуть все разделы")
            else:
                self.pushButton_showHideSections.setText("Свернуть все разделы")

    @QtCore.pyqtSlot()
    def show_sync_db(self):
        self.sync_db = sync_db.SyncDB(self.toolButton_privkey.text(),
                                      self.toolButton_pubkey.text())
        finished_sync_db = self.sync_db.exec()
        if finished_sync_db:
            self.refresh_tree_widget()

    @QtCore.pyqtSlot()
    def show_adding_data(self):
        global HIDE_PASSWORD
        if not HIDE_PASSWORD:
            self.password_hide()
        self.adding_data = adding_data.AddingData()
        checkbox_status = self.adding_data.exec_()
        self.refresh_tree_widget()

        if lines != 0 and self.privkey_file and result_check_privkey == 'ok' \
                or lines != 0 and result_check_choice_privkey == 'ok':
            self.pushButton_delete.setEnabled(True)
            self.pushButton_showPass.setEnabled(True)
        elif lines != 0 and self.privkey_file and result_check_privkey == '!ok'\
                or lines != 0 and result_check_choice_privkey == '!ok':
            self.pushButton_delete.setEnabled(True)
            self.pushButton_showPass.setEnabled(False)
        elif lines == 0:
            self.pushButton_delete.setEnabled(False)
        else:
            self.pushButton_delete.setEnabled(True)

        if checkbox_status:
            self.delete_buffer()

    @QtCore.pyqtSlot()
    def show_hide_all_sections(self):
        _text = self.pushButton_showHideSections.text()
        if _text == 'Развернуть все разделы':
            self.treeWidget.expandAll()
            self.pushButton_showHideSections.setText('Свернуть все разделы')
        else:
            self.treeWidget.collapseAll()
            self.pushButton_showHideSections.setText('Развернуть все разделы')

    def copy_buffer(self):
        global buffer
        row = self.current_row()
        if row[1] == 'item_1':
            buffer = QtWidgets.QApplication.clipboard()
            if buffer is not None:
                data_one_section = cur.execute("""
                SELECT pass
                FROM account_information
                WHERE name='{}' AND
                      login='{}' AND
                      email='{}' AND
                      url='{}'""".format(row[0][0], row[0][1],
                                         row[0][3], row[0][5])).fetchall()
                if choice_privkey is not None:
                    privkey = choice_privkey
                else:
                    with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') \
                            as privfile:
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
                     bottom_text='Если хотите удалить раздел, '
                                 'то удалите все аккаунты в нём.',
                     window_type='critical',
                     buttons='ok')
        elif row[1] == 'item_1':
            result = show_msg(title='Удаление аккаунта',
                              top_text=f'Данные аккаунта <b>{row[0][0]}</b> '
                                       f'с логином <b>{row[0][1]}</b> '
                                       f'будут удалены',
                              window_type='information',
                              bottom_text='Вы уверенны?',
                              buttons='yes_no')
            if result == QtWidgets.QMessageBox.Yes:
                acc_id = cur.execute("""SELECT id
                                        FROM account_information
                                        WHERE name = ? AND
                                              login = ? AND
                                              email = ? AND
                                              url = ? """,
                                     (row[0][0], row[0][1],
                                      row[0][3], row[0][5])).fetchall()[0][0]
                cur.execute("DELETE FROM data_change_time WHERE id = ?",
                            (str(acc_id),))
                cur.execute("""DELETE FROM account_information
                               WHERE name = ? AND
                                     login = ? AND
                                     email = ? AND
                                     url = ? """,
                            (row[0][0], row[0][1], row[0][3], row[0][5]))
                self.refresh_tree_widget()

        if lines == 0:
            self.pushButton_delete.setEnabled(False)
            self.pushButton_showPass.setEnabled(False)

    @QtCore.pyqtSlot()
    def password_hide_show(self):
        global HIDE_PASSWORD
        if lines != 0:
            if self.pushButton_showPass.text() == 'Показать пароли':
                HIDE_PASSWORD = False
                if choice_privkey is not None:
                    privkey = choice_privkey
                else:
                    with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb') \
                            as privfile:
                        keydata_priv = privfile.read()
                        privfile.close()
                    privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')

                for _data_section in range(amount_item_0):
                    data_one_section = cur.execute("""
                    SELECT *
                    FROM account_information
                    WHERE section='{}'""".format(
                        srt_section[_data_section])).fetchall()
                    acc_info = []
                    for item in data_one_section:
                        acc_info.append(list(item[2:]))

                    self.acc_info_list.append(acc_info)

                __acc_secret_info = dict()
                for _data_section in self.acc_info_list:
                    for _data_item in _data_section:
                        __acc_secret_info[_data_item[1]] = _data_item[2],\
                                                           _data_item[4]

                self.show_pass_thread = ShowPassThread(__acc_secret_info, privkey)
                self.show_pass_thread.started.connect(
                    self.show_pass_spinner_started)
                self.show_pass_thread.response.connect(self.show_pass_response)
                self.show_pass_thread.finished.connect(
                    self.show_pass_spinner_finished)
                self.show_pass_thread.start()
            elif self.pushButton_showPass.text() == 'Скрыть пароли':
                HIDE_PASSWORD = True
                top_level_item_iter = -1
                for data_section in range(amount_item_0):
                    data_one_section = cur.execute("""
                    SELECT *
                    FROM account_information
                    WHERE section='{}'""".format(
                        srt_section[data_section])).fetchall()
                    acc_info = []
                    for item in data_one_section:
                        acc_info.append(item[2:])
                    self.treeWidget.topLevelItem(data_section).setText(
                        0, str(srt_section[data_section]))
                    top_level_item_iter += 1
                    child_iter = -1
                    for index in range(len(acc_info)):
                        child_iter += 1
                        text_iter = 0
                        for _ in acc_info[index]:
                            text_iter += 1
                            if text_iter == 3:
                                self.treeWidget.topLevelItem(top_level_item_iter) \
                                    .child(child_iter) \
                                    .setText(text_iter, '**********')
                self.pushButton_showPass.setText('Показать пароли')

    @QtCore.pyqtSlot()
    def choice_pubkey(self):
        global choice_pubkey
        global result_check_choice_pubkey
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Укажите публичный ключ-файл (.pem)', os.getcwd(),
            '{}_pubkey.pem;;*_pubkey.pem'.format(db_name[:-3]))
        if directory_name[0] != '' and directory_name[1] != '':
            with open(directory_name[0], 'rb') as pubfile:
                keydata_pub = pubfile.read()
                pubfile.close()
            choice_pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
            self.toolButton_pubkey.setEnabled(False)
            self.toolButton_pubkey.setText(directory_name[0])
            self.pushButton_addingData.setEnabled(True)

            if not self.toolButton_privkey.isEnabled():
                try:
                    with open(self.toolButton_privkey.text(), 'rb') as privfile:
                        keydata_priv = privfile.read()
                        privfile.close()
                    self_test_privfile = rsa.PrivateKey.load_pkcs1(keydata_priv,
                                                                   'PEM')
                    chars = string.ascii_letters + string.digits
                    rnd_text = ''.join(random.choice(chars) for _ in range(20))
                    rnd_text = rnd_text.encode()
                    crypto_text = rsa.encrypt(rnd_text, choice_pubkey)
                    self_test_decrypto = rsa.decrypt(crypto_text,
                                                     self_test_privfile)
                    result_check_choice_pubkey = 'ok'
                    self.action_syncDb.setEnabled(True)
                except rsa.pkcs1.DecryptionError as rsa_dec_error:
                    self.toolButton_pubkey.setEnabled(True)
                    self.toolButton_pubkey.setText('Ключ неправильный. '
                                                   'Укажите pubkey.pem')
                    self.pushButton_addingData.setEnabled(False)
                    self.statusbar.showMessage(f'Ошибка: {rsa_dec_error}',
                                               30000)
                    result_check_choice_pubkey = '!ok'

    @QtCore.pyqtSlot()
    def choice_privkey(self):
        global choice_privkey
        global result_check_choice_privkey
        directory_name = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Укажите приватный ключ-файл (.pem)', os.getcwd(),
            '{}_privkey.pem;;*_privkey.pem'.format(db_name[:-3]))
        if directory_name[0] != '' and directory_name[1] != '':
            with open(directory_name[0], 'rb') as privfile:
                keydata_priv = privfile.read()
                privfile.close()
            choice_privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            if lines == 0:
                self.toolButton_privkey.setEnabled(False)
                self.toolButton_privkey.setText(directory_name[0])
                result_check_choice_privkey = 'ok'
                if not self.toolButton_pubkey.isEnabled():
                    self.action_syncDb.setEnabled(True)
            elif lines != 0:
                try:
                    first_pass = cur.execute("""
                    SELECT pass
                    FROM account_information
                    ORDER BY ID ASC LIMIT 1""").fetchall()
                    password_bin = (first_pass[0][0]).encode()
                    password_dec = base64.b64decode(password_bin)
                    decrypto = rsa.decrypt(password_dec, choice_privkey)
                    password = decrypto.decode()
                    result_check_choice_privkey = 'ok'
                except rsa.pkcs1.DecryptionError as rsa_dec_error:
                    result_check_choice_privkey = '!ok'
                    self.toolButton_privkey.setText(
                        'Ключ не подходит. '
                        'Выберете правильный privkey')
                    self.statusbar.showMessage(f'Ошибка: {rsa_dec_error}',
                                               30000)
                if result_check_choice_privkey == 'ok':
                    self.toolButton_privkey.setEnabled(False)
                    self.toolButton_privkey.setText(directory_name[0])
                    self.pushButton_showPass.setEnabled(True)
                    if not self.toolButton_pubkey.isEnabled():
                        try:
                            with open(self.toolButton_pubkey.text(), 'rb')\
                                    as pubfile:
                                keydata_pub = pubfile.read()
                                pubfile.close()
                            self_test_pubfile = rsa.PublicKey.load_pkcs1(
                                keydata_pub, 'PEM')
                            chars = string.ascii_letters + string.digits
                            rnd_text = ''.join(random.choice(chars)
                                               for _ in range(20))
                            rnd_text = rnd_text.encode()
                            crypto_text = rsa.encrypt(rnd_text,
                                                      self_test_pubfile)
                            self_test_decrypto = rsa.decrypt(crypto_text,
                                                             choice_privkey)
                            self.action_syncDb.setEnabled(True)
                        except rsa.pkcs1.DecryptionError as rsa_dec_error:
                            self.toolButton_pubkey.setEnabled(True)
                            self.toolButton_pubkey.setText('Ключ неправильный. '
                                                           'Укажите pubkey.pem')
                            self.pushButton_addingData.setEnabled(False)
                            self.statusbar.showMessage(
                                f'Ошибка: {rsa_dec_error}', 30000)

    def result_check_privkey(self):
        global result_check_privkey
        if lines != 0 and self.privkey_file:
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb')\
                        as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                first_pass = cur.execute("""
                SELECT pass
                FROM account_information
                ORDER BY ID ASC LIMIT 1""").fetchall()
                password_bin = (first_pass[0][0]).encode()
                password_dec = base64.b64decode(password_bin)
                decrypto = rsa.decrypt(password_dec, privkey)
                password = decrypto.decode()
                result_check_privkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                result_check_privkey = '!ok'
        elif lines == 0 and self.privkey_file and self.pubkey_file:
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb')\
                        as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(db_dir[:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for _ in range(20))
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
        if self.pubkey_file and self.privkey_file\
                and result_check_privkey == 'ok':
            try:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb')\
                        as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
                with open('{}_pubkey.pem'.format(db_dir[:-3]), 'rb') as pubfile:
                    keydata_pub = pubfile.read()
                    pubfile.close()
                pubkey = rsa.PublicKey.load_pkcs1(keydata_pub, 'PEM')
                chars = string.ascii_letters + string.digits
                rnd_pass = ''.join(random.choice(chars) for _ in range(20))
                rnd_pass = rnd_pass.encode()
                crypto_pass = rsa.encrypt(rnd_pass, pubkey)
                decrypto = rsa.decrypt(crypto_pass, privkey)
                result_check_pubkey = 'ok'
            except rsa.pkcs1.DecryptionError:
                result_check_pubkey = '!ok'
        else:
            result_check_pubkey = None

    def button_state(self):
        global pubkey_dir
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resource/image/cross.ico"),
                       QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        if self.pubkey_file and result_check_pubkey == 'ok':
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(
                db_name[:-3]))
            self.toolButton_pubkey.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey == '!ok':
            self.toolButton_pubkey.setEnabled(True)
            self.pushButton_addingData.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey is None:
            pubkey_dir = os.path.abspath("data/{}_pubkey.pem".format(
                db_name[:-3]))
            self.toolButton_pubkey.setEnabled(False)
        elif self.pubkey_file and result_check_pubkey == 'not privkey':
            self.toolButton_pubkey.setEnabled(False)
            self.toolButton_pubkey.setIcon(icon)
        else:
            self.toolButton_pubkey.setEnabled(True)
            self.pushButton_addingData.setEnabled(False)

        if self.privkey_file and result_check_privkey == 'ok':
            self.toolButton_privkey.setEnabled(False)
            self.pushButton_showPass.setEnabled(True)
        elif self.privkey_file and result_check_privkey == '!ok':
            self.toolButton_privkey.setEnabled(True)
            self.pushButton_addingData.setEnabled(False)
            self.pushButton_showPass.setEnabled(False)
        elif self.privkey_file and result_check_privkey == 'privkey != pubkey':
            self.toolButton_privkey.setEnabled(True)
            self.toolButton_pubkey.setEnabled(True)
            self.pushButton_addingData.setEnabled(False)
        elif self.privkey_file and result_check_privkey == 'not pubkey':
            self.toolButton_privkey.setEnabled(False)
            self.toolButton_privkey.setIcon(icon)
        else:
            self.toolButton_privkey.setEnabled(True)
            self.pushButton_showPass.setEnabled(False)

        if lines == 0:
            self.pushButton_delete.setEnabled(False)
            self.pushButton_showPass.setEnabled(False)

    def delete_buffer(self):
        global BUFFER_DEL_SEC
        self.timer = QtCore.QBasicTimer()
        self.timer_sec = QtCore.QTimer()
        self.step = 0
        self.statusbar.showMessage("Данные будут удалены с буфера обмена "
                                   f"через {BUFFER_DEL_SEC} секунд")
        timer_del = BUFFER_DEL_SEC * 10
        if self.timer_sec.isActive():
            self.timer_sec.stop()
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(timer_del, self)
            self.progressBar.show()
            self.start_timer(self.timer_func, BUFFER_DEL_SEC)

    def timerEvent(self, e):
        global BUFFER_DEL_SEC
        if self.step >= 100:
            self.timer.stop()
            buffer.clear()
            self.statusbar.showMessage("Данные удалены с буфера обмена")
            return
        else:
            self.step += 1
            self.progressBar.setValue(self.step)

    def start_timer(self, slot, count=0, interval=1000):
        global BUFFER_DEL_SEC
        counter = BUFFER_DEL_SEC

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
        global BUFFER_DEL_SEC
        self.statusbar.showMessage("Данные будут удалены с буфера обмена "
                                   f"через {count} секунд")
        if count <= 0:
            self.timer_sec.stop()

    def menu_context_album(self, event):
        global buffer
        global result_check_privkey
        global result_check_pubkey
        row = self.current_row()
        if row[1] == 'item_1':
            self.menu_context_alb = QtWidgets.QMenu(self.treeWidget)

            rsub_menu_copy_log = self.menu_context_alb.addMenu("Копировать")
            rsub_menu_change_log = self.menu_context_alb.addMenu("Изменить")
            rsub_menu_transfer_acc = self.menu_context_alb.addMenu(
                "Переместить в")

            rmenu_copy_log = rsub_menu_copy_log.addAction("Копировать логин")
            rmenu_copy_pass = rsub_menu_copy_log.addAction("Копировать пароль")
            rmenu_copy_email = rsub_menu_copy_log.addAction("Копировать почту")
            rmenu_copy_secret = rsub_menu_copy_log.addAction(
                "Копировать секретное слово")
            rmenu_copy_url = rsub_menu_copy_log.addAction("Копировать url")

            if result_check_privkey == 'ok'\
                    or result_check_choice_privkey == 'ok':
                rmenu_copy_pass.setEnabled(True)
                rmenu_copy_secret.setEnabled(True)
            else:
                rmenu_copy_pass.setEnabled(False)
                rmenu_copy_secret.setEnabled(False)

            rmenu_change_log = rsub_menu_change_log.addAction("Изменить логин")
            rmenu_change_pass = rsub_menu_change_log.addAction("Изменить пароль")
            rmenu_change_email = rsub_menu_change_log.addAction("Изменить почту")
            rmenu_change_secret = rsub_menu_change_log.addAction(
                "Изменить секретное слово")
            rmenu_change_url = rsub_menu_change_log.addAction("Изменить url")

            sect_list = []
            section = cur.execute("""
            SELECT section 
            FROM account_information 
            GROUP BY section 
            ORDER BY id""").fetchall()
            for section_item in section:
                sect_list.append(rsub_menu_transfer_acc.addAction(
                    section_item[0]))

            if not self.toolButton_pubkey.isEnabled():
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

            action2 = self.menu_context_alb.exec_(
                self.treeWidget.mapToGlobal(event))
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
                                     top_text='На этом аккаунте нет почты',
                                     window_type='critical',
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
                                     window_type='critical',
                                     buttons='ok')
                        else:
                            buffer.setText(row[0][5])
                            self.delete_buffer()
                elif action2 == rmenu_copy_pass:
                    self.copy_buffer()
                elif action2 == rmenu_copy_secret:
                    buffer = QtWidgets.QApplication.clipboard()
                    if buffer is not None:
                        data_one_section = cur.execute("""
                        SELECT secret_word 
                        FROM account_information 
                        WHERE name='{}' AND 
                              login='{}' AND 
                              email='{}' AND 
                              url='{}'""".format(row[0][0], row[0][1],
                                                 row[0][3], row[0][5])
                                                       ).fetchall()
                        if choice_privkey is not None:
                            privkey = choice_privkey
                        else:
                            with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb')\
                                    as privfile:
                                keydata_priv = privfile.read()
                                privfile.close()
                            privkey = rsa.PrivateKey.load_pkcs1(keydata_priv,
                                                                'PEM')
                        secret_bin = data_one_section[0][0].encode()
                        secret_dec = base64.b64decode(secret_bin)
                        decrypto = rsa.decrypt(secret_dec, privkey)
                        secret = decrypto.decode()
                        if secret == 'None':
                            show_msg(title='Ошибка',
                                     top_text='На этом аккаунте не указанно '
                                              'секретное слово',
                                     window_type='critical',
                                     buttons='ok')
                        else:
                            buffer.setText(secret)
                            self.delete_buffer()
                elif action2 == rmenu_change_log:
                    self.change = change.Change('Изменение логина',
                                                'Введите новый логин', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        login = self.change.lineEdit.text()
                        if login != '':
                            record_change_time(cur, row, 'change_login')
                            cur.execute("""
                            UPDATE account_information
                            SET login = ?
                            WHERE name = ? AND
                                  login = ? AND
                                  email = ? AND
                                  url = ? """, (login, row[0][0], row[0][1],
                                                row[0][3], row[0][5]))
                            self.refresh_tree_widget()
                        else:
                            show_msg(title='Ошибка',
                                     top_text='Нельзя изменить на пустой логин',
                                     window_type='critical',
                                     buttons='ok')
                elif action2 == rmenu_change_pass:
                    self.change = change.Change('Изменение пароля',
                                                'Введите новый пароль', True)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        if self.change.lineEdit.text() == '':
                            show_msg(title='Ошибка',
                                     top_text='Нельзя изменить на пустой пароль',
                                     window_type='critical',
                                     buttons='ok')
                        else:
                            if not self.toolButton_pubkey.isEnabled():
                                path_to_pubkey = self.toolButton_pubkey.text()
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
                            cur.execute("""
                            UPDATE account_information
                            SET pass = ?
                            WHERE name = ? AND
                                  login = ? AND
                                  email = ? AND
                                  url= ? """, (password, row[0][0], row[0][1],
                                               row[0][3], row[0][5]))
                            self.refresh_tree_widget()
                elif action2 == rmenu_change_email:
                    self.change = change.Change('Изменение почты',
                                                'Введите новую почту', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        email = self.change.lineEdit.text()
                        if email == '':
                            email = None
                        record_change_time(cur, row, 'change_email')
                        cur.execute("""
                        UPDATE account_information
                        SET email = ?
                        WHERE name = ? AND
                              login = ? AND
                              email = ? AND
                              url = ? """, (email, row[0][0], row[0][1],
                                            row[0][3], row[0][5]))
                        self.refresh_tree_widget()
                elif action2 == rmenu_change_secret:
                    self.change = change.Change('Изменение секретного слова',
                                                'Введите новое секретное слово',
                                                False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        secret_text = self.change.lineEdit.text()
                        if secret_text == '':
                            secret_text = 'None'
                        if not self.toolButton_pubkey.isEnabled():
                            path_to_pubkey = self.toolButton_pubkey.text()
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
                        cur.execute("""
                        UPDATE account_information
                        SET secret_word = ?
                        WHERE name = ? AND
                              login = ? AND
                              email = ? AND
                              url = ? """, (secret, row[0][0], row[0][1],
                                            row[0][3], row[0][5]))
                        self.refresh_tree_widget()
                elif action2 == rmenu_change_url:
                    self.change = change.Change('Изменение url',
                                                'Введите новый url', False)
                    result_close_window = self.change.exec_()
                    if result_close_window:
                        url = self.change.lineEdit.text()
                        if url == '':
                            url = None
                        record_change_time(cur, row, 'change_url')
                        cur.execute("""
                        UPDATE account_information
                        SET url = ?
                        WHERE name = ? AND
                              login = ? AND
                              email = ? AND
                              url = ? """, (url, row[0][0], row[0][1],
                                            row[0][3], row[0][5]))
                        self.refresh_tree_widget()

                for item_type in sect_list:
                    if action2 is not None and action2 == item_type:
                        record_change_time(cur, row, 'change_section')
                        cur.execute("""
                        UPDATE account_information
                        SET section = ?
                        WHERE name = ? AND
                              login = ? AND
                              email = ? AND
                              url = ? """, (item_type.text(), row[0][0],
                                            row[0][1], row[0][3], row[0][5]))
                        self.refresh_tree_widget()

    def add_tree_widget_item(self):
        global lines
        global amount_item_0
        global srt_section
        [lines], = cur.execute("SELECT Count(*) FROM account_information")
        section = []
        if lines != 0:
            self.pushButton_showHideSections.setEnabled(True)
            for _line in range(1, lines + 1):
                [_current_id], = cur.execute("""
                SELECT ID 
                FROM account_information 
                LIMIT 1 OFFSET {}""".format(_line - 1))

                [_current_section], = cur.execute("""
                SELECT section 
                FROM account_information 
                WHERE ID='{}'""".format(_current_id))

                section.append(_current_section)
            srt_section = list(dict.fromkeys(section))
            amount_item_0 = len(list(set(section)))
            for _data_section in range(amount_item_0):
                if _data_section == 0:
                    item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
                    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                    brush.setStyle(QtCore.Qt.NoBrush)
                    for index in range(0, 7):
                        item_0.setBackground(index, brush)
                    data_one_section = cur.execute("""
                    SELECT * 
                    FROM account_information 
                    WHERE section='{}'""".format(
                        srt_section[_data_section])).fetchall()
                else:
                    data_one_section = cur.execute("""
                    SELECT * 
                    FROM account_information 
                    WHERE section='{}'""".format(
                        srt_section[_data_section])).fetchall()
                    item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
                for _ in range(len(data_one_section)):
                    item_1 = QtWidgets.QTreeWidgetItem(item_0)
        else:
            self.pushButton_showHideSections.setEnabled(False)

    def delete_tree_widget_item(self):
        self.treeWidget.clear()

    def add_tree_widget_item_text(self):
        global privkey
        top_level_item_iter = -1
        child_iter = -1
        text_iter = 0
        if lines != 0:
            if self.privkey_file:
                with open('{}_privkey.pem'.format(db_dir[:-3]), 'rb')\
                        as privfile:
                    keydata_priv = privfile.read()
                    privfile.close()
                privkey = rsa.PrivateKey.load_pkcs1(keydata_priv, 'PEM')
            elif choice_privkey:
                privkey = choice_privkey

            for _data_section in range(amount_item_0):
                data_one_section = cur.execute("""
                SELECT * 
                FROM account_information 
                WHERE section='{}'""".format(
                    srt_section[_data_section])).fetchall()
                acc_info = []
                for item in data_one_section:
                    acc_info.append(item[2:])
                self.treeWidget.topLevelItem(_data_section)\
                    .setText(0, str(srt_section[_data_section]))
                top_level_item_iter += 1
                child_iter = -1
                for _index in range(len(acc_info)):
                    child_iter += 1
                    text_iter = 0
                    for _value in acc_info[_index]:
                        text_iter += 1
                        if (text_iter == 3 and HIDE_PASSWORD)\
                                or (text_iter == 5 and HIDE_PASSWORD):
                            self.treeWidget.topLevelItem(top_level_item_iter)\
                                .child(child_iter)\
                                .setText(text_iter, str('**********'))
                        elif _value is None:
                            value = None
                            self.treeWidget.topLevelItem(top_level_item_iter)\
                                .child(child_iter)\
                                .setText(text_iter, str(value))
                        elif len(_value) == rsa_length:
                            value_bin = _value.encode()
                            value_dec = base64.b64decode(value_bin)
                            try:
                                decrypto_value = rsa.decrypt(value_dec, privkey)
                                value = decrypto_value.decode()
                                self.treeWidget\
                                    .topLevelItem(top_level_item_iter)\
                                    .child(child_iter)\
                                    .setText(text_iter, str(value))
                            except rsa.pkcs1.DecryptionError:
                                value = '##ERRORPUBKEY##'
                                self.treeWidget\
                                    .topLevelItem(top_level_item_iter)\
                                    .child(child_iter)\
                                    .setText(text_iter, str(value))
                        elif (text_iter == 3 and rsa_length == 'error')\
                                or (text_iter == 5 and rsa_length == 'error'):
                            value = '##ERRORKEYLENGTH##'
                            self.treeWidget\
                                .topLevelItem(top_level_item_iter)\
                                .child(child_iter)\
                                .setText(text_iter, str(value))
                        else:
                            self.treeWidget\
                                .topLevelItem(top_level_item_iter)\
                                .child(child_iter)\
                                .setText(text_iter, str(_value))

    def create_tree_widget_top_items(self):
        """
        Creates a list with QTreeWidget => topLevelItem.

        :return: list[QTreeWidgetItem]
        """
        top_tree_widget_items = []
        for index_top_item in range(self.treeWidget.topLevelItemCount()):
            top_item = self.treeWidget.topLevelItem(index_top_item)
            top_tree_widget_items.append(top_item)
        return top_tree_widget_items
    
    def check_head_item_expand(self):
        """
        Checks top-level treeWidget items for expanded state and returns
        a dictionary with section name and expanded state.
            example: {'name_section': 'True/False'}

        :return: dict[str, bool]
        """

        top_tree_widget_items = self.create_tree_widget_top_items()

        name_and_expanded = {}
        for top_item in top_tree_widget_items:
            name_section = top_item.text(0)
            is_expanded = top_item.isExpanded()
            name_and_expanded[name_section] = is_expanded

        return name_and_expanded

    def refresh_tree_widget(self, load=False):
        """ Update QTreeWidgetItems with save expanded state. """
        name_expanded_top_item = self.check_head_item_expand()
        self.delete_tree_widget_item()
        self.add_tree_widget_item()
        self.add_tree_widget_item_text()

        tree_widget_items = self.create_tree_widget_top_items()

        for top_item in tree_widget_items:
            section_name = top_item.text(0)
            if section_name in name_expanded_top_item:
                if name_expanded_top_item[section_name]:
                    self.treeWidget.expandItem(top_item)
            elif not load:
                self.treeWidget.expandItem(top_item)

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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        close = show_msg(title='Предупреждение',
                         top_text='Все несохраненные изменения будут потеряны',
                         bottom_text='Все равно выйти?',
                         window_type='warning',
                         buttons='yes_no')
        if close == QtWidgets.QMessageBox.Yes:
            if buffer is not None:
                buffer.clear()
            cur.close()
            conn.close()
            a0.accept()
        else:
            a0.ignore()
