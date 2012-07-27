# -*- coding: utf-8 -*-
# file: pdfrog/authorlistwidget.py

from PySide.QtGui import *
from PySide.QtCore import *
import pdfrog
from .datamodel import Author

class AuthorList(QTableView):
    def __init__(self, parent=None, *args):
        QTableView.__init__(self, parent, *args)
        self.parent = parent
        self.setModel(AuthorListModel())
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setHighlightSections(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.installEventFilter(self)

        self.refreshData()

    def item(self, row):
        return self.model().item(row)

    def refreshData(self):
        mdl = self.model()
        mdl.clearData()
        for author in pdfrog.session.query(Author).limit(300):
            mdl.appendAuthor(author)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu:
            self.context_menu.exec_(QCursor.pos())
            return True
        else:
            return QTableView.eventFilter(self, obj, event)

    def removeSelectedAuthors(self):
        idxs = self.selectionModel().selectedRows()
        if len(idxs) == 0: return

        author_name_list = [self.item(idx.row()).name for idx in idxs]

        if any([self.item(idx.row()).getArticleCount() != 0 for idx in idxs]):
            # some authors have at least one article
            QMessageBox.warning(self, "Author removal", \
                "Can't remove authors with articles. Sorry.")
            return

        res = QMessageBox.question(self, "Author removal", \
            "Do you want to remove following authors from database:\n" + \
            ", ".join(author_name_list) + " ?", \
            buttons = QMessageBox.Ok | QMessageBox.Cancel)
        if res == QMessageBox.Ok:
            for idx in idxs:
                author = self.item(idx.row())
                author.removeFromDatabase()

            self.refreshData()

class AuthorListModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.datastore = []
        self.view = parent

    COLUMN_NAME = 0
    COLUMN_ORGANIZATION = 1
    COLUMN_ARTICLE_COUNT = 2
    COLUMN_ARTICLE_TAGS = 3

    def rowCount(self, parent=None):
        return len(self.datastore)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid(): return None

        if role == Qt.DisplayRole:
            column = index.column()
            if column == self.COLUMN_NAME:
                return self.datastore[index.row()].name
            elif column == self.COLUMN_ORGANIZATION:
                return self.datastore[index.row()].organization
            elif column == self.COLUMN_ARTICLE_COUNT:
                return self.datastore[index.row()].getArticleCount()
            elif column == self.COLUMN_ARTICLE_TAGS:
                tag_names = [tag.name for tag in self.datastore[index.row()].getArticleTags()]
                return ", ".join(tag_names)
            else:
                return "unknown"
        else:
            return None

    def headerData(self, column, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if column == self.COLUMN_NAME: return "Name"
                elif column == self.COLUMN_ORGANIZATION: return "Organization"
                elif column == self.COLUMN_ARTICLE_COUNT: return "Article Count"
                elif column == self.COLUMN_ARTICLE_TAGS: return "Article Tags"
                else:
                    return "Unknown"
        return None

    def appendAuthor(self, author):
        self.beginInsertRows(QModelIndex(), len(self.datastore), len(self.datastore))
        self.datastore.append(author)
        self.endInsertRows()

    def clearData(self):
        self.modelReset.emit()
        self.datastore = []

    def sort(self, column, order):
        def tags_sort_key(obj):
            return ", ".join([tag.name for tag in obj.getArticleTags()])
        def name_sort_key(obj):
            return obj.name if obj.name is not None else ""
        def organization_sort_key(obj):
            return obj.organization if obj.organization is not None else ""

        reverse = (order == Qt.DescendingOrder)
        self.layoutAboutToBeChanged.emit()
        if column == self.COLUMN_NAME:
            self.datastore = sorted(self.datastore, key=name_sort_key, reverse=reverse)
        elif column == self.COLUMN_ORGANIZATION:
            self.datastore = sorted(self.datastore, key=organization_sort_key, reverse=reverse)
        elif column == self.COLUMN_ARTICLE_COUNT:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.getArticleCount(), reverse=reverse)
        elif column == self.COLUMN_ARTICLE_TAGS:
            self.datastore = sorted(self.datastore, key=tags_sort_key, reverse=reverse)
        self.layoutChanged.emit()

    def item(self, row):
        return self.datastore[row]
