#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# For Python3.x

import sys
import operator  # used for sorting
import random
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, QEvent, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QMainWindow, QMdiArea, QWidget, QTableView,
    QAbstractItemView, QGridLayout,
    QStyledItemDelegate, QCompleter, QLineEdit, QApplication)


title = 'Backlight management'
header = ['Pos', 'Supplier', 'Artikel', 'Benennung']
table = [['001', 'Meyer', '47110', 'Bratwurst weiss, 125 g / Stuck, 50% Schweinefleisch, 50% Rindfleisch'],
    ['002', 'Mueller', '47110', 'Bratwurst weiss, 125 g / Stuck, 50% Schweinefleisch, 50% Rindfleisch'],
    ['003', 'Mauser', '47110', 'Bratwurst weiss, 125 g / Stuck, 50% Schweinefleisch, 50% Rindfleisch']]
columnWidths = [20, 30, 40, 400]

completer_list = ['Mauser', 'Meyer', 'Mueller']


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("MDI demo")
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.tileSubWindows()
        title = 'TEST'
        self.list_model = 'listinlist'
        sub = Table(self, title, table, header, columnWidths)
        self.mdi_area.addSubWindow(sub)
        sub.show()


class Table(QWidget):
    def __init__(self, parent, title, dataList, header, columnWidths):
        QWidget.__init__(self)
        self.parent = parent
        self.title = title
        self.old_data = self.mylist = self.dataList = sorted(dataList)
        self.header = header
        self.columnWidths = columnWidths
        self.mdi_area = parent.mdi_area
        self.setWindowTitle(self.title) 
        self.installEventFilter(self)
        self.view = QTableView()
        self.model = TableModel(self, self.dataList, self.header)
        self.update_table()
        self.headerSize(parent)
        # GridLayout
        grid = QGridLayout() 
        grid.addWidget(self.view, 0, 0)
        self.setLayout(grid) 

    def updateGeometryAsync(self):
        QtCore.QTimer.singleShot(0, self.updateGeometry)

    def headerSize(self, parent):
        """
        Build header- and columnsize
        """
        view = self.view
        model = self.model
        view.setModel(model)
        view.resizeColumnsToContents()
        view.resizeRowsToContents()
        view.setWordWrap(True)

    def update_table(self):
        # ... when a row header label changes and makes the
        # width of the vertical header change too       
        self.model.headerDataChanged.connect(self.updateGeometryAsync)
        self.view.setModel(self.model)
        # enable sorting
        self.view.setSortingEnabled(True)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.old_data_counter = len(self.mylist)
        self.mdi_area.adjustSize()
        index = self.view.model().index(0, 1)
        self.view.setCurrentIndex(index)

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress and widget is self:
            key = event.key()
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                DatasetView(self, self.view, self.model)
            return True
        return QWidget.eventFilter(self, widget, event)


class TableModel(QtCore.QAbstractTableModel):
    """
    Build table
    """

    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if (orientation == QtCore.Qt.Horizontal
                and role == QtCore.Qt.DisplayRole):
            return self.header[col]
        return None

    def sort(self, col, order):
        """
        Sort table by given column number col
        """

        self.layoutAboutToBeChanged.emit()
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist #.reverse()
        self.layoutChanged.emit()

    def output_list(self):
        return self.mylist


class DatasetView(object):

    #def datasetView(self):
    def __init__(self, parent, view, model):

        self.parent = parent
        self.model = model
        self.mdi_area = self.parent.mdi_area
        i = QAbstractItemView.SelectRows
        self.mylist = model.output_list()
        self.index = view.selectedIndexes()[0].row()
        dataset = self.mylist[self.index]
        header = parent.header
        width = 300
        dialog = Dataset(self, dataset, header, width)
        self.new_child_window(dialog)

    def new_child_window(self, dialog):
        # Show dataset window
        sub = self.mdi_area.addSubWindow(dialog).show()


class TableItemCompleter(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        print('#######################')
        print('index', index)
        editor = QLineEdit(parent)
        print('editor', editor)
        print('index.data', index.data(), index.data(Qt.UserRole))
        completion_ls = index.data(Qt.UserRole) # get list
        completer = QCompleter(completion_ls, parent)
        editor.setCompleter(completer)
        print('#######################')
        return editor


class Dataset(QWidget): 

    def __init__(self, parent, dataset, header, columnWidths): 
        super(Dataset, self).__init__()
        self.parent = parent
        self.dataset = dataset
        self.header = header
        self.columnWidths = columnWidths
        self.setObjectName('DATASET')
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.StrongFocus)
        self.view = QTableView(self)
        self.view.clicked.connect(self._item_clicked)
        # GridLayout
        grid = QGridLayout() 
        grid.addWidget(self.view, 0, 0)
        self.setLayout(grid)
        self.model = QStandardItemModel(self)
        # Load dataset
        [self.model.invisibleRootItem().appendRow(
            QStandardItem(column)) for column in self.dataset]
        # Vertical header
        [self.model.setHeaderData(i, Qt.Vertical, column)
            for i, column in enumerate(header)]
        self.proxy = QSortFilterProxyModel(self) 
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        # set completer for item
        self.view.setItemDelegate(TableItemCompleter(
            self.model.invisibleRootItem().child(1).setData(
            (Qt.UserRole, random.sample(completer_list, 1)))))

    def sizeHint(self):
        # and the margins which include the frameWidth and the extra
        # margins that would be set via a stylesheet or something else
        margins = self.contentsMargins()
        # y
        height = round(self.fontMetrics().height() * 1.1)
        height += self.view.verticalHeader().length()
        height += self.view.horizontalHeader().height()
        height += self.view.horizontalScrollBar().height()
        height += margins.left() + margins.right()
        # x
        width = self.view.horizontalHeader().length()
        width += self.view.verticalHeader().width()
        width += self.view.verticalScrollBar().width()
        width += margins.left() + margins.right()
        return QSize(width, height)

    def _item_clicked(self, index):
        # numeric position of dataset
        pos2dataset = index.row()
        # in front of item
        self.item_after = index.sibling(1,0)
        # in front of item
        item_before = index.sibling(-1,0)

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()