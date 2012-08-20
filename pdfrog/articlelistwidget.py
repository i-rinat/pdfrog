# -*- coding: utf-8 -*-
# file: pdfrog/articlelistwidget.py
from PySide.QtGui import *
from PySide.QtCore import *
from pdfrog.datamodel import Article
from pdfrog.editarticledialog import EditArticleDialog
import pdfrog

class ArticleList(QTableView):
    def __init__(self, *args):
        QTableView.__init__(self, *args)
        mdl = ArticleListModel(self)
        self.setModel(mdl)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setHighlightSections(False)
        self.installEventFilter(self)
        self.setAcceptDrops(True)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # connect signals
        self.horizontalHeader().sectionResized.connect(self.__handle_headerSectionResized)
        self.activated.connect(self.handle_activated)
        # make scrolling smoother
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # fill list with initial data
        self.query = None
        self.refreshData()

    def createMenu(self, article_menu):
        article_edit_title_action = QAction('Edit title', self)
        article_edit_title_action.setShortcut('F2')
        article_edit_title_action.triggered.connect(self.editSelectedArticlesTitle)

        article_edit_action = QAction('Edit ...', self)
        article_edit_action.triggered.connect(self.editSelectedArticle)

        article_delete_action = QAction("Delete", self)
        article_delete_action.setShortcut('Del')
        article_delete_action.triggered.connect(self.deleteSelectedArticles)

        article_open_action = QAction("Open (external)", self)
        article_open_action.setShortcut('Ctrl++')
        article_open_action.triggered.connect(self.openSelectedArticlesExternal)

        article_add_tag_action = QAction("Add tag by name ...", self)
        article_add_tag_action.triggered.connect(self.addTagToSelectedArticles)

        article_remove_tag_action = QAction("Remove tag by name ...", self)
        article_remove_tag_action.triggered.connect(self.removeTagFromSelectedArticles)

        article_refresh_list_action = QAction(QIcon.fromTheme("view-refresh"), "Refresh list", self)
        article_refresh_list_action.triggered.connect(self.refreshData)

        article_menu.addAction(article_refresh_list_action)
        article_menu.addAction(article_edit_title_action)
        article_menu.addAction(article_add_tag_action)
        article_menu.addAction(article_remove_tag_action)
        article_menu.addSeparator()
        article_menu.addAction(article_open_action)
        article_menu.addAction(article_edit_action)
        article_menu.addAction(article_delete_action)

        self.context_menu = article_menu

    def __handle_headerSectionResized(self, idx, oldsize, newsize):
        self.resizeRowsToContents()

    def deleteSelectedArticles(self):
        """deletes selected articles from database"""
        selected_rows = self.selectionModel().selectedRows()
        if len(selected_rows) == 0:   # nothing to delete
            return
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Question)
        mb.addButton(QMessageBox.Yes)
        mb.addButton(QMessageBox.No)
        mb.setWindowTitle('Delete')
        text = 'Do you want to remove these articles from database:\n\n' + \
            ',\n'.join(['"'+self.model().data(idx)+'"' for idx in selected_rows]) + \
            ' ?\n'
        mb.setText(text)
        res = mb.exec_()
        if QMessageBox.Yes == res:
            article_list = [self.model().item(idx.row()) for idx in selected_rows];
            for a in article_list:
                self.model().deleteArticleByObject(a)
                pdfrog.session.delete(a)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu:
            self.context_menu.exec_(QCursor.pos())
            return True
        else:
            return QTableView.eventFilter(self, obj, event)

    def handle_activated(self, index):
        article = self.item(index.row())
        Article.openExternal(article)

    def openSelectedArticlesExternal(self):
        """launches external viewer for selected articles"""
        idxs = self.selectionModel().selectedRows()
        if len(idxs) > 2:
            res = QMessageBox.question(self, "Open articles", \
                "Do you want to open {0} articles?".format(len(idxs)), \
                buttons = QMessageBox.Ok | QMessageBox.Cancel,
                default_button = QMessageBox.Ok)
            if res == QMessageBox.Cancel:
                return
        for item in idxs:
            Article.openExternal(self.item(item.row()))

    def editSelectedArticlesTitle(self):
        """edit title of first selected article"""
        if len(self.selectedIndexes()) != 0:    # something selected
            idx = self.selectedIndexes()
            self.edit(idx[0])  # edit first selected row

    def editSelectedArticle(self):
        idxs = self.selectedIndexes()
        if len(idxs) != 0:    # something selected
            ead = EditArticleDialog(self, self.item(idxs[0].row()))
            ead.exec_()
            self.dataChanged(idxs[0], idxs[0])

    def appendArticle(self, obj):
        if type(obj) is not Article:
            raise Exception("is not Article")
        self.model().appendArticle(obj)

    def removeAllArticles(self):
        self.model().clearData()

    def item(self, row):
        return self.model().item(row)

    def addTagToSelectedArticles(self):
        idxs = self.selectionModel().selectedRows()
        if len(idxs) == 0: return
        (tag_name, ok_pressed) = QInputDialog.getText(self, "Add tag", "Tag:")
        if ok_pressed and tag_name != '':
            for idx in idxs:
                self.item(idx.row()).addTagByName(tag_name)
                self.dataChanged(idx, idx)

    def removeTagFromSelectedArticles(self):
        idxs = self.selectionModel().selectedRows()
        if len(idxs) == 0: return
        (tag_name, ok_pressed) = QInputDialog.getText(self, "Remove tag", "Tag:")
        if ok_pressed and tag_name != '':
            for idx in idxs:
                self.item(idx.row()).removeTagByName(tag_name)
                self.dataChanged(idx, idx)

    def refreshData(self, query=None):
        if query is None:
            query = self.query or pdfrog.session.query(Article).limit(300)
        self.query = query
        mdl = self.model()
        mdl.clearData()
        item_count = 0
        for article in query:
            mdl.appendArticle(article)
            item_count += 1
        self.resizeRowsToContents()
        return item_count


class ArticleListModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.datastore = []
        self.view = parent

    COLUMN_TITLE = 0
    COLUMN_MD5 = 1
    COLUMN_MIME = 2
    COLUMN_AUTHORS = 3
    COLUMN_TAGS = 4

    def rowCount(self, parent = None):
        return len(self.datastore)

    def columnCount(self, parent = None):
        return 5

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            if index.column() == self.COLUMN_TITLE:
                return self.datastore[index.row()].title
            elif index.column() == self.COLUMN_MD5:
                return self.datastore[index.row()].md5
            elif index.column() == self.COLUMN_MIME:
                mime = self.datastore[index.row()].filemime
                compr = self.datastore[index.row()].filecompr
                if compr is not None: mime += " ("+compr+")"
                return mime
            elif index.column() == self.COLUMN_AUTHORS:
                article = self.datastore[index.row()]
                author_string = ", ".join(author.name \
                  for author in article.authors[0:3] if author.name is not None)
                if len(article.authors) > 3:
                    author_string += ", et. al."
                return author_string
            elif index.column() == self.COLUMN_TAGS:
                article = self.datastore[index.row()]
                tag_string = ", ".join(tag.name for tag in article.tags)
                return tag_string
            else:
                return "Unknown"
        elif role == Qt.EditRole:
            return self.datastore[index.row()].title
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.datastore[index.row()].title = value
            return True
        return False

    def flags(self, index):
        flags = super(self.__class__,self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        if column == self.COLUMN_TITLE:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.title, reverse=(order == Qt.DescendingOrder))
        elif column == self.COLUMN_MD5:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.md5, reverse=(order == Qt.DescendingOrder))
        elif column == self.COLUMN_MIME:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.filemime, reverse=(order == Qt.DescendingOrder))
        elif column == self.COLUMN_AUTHORS:
            # TODO: should I sort by authors?
            pass # do nothing
        elif column == self.COLUMN_TAGS:
            pass
        self.layoutChanged.emit()

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == self.COLUMN_TITLE: return "Title"
            elif column == self.COLUMN_MD5: return "md5"
            elif column == self.COLUMN_MIME: return "mime"
            elif column == self.COLUMN_AUTHORS: return "Authors"
            elif column == self.COLUMN_TAGS: return "Tags"
            else:
                return "Unnamed column"
        else:
            return None

    def appendArticle(self, obj):
        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)
        self.datastore.append(obj)
        self.endInsertRows()

    def deleteArticleByObject(self, obj):
        row = self.datastore.index(obj)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.datastore.remove(obj)
        self.endRemoveRows()

    def clearData(self):
        self.modelReset.emit()
        self.datastore = []

    def item(self, row):
        return self.datastore[row]
