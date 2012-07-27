# -*- coding: utf-8 -*-
import sys
import pdfrog

if __name__ == "__main__":
    if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf-8')
    w = pdfrog.pdfrog()
    w.run()
