# -*- coding: utf-8 -*-
# file: pdfrog/journallistwidget.py

from PySide.QtCore import *
from PySide.QtGui import *
import pdfrog
from .datamodel import Journal

class JournalList(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)
        self.parent = parent
        self.setModel(JournalListModel(self))
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setHighlightSections(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.installEventFilter(self)

        self.query = None
        self.refreshData()

    def refreshData(self, query=None):
        if query is None:
            query = self.query or pdfrog.session.query(Journal).limit(300)
        self.query = query
        self.model().clearData()
        item_count = 0
        for journal in query:
            self.model().appendJournal(journal)
            item_count += 1
        return item_count

    def createMenu(self, journal_menu):
        journal_refresh_list_action = QAction(QIcon.fromTheme("view-refresh"), "Refresh list", self)
        journal_refresh_list_action.triggered.connect(self.refreshData)

        journal_menu.addAction(journal_refresh_list_action)
        self.context_menu = journal_menu

    def item(self, row):
        return self.model().item(row)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu:
            self.context_menu.exec_(QCursor.pos())
            return True
        else:
            return QTableView.eventFilter(self, obj, event)


class JournalListModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.datastore = []
        self.view = parent

    COLUMN_TITLE = 0
    COLUMN_ARTICLE_COUNT = 1

    def rowCount(self, parent=None):
        return len(self.datastore)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): return None
        if role == Qt.DisplayRole:
            column = index.column()
            if column == self.COLUMN_TITLE:
                return self.datastore[index.row()].title
            elif column == self.COLUMN_ARTICLE_COUNT:
                return str(self.datastore[index.row()].articleCount())
            else:
                return "unknown"
        else:
            return None

    def headerData(self, column, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if column == self.COLUMN_TITLE: return "Name"
                elif column == self.COLUMN_ARTICLE_COUNT: return "Article Count"
                else: return "Unknown"
        return None

    def appendJournal(self, journal):
        self.beginInsertRows(QModelIndex(), len(self.datastore), len(self.datastore))
        self.datastore.append(journal)
        self.endInsertRows()

    def clearData(self):
        self.modelReset.emit()
        self.datastore = []

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if column == self.COLUMN_TITLE:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.title, reverse=(order == Qt.DescendingOrder))
        elif column == self.COLUMN_ARTICLE_COUNT:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.articleCount(), reverse=(order == Qt.DescendingOrder))
        self.layoutChanged.emit()

    def item(self, row):
        return self.datastore[row]
