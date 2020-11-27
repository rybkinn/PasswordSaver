# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import sqlite3
import py.DatabaseCreation
import py.AddingData
import py.StartWindow

import pprint


def show_msg(text_show, text2_show):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text_show)
    msg.setInformativeText(text2_show)
    msg.setWindowTitle("Сообщение")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
    result = msg.exec_()
    return result


class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.createdb = createdb()
        lines = 0

    def connectsql(self, connected):
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
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(810, 540, 31, 20))
        self.label_2.setObjectName("label_2")
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

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.action_3.triggered.connect(self.savebd)
        self.action_4.triggered.connect(self.show_createdb)
        self.action_5.triggered.connect(self.loadbd)
        self.action_7.triggered.connect(self.exit)
        self.pushButton.clicked.connect(self.deletedata)
        self.pushButton_2.clicked.connect(self.show_addingdata)
        self.pushButton_3.clicked.connect(self.copybuffer)

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
                        exec('self.treeWidget.topLevelItem(%d).child(%d).setText(%d, _translate("MainWindow", "%s"))' % (toplevelitem_iter, child_iter, text_iter, _value))

        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.pushButton_3.setText(_translate("MainWindow", "Копировать пароль в буфер"))
        self.pushButton.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        self.label_2.setText(_translate("MainWindow", "v 0.2"))
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
        if result == 1024:
            conn.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Сообщение")
            msg.setText("База данных сохранена")
            msg.exec_()
        elif result == 65536:
            pass

    @QtCore.pyqtSlot()
    def show_createdb(self):
        self.createdb.show()

    @QtCore.pyqtSlot()
    def loadbd(self):
        print('loadbd')
        pass

    @QtCore.pyqtSlot()
    def exit(self):
        result = show_msg('Все несохраненные изменения будут потеряны.', 'Все равно выйти?')
        if result == 1024:
            conn.close()
            self.close()
        elif result == 65536:
            pass

    @QtCore.pyqtSlot()
    def show_addingdata(self):
        self.addingdata = addingdata()
        self.addingdata.exec_()
        self.refreshui()

    @QtCore.pyqtSlot()
    def copybuffer(self):
        row = self.current_row()
        buffer = QtWidgets.QApplication.clipboard()
        if row[1] == 'item_1':
            if buffer is not None:
                buffer.setText(row[0][2])
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Сообщение")
                msg.setText("Пароль скопирован")
                msg.exec_()
        pass

    @QtCore.pyqtSlot()
    def deletedata(self):
        row = self.current_row()
        if row[1] == 'item_0 first' or row[1] == 'item_0':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Сообщение")
            msg.setText("Нельзя удалить раздел")
            msg.setInformativeText("Если хотите удалить раздел, то удалите все аккаунты в нём")
            msg.exec_()
        elif row[1] == 'item_1':
            result = show_msg('Данные аккаунта <b>{}</b> с логином <b>{}</b> будут удалены.'.format(row[0][0], row[0][1]), 'Вы уверенны?')
            if result == 1024:
                cur.execute("DELETE FROM account_information WHERE name='{}' AND login='{}' AND pass='{}' AND email='{}' AND secret_word='{}' AND url='{}'".format(row[0][0], row[0][1], row[0][2], row[0][3], row[0][4], row[0][5]))
                self.refreshui()
            elif result == 65536:
                pass

    def refreshui(self):
        self.close()
        self.__init__()
        self.show()
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


class createdb(QtWidgets.QDialog, py.DatabaseCreation.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class addingdata(QtWidgets.QDialog, py.AddingData.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
