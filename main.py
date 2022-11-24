import sys
import os
import re

from PyPDF2 import PdfReader
from PyQt6 import uic, QtCore
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QCheckBox,
    QLabel,
)

HOME_PATH = os.getenv("HOME")


# TODO module
def get_documents_and_pages(
    dir_path: str,
    query: str,
    regex: bool,
    case_sensitive: bool,
    file_types: tuple,
) -> [(str, dict)]:
    documents = []
    if regex:
        query = re.compile(query)
    for document in os.scandir(dir_path):
        document_path = document.path
        if not document_path.endswith(file_types):
            continue

        if ".pdf" in file_types and document_path.endswith(".pdf"):
            reader = PdfReader(document_path)
            pages = {}
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if not case_sensitive:
                    text = text.lower()
                if regex:
                    matches = len(query.findall(text))
                    if matches:
                        pages[i + 1] = len(query.findall(text))
                else:
                    if query in text:
                        pages[i + 1] = text.count(query)
            if pages:
                documents.append((document_path, pages))

        if ".TODO" in file_types and document_path.endswith(".TODO"):
            pass  # TODO

    return sorted(documents, key=lambda x: sum(x[1].values()), reverse=True)


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        # load ui file
        uic.loadUi("design.ui", self)

        # define widgets
        # menu-bar
        _translate = QtCore.QCoreApplication.translate
        self.actionExit = self.findChild(QAction, "actionExit")
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+X"))
        self.actionExit.triggered.connect(
            lambda: QtCore.QCoreApplication.instance().quit()
        )
        # main-window
        self.pushButton_browse = self.findChild(QPushButton, "pushButton_browse")
        self.pushButton_browse.clicked.connect(self.get_dir_path)
        self.pushButton_run = self.findChild(QPushButton, "pushButton_run")
        self.pushButton_run.clicked.connect(self.query)
        self.lineEdit_path = self.findChild(QLineEdit, "lineEdit_path")
        self.lineEdit_query = self.findChild(QLineEdit, "lineEdit_query")
        self.checkBox_regex = self.findChild(QCheckBox, "checkBox_regex")
        self.checkBox_case_sensitive = self.findChild(
            QCheckBox, "checkBox_case_sensitive"
        )
        self.checkBox_file_format_pdf = self.findChild(
            QCheckBox, "checkBox_file_format_pdf"
        )
        self.checkBox_file_format_txt = self.findChild(
            QCheckBox, "checkBox_file_format_txt"
        )
        self.checkBox_file_format_xlsx = self.findChild(
            QCheckBox, "checkBox_file_format_xlsx"
        )
        self.checkBox_file_format_docx = self.findChild(
            QCheckBox, "checkBox_file_format_docx"
        )
        self.checkBox_file_format_html = self.findChild(
            QCheckBox, "checkBox_file_format_html"
        )
        self.checkBox_file_format_pptx = self.findChild(
            QCheckBox, "checkBox_file_format_pptx"
        )
        self.label_output = self.findChild(QLabel, "label_output")
        # TODO config
        # view
        self.show()

    def get_dir_path(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select directory",
            directory=HOME_PATH,
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        self.lineEdit_path.setText(dir_path)

    def query(self) -> None:
        dir_path = self.lineEdit_path.text()
        query = self.lineEdit_query.text()
        regex: bool = self.checkBox_regex.isChecked()
        case_sensitive: bool = self.checkBox_case_sensitive.isChecked()
        # TODO file type enum
        pdf: [str, bool] = (".pdf", self.checkBox_file_format_pdf.isChecked())
        txt: [str, bool] = (".txt", self.checkBox_file_format_txt.isChecked())
        xlsx: [str, bool] = (".xlsx", self.checkBox_file_format_xlsx.isChecked())
        docx: [str, bool] = (".docx", self.checkBox_file_format_docx.isChecked())
        html: [str, bool] = (".html", self.checkBox_file_format_html.isChecked())
        pptx: [str, bool] = (".pptx", self.checkBox_file_format_pptx.isChecked())
        file_types = tuple([t[0] for t in [pdf, txt, xlsx, docx, html, pptx] if t[1]])
        # TODO start end time filter

        try:
            documents_and_pages = get_documents_and_pages(
                dir_path, query, regex, case_sensitive, file_types
            )
            # TODO format output
            self.label_output.setText(str(documents_and_pages))
            # TODO file viewer
        except FileNotFoundError:
            self.label_output.setText("Error! Invalid directory path.")


if __name__ == "__main__":
    # init app
    app = QApplication(sys.argv)
    ui_window = UI()
    app.exec()
