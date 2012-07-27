# -*- coding: utf-8 -*-

from PySide.QtGui import *
from PySide.QtCore import *
from pdfrog.datamodel import Article, Tag, Author
from pdfrog.addfiledialog import AddFileDialog
from pdfrog.articlelistwidget import ArticleList
from .taglistwidget import TagList
from .authorlistwidget import AuthorList
import pdfrog
import tempfile
import subprocess
import os
import shlex

class MainWnd (QMainWindow):
    def __init__(self, parent=None):
        super(MainWnd, self).__init__(parent)
        self.setWindowTitle("pdfrog")
        self.resize(600, 400)
        self.setAcceptDrops(True)

        self.createWidgets()
        self.createMenus()
        self.statusBar()
        self.article_query = pdfrog.session.query(Article).limit(1000)

    def createWidgets(self):
        self.article_list = ArticleList()
        self.article_list.show()

        self.author_list = AuthorList()
        self.author_list.show()

        self.tag_list = TagList()
        self.tag_list.show()

        self.article_search_bar = QLineEdit();
        self.article_search_bar.setPlaceholderText('Filter...')
        self.article_search_bar.returnPressed.connect(self.articleSearchBarReturnPressed)

        vbox = QVBoxLayout()
        vbox.addWidget(self.article_search_bar)
        vbox.addWidget (self.article_list)
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        tab_widget = QTabWidget()
        self.tab_widget = tab_widget
        tab_widget.addTab(central_widget, "Articles")
        tab_widget.addTab(self.author_list, "Authors")
        tab_widget.addTab(self.tag_list, "Tags")
        tab_widget.currentChanged.connect(self.tabCurrentPageChanged)
        self.setCentralWidget(tab_widget)

    def createMenus(self):
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openDatabase)

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveDatabase)

        add_files_action = QAction('Add files...', self)
        add_files_action.triggered.connect(self.addFilesDialog)

        article_edit_title_action = QAction('Edit title', self)
        article_edit_title_action.setShortcut('F2')
        article_edit_title_action.triggered.connect(self.article_list.editSelectedArticlesTitle)

        article_edit_action = QAction('Edit ...', self)
        article_edit_action.triggered.connect(self.article_list.editSelectedArticle)

        delete_article_action = QAction("Delete", self)
        delete_article_action.setShortcut('Del')
        delete_article_action.triggered.connect(self.article_list.deleteSelectedArticles)

        article_open_action = QAction("Open (external)", self)
        article_open_action.setShortcut('Ctrl++')
        article_open_action.triggered.connect(self.article_list.openSelectedArticlesExternal)

        article_add_tag_action = QAction("Add tag by name ...", self)
        article_add_tag_action.triggered.connect(self.article_list.addTagToSelectedArticles)

        article_remove_tag_action = QAction("Remove tag by name ...", self)
        article_remove_tag_action.triggered.connect(self.article_list.removeTagFromSelectedArticles)

        author_remove_action = QAction("Remove", self)
        author_remove_action.setShortcut('Del')
        author_remove_action.triggered.connect(self.author_list.removeSelectedAuthors)

        tag_remove_action = QAction("Remove", self)
        tag_remove_action.triggered.connect(self.tag_list.removeSelectedTags)

        tag_rename_action = QAction("Rename", self)
        tag_rename_action.triggered.connect(self.tag_list.renameSelectedTag)

        tag_discharge_action = QAction("Discharge", self)
        tag_discharge_action.triggered.connect(self.tag_list.dischargeSelectedTags)

        db_menu = self.menuBar().addMenu("Database")
        db_menu.addAction(open_action)
        db_menu.addAction(save_action)
        db_menu.addSeparator()
        db_menu.addAction(add_files_action)
        db_menu.addSeparator()
        db_menu.addAction(exit_action)

        article_menu = self.menuBar().addMenu("Article")
        self.article_menu = article_menu
        article_menu.addAction(article_edit_title_action)
        article_menu.addAction(article_add_tag_action)
        article_menu.addAction(article_remove_tag_action)
        article_menu.addSeparator()
        article_menu.addAction(article_open_action)
        article_menu.addAction(article_edit_action)
        article_menu.addAction(delete_article_action)

        author_menu = self.menuBar().addMenu("Author")
        author_menu.setEnabled(False)
        self.author_menu = author_menu
        author_menu.addAction(author_remove_action)

        tag_menu = self.menuBar().addMenu("Tag")
        tag_menu.setEnabled(False)
        self.tag_menu = tag_menu
        tag_menu.addAction(tag_remove_action)
        tag_menu.addAction(tag_rename_action)
        tag_menu.addAction(tag_discharge_action)

        # context menus
        self.article_list.context_menu = self.article_menu
        self.author_list.context_menu = self.author_menu
        self.tag_list.context_menu = tag_menu

    def openDatabase(self):
        QMessageBox.information(self, "Open", "This function has not implemented yet.")

    def saveDatabase(self):
        pdfrog.session.commit()
        self.statusBar().showMessage('Saved')

    def tabCurrentPageChanged(self, index):
        # TODO: get rid of hardcoded tabwidget page order
        self.article_menu.setEnabled(index == 0)
        self.author_menu.setEnabled(index == 1)
        self.tag_menu.setEnabled(index == 2)

    def addFilesDialog(self):
        fl = QFileDialog.getOpenFileNames(self, filter="PDF documents (*.pdf);; All Files (*.*)", selectedFilter="*.pdf")
        self.addFiles(fl[0])

    def addFiles(self, filelist):
        total_documents = len(filelist)
        doc_idx = 1
        for filename in filelist:
            afd = AddFileDialog()
            afd.setTotalCount(total_documents)
            afd.setCurrent(doc_idx)
            afd.setFileName(filename)
            afd.exec_()
            doc_idx += 1
        self.refreshArticleList()

    def closeEvent(self, event):
        from time import sleep
        self.statusBar().showMessage('Saving changes to database (please wait) ...')
        self.statusBar().repaint()
        pdfrog.session.commit()
        self.statusBar().showMessage('Saved')
        self.statusBar().repaint()
        QMainWindow.closeEvent(self, event)

    def refreshArticleList(self):
        self.article_list.removeAllArticles()
        for article in self.article_query:
            self.article_list.appendArticle(article)
        article_count = self.article_query.count()
        self.statusBar().showMessage(str(article_count) + " article(s)")
        self.article_list.resizeRowsToContents()

    def dropEvent(self, event):
        self.addFiles(self.__drop_files)

    def dragEnterEvent(self, event):
        md = event.mimeData()
        if md.hasUrls():
            self.__drop_files = [url.toLocalFile() for url in md.urls()]
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def articleSearchBarReturnPressed(self):
        query_list = []
        for keyword in shlex.split(self.article_search_bar.text()):
            # shlex.split have some kind of difficulties with unicode
            keyword = keyword.decode()
            query = pdfrog.session.query(Article)
            if keyword[0:4] == "tag:":
                tagname = keyword[4:]
                query = query.join(Article.tags).filter(Tag.name==tagname)
            elif keyword[0:7] == "author:":
                authorname = keyword[7:]
                query = query.join(Article.authors).filter(Author.name.like('%'+authorname+'%'))
            else:
                likestr = '%' + keyword + '%'
                query = query.filter(Article.title.like(likestr))
            query_list.append(query)
        # intersect queries
        query = pdfrog.session.query(Article)
        query = query.intersect(*query_list)

        self.article_query = query
        self.statusBar().showMessage('Filtering ...')
        self.statusBar().repaint()
        self.refreshArticleList()
        #self.statusBar().showMessage('Ok')
