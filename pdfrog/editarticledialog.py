# -*- coding: utf-8 -*-
# file: pdfrog/editarticledialog.py
from PySide.QtCore import *
from PySide.QtGui import *
from pdfrog.datamodel import Article
from pdfrog.editarticleauthorsdialog import EditArticleAuthorsDialog
from pdfrog.editarticletagsdialog import EditArticleTagsDialog
import pdfrog

class EditArticleDialog(QDialog):
    def __init__(self, parent, article):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.article = article
        if article == None:
            raise Exception('You must supply article object')
        if type(article) is not Article:
            raise Exception('Expected object of Article class')

        self.setWindowTitle('Edit article')
        self.createWidgets()
        self.updateAuthorList()
        self.updateTagList()

    def createWidgets(self):
        # creating widgets
        self.article_title = QLineEdit()
        self.open_button = QPushButton('View article')
        self.journal_name = QLineEdit()
        self.journal_select_button = QPushButton('Select')
        self.author_list = QListWidget()
        self.edit_author_list_button = QPushButton('Edit author list')
        self.tag_list = QListWidget()
        self.edit_tag_list_button = QPushButton('Edit tag list')
        dialog_button_box = QDialogButtonBox()
        dialog_button_box.addButton("Close", QDialogButtonBox.AcceptRole)

        # set up widget properties
        self.journal_name.setReadOnly(True)
        self.article_title.setText(self.article.title)

        # signals
        dialog_button_box.accepted.connect(self.accept)
        self.edit_author_list_button.clicked.connect(self.editArticleAuthors)
        self.edit_tag_list_button.clicked.connect(self.editArticleTags)

        # widget packing
        main_vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(QLabel('Title:'))
        hbox1.addWidget(self.article_title, stretch=1)
        hbox1.addWidget(self.open_button)
        main_vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel('Journal:'))
        hbox2.addWidget(self.journal_name, stretch=2)
        hbox2.addWidget(self.journal_select_button, stretch=0)
        hbox2.addStretch(stretch=1)
        main_vbox.addLayout(hbox2)

        vbox_authors = QVBoxLayout()
        vbox_authors.addWidget(QLabel('Authors'))
        vbox_authors.addWidget(self.author_list, stretch=1)
        vbox_authors.addWidget(self.edit_author_list_button, stretch=0)

        vbox_tags = QVBoxLayout()
        vbox_tags.addWidget(QLabel('Tags'))
        vbox_tags.addWidget(self.tag_list, stretch=1)
        vbox_tags.addWidget(self.edit_tag_list_button, stretch=0)

        hbox3 = QHBoxLayout()
        hbox3.addLayout(vbox_authors, stretch=1)
        hbox3.addLayout(vbox_tags, stretch=1)
        main_vbox.addLayout(hbox3, stretch=1)

        main_vbox.addWidget(dialog_button_box)
        self.setLayout(main_vbox)

    def accept(self):
        self.article.title = self.article_title.text()
        pdfrog.session.flush()
        QDialog.accept(self)

    def reject(self):
        pdfrog.session.flush()
        QDialog.reject(self)

    def editArticleAuthors(self):
        aad = EditArticleAuthorsDialog(self, self.article)
        aad.exec_()
        self.updateAuthorList()

    def editArticleTags(self):
        eat = EditArticleTagsDialog(self, self.article)
        eat.exec_()
        self.updateTagList()

    def updateAuthorList(self):
        self.author_list.clear()
        for author in self.article.authors:
            self.author_list.addItem(author.name)

    def updateTagList(self):
        self.tag_list.clear()
        for tag in self.article.tags:
            self.tag_list.addItem(tag.name)
