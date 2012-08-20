# -*- coding: utf-8 -*-
# file: pdfrog/__init__.py
import sqlalchemy as sa
import sqlalchemy.orm
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from pdfrog.mainwnd import MainWnd
from pdfrog.datamodel import Article, Author, Base
from tempfile import mkdtemp
from sqlalchemy import create_engine

tmpdir = mkdtemp('', 'pdfrog_')

session = None

class pdfrog:
    def __init__(self):
        pass

    def __setup_tables(self):
        global session
        show_sa_debug = False
        self.engine = sa.create_engine ('sqlite:///db.db', echo=show_sa_debug)
        Session = sa.orm.sessionmaker()
        session = Session (bind = self.engine)
        Base.metadata.create_all (self.engine)

    def run(self):
        self.__setup_tables()
        session.commit()

        app = QApplication(sys.argv)
        QTextCodec.setCodecForCStrings (QTextCodec.codecForName("UTF-8"))

        mainwnd = MainWnd()
        mainwnd.show()
        sys.exit(app.exec_())
