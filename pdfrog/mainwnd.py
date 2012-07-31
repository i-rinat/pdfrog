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

        self.author_list = AuthorList(parent=self)
        self.author_list.show()

        self.tag_list = TagList()
        self.tag_list.show()

        self.article_search_bar = QLineEdit();
        self.article_search_bar.setPlaceholderText('Filter articles...')
        self.article_search_bar.returnPressed.connect(self.articleSearchBarReturnPressed)
        article_search_button = QPushButton("→")
        article_search_button.clicked.connect(self.articleSearchBarReturnPressed)

        self.author_search_bar = QLineEdit()
        self.author_search_bar.setPlaceholderText('Filter authors...')
        self.author_search_bar.returnPressed.connect(self.authorSearchBarReturnPressed)
        author_search_button = QPushButton("→")
        author_search_button.clicked.connect(self.authorSearchBarReturnPressed)

        self.tag_search_bar = QLineEdit()
        self.tag_search_bar.setPlaceholderText('Filter tags...')
        self.tag_search_bar.returnPressed.connect(self.tagSearchBarReturnPressed)
        tag_search_button = QPushButton("→")
        tag_search_button.clicked.connect(self.tagSearchBarReturnPressed)

        tab_widget = QTabWidget()
        self.tab_widget = tab_widget

        # article list page
        box1 = QGridLayout()
        box1.addWidget(self.article_search_bar, 0, 0)
        box1.addWidget(article_search_button, 0, 1)
        box1.addWidget(self.article_list, 1, 0, 1, 2)
        articles_compaund_page = QWidget()
        articles_compaund_page.setLayout(box1)
        tab_widget.addTab(articles_compaund_page, "Articles")

        # author list page
        box2 = QGridLayout()
        box2.addWidget(self.author_search_bar, 0, 0)
        box2.addWidget(author_search_button, 0, 1)
        box2.addWidget(self.author_list, 1, 0, 1, 2)
        authors_compound_page = QWidget()
        authors_compound_page.setLayout(box2)
        tab_widget.addTab(authors_compound_page, "Authors")

        # tag list page
        box3 = QGridLayout()
        box3.addWidget(self.tag_search_bar, 0, 0)
        box3.addWidget(tag_search_button, 0, 1)
        box3.addWidget(self.tag_list, 1, 0, 1, 2)
        tags_compound_page = QWidget()
        tags_compound_page.setLayout(box3)
        tab_widget.addTab(tags_compound_page, "Tags")
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

        db_menu = self.menuBar().addMenu("Database")
        db_menu.addAction(open_action)
        db_menu.addAction(save_action)
        db_menu.addSeparator()
        db_menu.addAction(add_files_action)
        db_menu.addSeparator()
        db_menu.addAction(exit_action)

        self.article_menu = self.menuBar().addMenu("Article")
        self.article_menu.setEnabled(True)
        self.article_list.createMenu(self.article_menu)

        self.author_menu = self.menuBar().addMenu("Author")
        self.author_menu.setEnabled(False)
        self.author_list.createMenu(self.author_menu)

        self.tag_menu = self.menuBar().addMenu("Tag")
        self.tag_menu.setEnabled(False)
        self.tag_list.createMenu(self.tag_menu)

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
            elif keyword[0:12] == "authorexact:":
                authorname = keyword[12:]
                query = query.join(Article.authors).filter(Author.name == authorname)
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

    def findArticlesByAuthorName(self, authorname):
        self.selectTab("articles")
        self.article_search_bar.setText('authorexact:"{}"'.format(authorname.replace('"', r'\"')))
        self.articleSearchBarReturnPressed()

    def selectTab(self, tab):
        # TODO: I use hardcoded tab order
        if tab == "articles":
            self.tab_widget.setCurrentIndex(0)
        elif tab == "authors":
            self.tab_widget.setcurrentIndex(1)
        elif tab == "tags":
            self.tab_widget.setCurrentIndex(2)

    def authorSearchBarReturnPressed(self):
        self.statusBar().showMessage('Filtering authors...')
        self.statusBar().repaint()
        query_list = []
        for keyword in shlex.split(self.author_search_bar.text()):
            keyword = keyword.decode()
            query = pdfrog.session.query(Author)
            if keyword[0:4] == "org:":
                query = query.filter(Author.organization.like("%{}%".format(keyword[4:])))
            elif keyword[0:9] == "orgexact:":
                query = query.filter(Author.organization == keyword[9:])
            elif keyword[0:4] == "tag:":
                query = query.join(Author.articles).join(Article.tags)
                query = query.filter(Tag.name==keyword[4:])
            else:
                query = query.filter(Author.name.like("%{}%".format(keyword)))
            query_list.append(query)

        query = pdfrog.session.query(Author).intersect(*query_list)
        item_count = self.author_list.refreshData(query)
        self.statusBar().showMessage('{} author(s)'.format(item_count))

    def tagSearchBarReturnPressed(self):
        self.statusBar().showMessage('Filtering tags...')
        self.statusBar().repaint()
        query_list = []
        for keyword in shlex.split(self.tag_search_bar.text()):
            keyword = keyword.decode()
            query = pdfrog.session.query(Tag)
            query = query.filter(Tag.name.like("%{}%".format(keyword)))
            query_list.append(query)

        query = pdfrog.session.query(Tag).intersect(*query_list)
        item_count = self.tag_list.refreshData(query)
        self.statusBar().showMessage('{} tag(s)'.format(item_count))
