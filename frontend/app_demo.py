from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QMessageBox, QMainWindow, QApplication, QTableWidget, QTableWidgetItem, QToolBar, QStatusBar, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets

import os
import sys
from functools import partial
import matplotlib.pyplot as plt
import subprocess

from backend import baseDb as base
from backend import labels
from frontend import charts


_db_path = os.path.abspath('%s' % (labels.DB_FILE,))
_icons_folder_path = os.path.abspath('frontend/icon')


# Okno wyboru tabeli
class ShowTableData(QDialog):
    def __init__(self, *args, **kwargs):
        super(ShowTableData, self).__init__(*args, **kwargs)

        self.title = "Proszę wybrać dane do wyświetlenia:"
        self.width = 300
        self.height = 200
        self.main_widget = QWidget()

        layout = QVBoxLayout(self.main_widget)

        self.QBtn = QPushButton()
        self.QBtn.setText("Dalej")
        self.QBtn.clicked.connect(self.get_table_data)
        # self.QBtn.setStyleSheet('background-color:blue; color:white; font-size:24px;')

        self.l1 = QLabel()
        self.l1.setText("Nazwa tabeli: ")
        self.l1.setAlignment(Qt.AlignLeft)
        self.l1.setFixedSize(self.width, 15)

        tables = base.select_tables(_db_path)
        print(_db_path)
        print(tables)
        self.select_el = QComboBox()
        if tables:
            for table in tables:
                name = '%s' % (table[0],)
                print(name)
                self.select_el.addItem(name)

        layout.addWidget(self.l1)
        layout.addWidget(self.select_el)
        layout.addWidget(self.QBtn)
        layout.setSpacing(10)
        layout.addStretch(0)
        # layout.setContentMargin(0, 0, 0, 0);

        self.setLayout(layout)
        self.s()


    def s(self):
        self.setWindowTitle(self.title)
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.show()

    def get_table_data(self):
        global global_table_name
        global global_table_schema
        global_table_name = self.select_el.itemText(self.select_el.currentIndex())
        try:
            table_cols = base.select_table_columns(_db_path, global_table_name)
            global_table_schema = (global_table_name,) + tuple(table_cols)
            self.accept()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Nie udało się pobrać wartości z bazy danych')
        return global_table_schema


# okno obostrzeń dla wyświetlanych wykresów
class ChartPanel(QDialog):
    def __init__(self, *args, **kwargs):
        super(ChartPanel, self).__init__(*args, **kwargs)

        self.title = "Wyświetl dane w formie graficznej"
        self.width = 500
        self.height = 650
        self.s()

        layout = QVBoxLayout()
        layout_V_1 = QVBoxLayout()
        layout_V_2 = QVBoxLayout()

        self.l1 = QLabel()
        self.l1.setText("Użytkownik: ")
        self.l1.setAlignment(Qt.AlignLeft)

        self.l2 = QLabel()
        self.l2.setText("Kurs: ")
        self.l2.setAlignment(Qt.AlignLeft)

        self.l3 = QLabel()
        self.l3.setText("Tabela: ")
        self.l3.setAlignment(Qt.AlignLeft)

        self.l4 = QLabel()
        self.l4.setText("Rodzaj: ")
        self.l4.setAlignment(Qt.AlignLeft)

        self.l5 = QLabel()
        self.l5.setText("Rok: ")
        self.l5.setAlignment(Qt.AlignLeft)

        self.user_box = QComboBox()
        self.user_box.setFixedSize(350, 20)
        self.user_box.currentTextChanged.connect(partial(self.on_users_combobox_changed, layout_V_1=layout_V_1))
        cols = '"%s", "%s", "%s"' % (labels.ID, labels.USER_NAME, labels.DEPARTMENT_ID)
        users_data = base.select_table_data_1(_db_path, labels.TABLE_USERS, cols)
        # print(users_data)
        if users_data:
            for user_data in users_data:
                self.userId = user_data[0]
                user = user_data[1]
                user_departmentId = user_data[2]

                cols = '"%s"' % (labels.DEPARTMENT_NAME,)
                condition = '"%s" = %s' % (labels.ID, user_departmentId)
                departaments_data = base.select_table_data_2(_db_path, labels.TABLE_DEPARTMENTS, cols, condition)
                # print(departaments_data)
                if departaments_data:
                    for departament_data in departaments_data:
                        show = '%s (Wydział: %s, userId: %s)' % (user, departament_data[0], self.userId)
                        self.user_box.addItem(show)

        self.tabel_type_box = QComboBox()
        self.tabel_type_box.currentTextChanged.connect(partial(self.on_tabel_type_box_combobox_changed, layout_V_2=layout_V_2))
        self.tabel_type_box.setFixedSize(350, 20)
        self.tabel_type_box.addItem(labels.TABLE_RESULTS)
        self.tabel_type_box.addItem(labels.TABLE_STATISTICS)

        self.QBtn_1 = QPushButton()
        self.QBtn_1.setText("Podgląd odpowiedzi P1 - P14")
        self.QBtn_1.clicked.connect(partial(self.printData, expectedResponseType=1))

        self.QBtn_2 = QPushButton()
        self.QBtn_2.setText("Podgląd szczegółów respondentów")
        self.QBtn_2.clicked.connect(partial(self.printData, expectedResponseType=2))

        self.QBtn_3 = QPushButton()
        self.QBtn_3.setText(labels.BOXPLOT)
        self.QBtn_3.clicked.connect(partial(self.printData, expectedResponseType=3))

        layout.addWidget(self.l1)
        layout.addWidget(self.user_box)
        layout.addStretch(0)
        layout.addWidget(self.l2)
        layout.addLayout(layout_V_1)
        layout.addStretch(0)
        layout.addWidget(self.l3)
        layout.addWidget(self.tabel_type_box)
        layout.addStretch(0)
        layout.addWidget(self.l4)
        layout.addLayout(layout_V_2)
        layout.addStretch(1)
        layout.addWidget(self.QBtn_3)
        layout.addStretch(0)
        layout.addWidget(self.QBtn_1)
        layout.addStretch(0)
        layout.addWidget(self.QBtn_2)
        layout.addStretch(1)

        self.setLayout(layout)


    def on_users_combobox_changed(self, value, layout_V_1):

        for i in range(layout_V_1.count()):
            child = layout_V_1.itemAt(i)
            if child:
                if child.widget():
                    child.widget().deleteLater()

        self.courses_box = QComboBox()
        self.courses_box.setFixedSize(350, 40)
        # print("combobox changed", value)
        cols = '"%s", "%s", "%s", "%s"' % (labels.ID, labels.COURSE_NAME, labels.YEAR, labels.TERM)
        userId = int(value.split('userId: ')[1].split(')')[0])
        condition = '"%s" = %s' % (labels.USER_ID, userId)
        courses_data = base.select_table_data_2(_db_path, labels.TABLE_COURSES, cols, condition)
        # print(courses_data)
        if courses_data:
            for course_data in courses_data:
                _courseId = course_data[0]
                _courseName = course_data[1]
                self._year = course_data[2]
                self._term = course_data[3]
                self._data = 'rok: %s, semestr: %s' % (self._year, self._term)
                show = '%s,\n (courseId: %s, rok: %s, semestr: %s)' % (_courseName, _courseId, self._year, self._term)
                self.courses_box.addItem(show)

            layout_V_1.addWidget(self.courses_box)
            layout_V_1.addStretch(1)

        else:
            info = QLabel()
            info.setText("Wybrany użytkownik nie ma przypisanego kursu.")
            info.setAlignment(Qt.AlignCenter)
            layout_V_1.addWidget(info)

    def on_tabel_type_box_combobox_changed(self, value, layout_V_2):
        for i in range(layout_V_2.count()):
            child = layout_V_2.itemAt(i)
            if child:
                if child.widget():
                    child.widget().deleteLater()
        table = self.tabel_type_box.itemText(self.tabel_type_box.currentIndex())

        # types_box
        self.types_box = QComboBox()
        self.types_box.setFixedSize(350, 20)
        if table == labels.TABLE_STATISTICS:
            cols = '"%s"' % (labels.COL_1,)
            types = base.select_table_data_1(_db_path, table, cols)

            # Removing duplicates
            types = list(set([i for i in types]))
            if types:
                for type in types:
                    show = '%s' % (type[0],)
                    self.types_box.addItem(show)

                layout_V_2.addWidget(self.types_box)
                layout_V_2.addStretch(1)
            else:
                info = QLabel()
                info.setText("Brak typu do wybrania.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_2.addWidget(info)
        else:
            info = QLabel()
            info.setText("Wskazana tabela nie zawiera szczegółowego rodzaju danych (odchylenie, średnia itp.)")
            info.setAlignment(Qt.AlignCenter)
            layout_V_2.addWidget(info)

        # attedance_box
        self.l6 = QLabel()
        self.l6.setText("Frekwencja respondentów: ")
        self.l6.setAlignment(Qt.AlignLeft)
        layout_V_2.addWidget(self.l6)

        self.attedance_box= QComboBox()
        self.attedance_box.setFixedSize(350, 20)
        if table == labels.TABLE_RESULTS:
            self.attedance_box.addItem(labels.ALL)
            cols = '"%s", "%s"' % (labels.COL_ATTENDANCE, labels.COL_ATTENDANCE_MAP)
            attedance = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                                 '"%s" IS NOT NULL' % (labels.COL_ATTENDANCE,))
            if attedance:
                for item in attedance:
                    self.attedance_box.addItem('%s (id: %s)' % (item[0], item[1]))

                layout_V_2.addWidget(self.attedance_box)
                layout_V_2.addStretch(1)
            else:
                info = QLabel()
                info.setText("Brak pola do wybrania.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_2.addWidget(info)
        else:
            info = QLabel()
            # info.setText("Wskazana tabela nie zawiera szczegółowego rodzaju danych (tj. frekwencji)")
            info.setText("--")
            info.setAlignment(Qt.AlignCenter)
            layout_V_2.addWidget(info)

        # presence_box
        self.l7 = QLabel()
        self.l7.setText("Obecność respondentów na pierwszych zajęciach: ")
        self.l7.setAlignment(Qt.AlignLeft)
        layout_V_2.addWidget(self.l7)
        self.presence_box = QComboBox()
        self.presence_box.setFixedSize(350, 20)
        if table == labels.TABLE_RESULTS:
            self.presence_box.addItem(labels.ALL)
            cols = '"%s", "%s"' % (labels.COL_PRESENCE, labels.COL_PRESENCE_MAP)
            presence = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                                '"%s" IS NOT NULL' % (labels.COL_PRESENCE,))
            if presence:
                for item in presence:
                    self.presence_box.addItem('%s (id: %s)' % (item[0], item[1]))

                layout_V_2.addWidget(self.presence_box)
                layout_V_2.addStretch(1)
            else:
                info = QLabel()
                info.setText("Brak pola do wybrania.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_2.addWidget(info)
        else:
            info = QLabel()
            # info.setText("Wskazana tabela nie zawiera szczegółowego rodzaju danych (tj, obecności)")
            info.setText("--")
            info.setAlignment(Qt.AlignCenter)
            layout_V_2.addWidget(info)

        # marks_box
        self.l8 = QLabel()
        self.l8.setText("Średnia ocen respondentów: ")
        self.l8.setAlignment(Qt.AlignLeft)
        layout_V_2.addWidget(self.l8)
        self.marks_box = QComboBox()
        self.marks_box.setFixedSize(350, 20)
        if table == labels.TABLE_RESULTS:
            self.marks_box.addItem(labels.ALL)
            cols = '"%s", "%s"' % (labels.COL_AVERAGE_MARKS, labels.COL_AVERAGE_MARKS_MAP)
            marks = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                             '"%s" IS NOT NULL' % (labels.COL_AVERAGE_MARKS,))
            if marks:
                for item in marks:
                    self.marks_box.addItem('%s (id: %s)' % (item[0], item[1]))

                layout_V_2.addWidget(self.marks_box)
                layout_V_2.addStretch(1)
            else:
                info = QLabel()
                info.setText("Brak pola do wybrania.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_2.addWidget(info)
        else:
            info = QLabel()
            # info.setText("Wskazana tabela nie zawiera szczegółowego rodzaju danych (tj, obecności)")
            info.setText("--")
            info.setAlignment(Qt.AlignCenter)
            layout_V_2.addWidget(info)

    def printData(self, expectedResponseType):
        if plt.get_fignums():
            # Figure is still opened
            plt.close('all')
        table = self.tabel_type_box.itemText(self.tabel_type_box.currentIndex())
        # print(table)
        userId = int(self.user_box.itemText(self.user_box.currentIndex()).split('userId: ')[1].split(')')[0])
        # print(userId)
        department_name = self.user_box.itemText(self.user_box.currentIndex()).split('Wydział: ')[1].split(',')[0]
        # print(department_name)
        cols = '"%s"' % (labels.ID,)
        condition = '"%s" = "%s"' % (labels.DEPARTMENT_NAME, department_name)
        departament_data = base.select_table_data_2(_db_path, labels.TABLE_DEPARTMENTS, cols, condition)
        departamentId = None
        if departament_data:
            departamentId = (departament_data[0])[0]

        courseId = None
        if self.courses_box:
            courseId = int(self.courses_box.itemText(self.courses_box.currentIndex()).split('courseId: ')[1].split(',')[0])

        type = None
        if self.types_box:
            type = self.types_box.itemText(self.types_box.currentIndex())

        attedanceId = None
        if self.attedance_box:
            text = self.attedance_box.itemText(self.attedance_box.currentIndex())
            if text != labels.ALL:
                attedanceId = int(text.split('id: ')[1].split(')')[0])

        presenceId = None
        if self.presence_box:
            text = self.presence_box.itemText(self.presence_box.currentIndex())
            if text != labels.ALL:
                presenceId = int(text.split('id: ')[1].split(')')[0])

        marksId = None
        if self.marks_box:
            text = self.marks_box.itemText(self.marks_box.currentIndex())
            if text != labels.ALL:
                marksId = int(text.split('id: ')[1].split(')')[0])

        if expectedResponseType == 1:
            charts.show_bar_chart(self=self, file=_db_path, table=table, userId=userId,
                                  departmentId=departamentId, courseId=courseId, type=type, attedanceId=attedanceId,
                                  presenceId=presenceId, marksId=marksId, show_columns=[labels.COL_QUESTION], year=self._data)
        elif expectedResponseType == 2:
            # print("INFO")
            # print(table, userId, departamentId, courseId, type, attedanceId, presenceId, marksId, year)
            # print("END_INFO")
            charts.show_respondent_data(self=self, file=_db_path, table=table, userId=userId,
                                        departmentId=departamentId, courseId=courseId, type=type, attedanceId=attedanceId,
                                        presenceId=presenceId, marksId=marksId,
                                        show_columns=[labels.COL_ATTENDANCE_2, labels.COL_PRESENCE, labels.COL_AVERAGE_MARKS], year=self._data)
        if expectedResponseType == 3:
            charts.show_boxplot_chart(self=self, file=_db_path, table=table, userId=userId,
                                      departmentId=departamentId, courseId=courseId, type=type, attedanceId=attedanceId,
                                      presenceId=presenceId, marksId=marksId, show_columns=[labels.COL_QUESTION], year=self._data)
        # else:
        #     QMessageBox.warning(self, 'Info', 'Niepoprawna definicja oczekiwanego rezultatu.')

    def s(self):
        self.setWindowTitle(self.title)
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.show()


# okno obostrzeń dla wyświetlanych plików pdf
class PdfPanel(QDialog):
    def __init__(self, *args, **kwargs):
        super(PdfPanel, self).__init__(*args, **kwargs)

        self.title = "Wyświetl komentarze jako pdf"
        self.width = 500
        self.height = 650
        self.s()

        layout = QVBoxLayout()
        layout_V_1 = QVBoxLayout()
        layout_V_2 = QVBoxLayout()


        self.l1 = QLabel()
        self.l1.setText("Użytkownik: ")
        self.l1.setAlignment(Qt.AlignLeft)

        self.l2 = QLabel()
        self.l2.setText("Kurs: ")
        self.l2.setAlignment(Qt.AlignLeft)

        self.user_box = QComboBox()
        self.user_box.setFixedSize(350, 20)
        self.user_box.currentTextChanged.connect(partial(self.on_users_combobox_changed, layout_V_1=layout_V_1, layout_V_2=layout_V_2))
        cols = '"%s", "%s", "%s"' % (labels.ID, labels.USER_NAME, labels.DEPARTMENT_ID)
        users_data = base.select_table_data_1(_db_path, labels.TABLE_USERS, cols)
        # print(users_data)
        if users_data:
            for user_data in users_data:
                self.userId = user_data[0]
                userName = user_data[1]
                user_departmentId = user_data[2]

                cols = '"%s"' % (labels.DEPARTMENT_NAME,)
                condition = '"%s" = %s' % (labels.ID, user_departmentId)
                departaments_data = base.select_table_data_2(_db_path, labels.TABLE_DEPARTMENTS, cols, condition)
                # print(departaments_data)
                if departaments_data:
                    for departament_data in departaments_data:
                        show = '%s (Wydział: %s, userId: %s)' % (userName, departament_data[0], self.userId)
                        self.user_box.addItem(show)

        self.QBtn_1 = QPushButton()
        self.QBtn_1.setText("Podgląd PDF")
        self.QBtn_1.clicked.connect(partial(self.openPDF, expectedResponseType=1))

        layout.addWidget(self.l1)
        layout.addWidget(self.user_box)
        layout.addStretch(0)
        layout.addWidget(self.l2)
        layout.addLayout(layout_V_1)
        layout.addStretch(0)
        layout.addLayout(layout_V_2)
        layout.addStretch(1)
        layout.addWidget(self.QBtn_1)
        layout.addStretch(1)

        self.setLayout(layout)

    def on_users_combobox_changed(self, value, layout_V_1, layout_V_2):
        # print('on_users_combobox_changed')
        # for i in range(layout_V_1.count()):
        #     print(i)

        for i in range(layout_V_1.count()):
            child = layout_V_1.itemAt(i)
            if child:
                if child.widget():
                    child.widget().deleteLater()

        # print("combobox changed", value)
        cols = '"%s", "%s"' % (labels.COMMENTS_FOLDER_ID, labels.COMMENTS_FOLDER_NAME)
        userId = int(value.split('userId: ')[1].split(')')[0])
        comments_folders_data = base.select_table_data_1(_db_path, labels.TABLE_MAP, cols)
        # print(comments_folders_data)
        comments_folders_data = [tuple(xi for xi in elem if xi is not None) for elem in comments_folders_data]
        comments_folders_data = [t for t in comments_folders_data if t != ()]
        # print(comments_folders_data)

        cols = '"%s"' % (labels.COMMENTS_FOLDER_ID,)
        condition = '"%s" = %s' % (labels.USER_ID, userId)
        available_folders_data = base.select_table_data_2(_db_path, labels.TABLE_PDF_FILES, cols, condition)
        available_folders_data = list(set(available_folders_data))

        available_folders_data = [item for t in available_folders_data for item in t]
        # print(available_folders_data)

        self.comments_folders_box = QComboBox()
        self.comments_folders_box.setFixedSize(350, 20)
        self.comments_folders_box.currentTextChanged.connect(
            partial(self.on_comments_combobox_changed, layout_V_2=layout_V_2, userId=userId))
        if comments_folders_data:
            for comments_folder_data in comments_folders_data:
                show = '%s, (id: %s)' % (comments_folder_data[1], comments_folder_data[0])
                if comments_folder_data[0] in available_folders_data:
                    self.comments_folders_box.addItem(show)
            if self.comments_folders_box.count() == 0:
                info = QLabel()
                info.setText("Wybrany użytkownik nie posiada folderów przedmiotów.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_1.addWidget(info)
            else:
                layout_V_1.addWidget(self.comments_folders_box)
        else:
            info = QLabel()
            info.setText("Wybrany użytkownik nie posiada folderów przedmiotów.")
            info.setAlignment(Qt.AlignCenter)
            layout_V_1.addWidget(info)

    def on_comments_combobox_changed(self, value, layout_V_2, userId):
        # print('on_comments_combobox_changed')
        for i in range(layout_V_2.count()):
            child = layout_V_2.itemAt(i)
            if child:
                if child.widget():
                    child.widget().deleteLater()
        self.l3 = QLabel()
        self.l3.setText("Typ komentarzy: ")
        self.l3.setAlignment(Qt.AlignLeft)
        layout_V_2.addWidget(self.l3)

        self.category_box = QComboBox()
        self.category_box.setFixedSize(350, 20)

        cols = '"%s", "%s"' % (labels.CATEGORY_ID, labels.CATEGORY_NAME)
        categories_data = base.select_table_data_1(_db_path, labels.TABLE_MAP, cols)
        # print(categories_data)
        categories_data = [tuple(xi for xi in elem if xi is not None) for elem in categories_data]
        categories_data = [t for t in categories_data if t != ()]
        # print(categories_data)

        commentFolderId = int(value.split('id: ')[1].split(')')[0])
        cols = '"%s"' % (labels.CATEGORY_ID,)
        condition = '"%s" = %s AND "%s" = %s' % \
                    (labels.USER_ID, userId, labels.COMMENTS_FOLDER_ID, commentFolderId)
        available_folders_data = base.select_table_data_2(_db_path, labels.TABLE_PDF_FILES, cols,
                                                          condition)
        available_folders_data = list(set(available_folders_data))
        available_folders_data = [item for t in available_folders_data for item in t]
        available_folders_data = list(map(int, available_folders_data))
        # print(available_folders_data)

        if categories_data:
            for category_data in categories_data:
                if category_data[0] in available_folders_data:
                    show = '%s, (id: %s)' % (category_data[1], category_data[0])
                    self.category_box.addItem(show)

            if self.category_box.count() == 0:
                info = QLabel()
                info.setText("Wybrany kurs nie posiada katalogów z komentarzami.")
                info.setAlignment(Qt.AlignCenter)
                layout_V_2.addWidget(info)
            else:
                layout_V_2.addWidget(self.category_box)
        else:
            info = QLabel()
            info.setText("Wybrany kurs nie posiada katalogów z komentarzami.")
            info.setAlignment(Qt.AlignCenter)
            layout_V_2.addWidget(info)

    def openPDF(self, expectedResponseType):
        userId = int(self.user_box.itemText(self.user_box.currentIndex()).split('userId: ')[1].split(')')[0])
        # print(userId)

        commentsFoldersId= None
        if self.comments_folders_box:
            commentsFoldersId = self.comments_folders_box.itemText(self.comments_folders_box.currentIndex()).split('id: ')[1].split(')')[0]

        categoryId = None
        if self.comments_folders_box:
            categoryId = self.category_box.itemText(self.category_box.currentIndex()).split('id: ')[1].split(')')[0]

        if expectedResponseType == 1:
            cols = '"%s"' % (labels.FILE_PATH,)
            condition = '"%s" = "%s" and "%s" = "%s" and "%s" = "%s"' % \
                        (labels.USER_ID, userId,
                         labels.COMMENTS_FOLDER_ID, commentsFoldersId,
                         labels.CATEGORY_ID, categoryId)
            file_path = base.select_table_data_2(_db_path, labels.TABLE_PDF_FILES, cols, condition)
            # print(file_path)
            if file_path:
                file_path = file_path[0]
                # print(file_path)
                file_path = '../%s' % (file_path[0],)
                # print(file_path)
                abs_file_path = os.path.abspath(file_path)
                print(abs_file_path)
                subprocess.Popen([abs_file_path], shell=True)
            else:
                QMessageBox.warning(self, 'Info', 'Ścieżka pliku nie istnieje.')
        else:
            QMessageBox.warning(self, 'Info', 'Niepoprawna definicja oczekiwanego rezultatu.')


    def s(self):
        self.setWindowTitle(self.title)
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.show()


# Edycja danych w głównym oknie
class EditableHeaderView(QtWidgets.QHeaderView):
    textChanged = QtCore.pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(EditableHeaderView, self).__init__(QtCore.Qt.Horizontal, parent)
        self._is_editable = dict()
        self.setSectionsClickable(True)
        self._lineedit = QtWidgets.QLineEdit(self, visible=False)
        self._lineedit.editingFinished.connect(self._lineedit.hide)
        self._lineedit.textChanged.connect(self.on_text_changed)
        self.sectionDoubleClicked.connect(self.on_sectionDoubleClicked)
        self._current_index = -1
        self._filters_text = dict()

    def setEditable(self, index, is_editable):
        if 0 <= index < self.count():
            self._is_editable[index] = is_editable

    @QtCore.pyqtSlot()
    def hide_lineedit(self):
        self._filters_text[self._current_index] = self._lineedit.text()
        self._lineedit.hide()
        self._current_index = -1
        self._lineedit.clear()

    @QtCore.pyqtSlot(int)
    def on_sectionDoubleClicked(self, index):
        self.hide_lineedit()
        is_editable = False
        if index in self._is_editable:
            is_editable = self._is_editable[index]
        if is_editable:
            geom = QtCore.QRect(self.sectionViewportPosition(index), 0, self.sectionSize(index), self.height())
            self._lineedit.setGeometry(geom)
            if index in self._filters_text:
                self._lineedit.setText(self._filters_text[index])
            self._lineedit.show()
            self._lineedit.setFocus()
            self._current_index = index
            self.textChanged.emit(self._current_index, self._lineedit.text())

    @QtCore.pyqtSlot(str)
    def on_text_changed(self, text):
        if self._current_index != -1:
            self.textChanged.emit(self._current_index, text)


# Główne okno aplikacji
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        table_schema = ShowTableData(self)
        table_schema.exec_()
        # print(global_table_schema)
        # layout = QVBoxLayout()

        try:
            self.table_name = global_table_schema[0]
            self.table_cols = tuple(global_table_schema)[1:] + ('Usuń',)
            print(self.table_cols)
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Brak wybranego schematu tabeli. Okno zostało zamknięte.')
            sys.exit()

        self.setWindowTitle("System zarządzania danymi")
        self.setMinimumSize(900, 600)

        self.tableWidget = QTableWidget()

        headerview = EditableHeaderView(self.tableWidget)
        self.tableWidget.setHorizontalHeader(headerview)

        self.setCentralWidget(self.tableWidget)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.horizontalHeader().sortIndicatorChanged.connect(
            self.tableWidget.resizeRowsToContents)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.tableWidget.setColumnCount(len(self.table_cols))
        self.tableWidget.setHorizontalHeaderLabels(self.table_cols)

        self.load_data()

        headerview.textChanged.connect(self.on_text_changed)

        # read table data and next step: edit data
        self.tableWidget.itemChanged.connect(self.UpdateTableTuple)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        btn_ac_chart = QAction(QIcon('%s/chart.png' % (_icons_folder_path,)), "Rysuj", self)
        btn_ac_chart.triggered.connect(self.chart)
        btn_ac_chart.setStatusTip("Rysuj")
        toolbar.addAction(btn_ac_chart)

        btn_ac_pdf = QAction(QIcon('%s/pdf.png' % (_icons_folder_path,)), "Podgląd", self)
        btn_ac_pdf.triggered.connect(self.pdf)
        btn_ac_pdf.setStatusTip("Podgląd")
        toolbar.addAction(btn_ac_pdf)

        btn_ac_refresh = QAction(QIcon('%s/refresh.png' % (_icons_folder_path,)), "Odśwież", self)
        btn_ac_refresh.triggered.connect(self.load_data)
        btn_ac_refresh.setStatusTip("Ośwież")
        toolbar.addAction(btn_ac_refresh)

        btn_ac_change = QAction(QIcon('%s/change.png' % (_icons_folder_path,)), "Zmień", self)
        btn_ac_change.triggered.connect(self.change)
        btn_ac_change.setStatusTip("Zmień")
        toolbar.addAction(btn_ac_change)

        self.show()

    @QtCore.pyqtSlot(int, str)
    def on_text_changed(self, col, text):
        # print(col, text)
        self.filter_data(col, text)

    def filter_data(self, col, text):
        tmp = [t for t in self.result if t[col].startswith(str(text))]
        # print(tmp)
        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(tmp):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(tmp):
            _button = QPushButton()
            _button.setIcon(QIcon('%s/bin.png' % (_icons_folder_path,)))
            _button.setText('Usuń')
            _button.clicked.connect(partial(self.DeleteTableTuple, button_row=row_number))
            self.tableWidget.setCellWidget(row_number, len(self.table_cols) - 1, _button)

    def load_data(self):
        self.result = base.select_table_data(_db_path, self.table_name)
        # print(self.result)

        self.result = [tuple(str(x) for x in tup) for tup in self.result]
        # print(self.result)

        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(self.result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        for row_number, row_data in enumerate(self.result):
            _button = QPushButton()
            _button.setIcon(QIcon('%s/bin.png' % (_icons_folder_path,)))
            _button.setText('Usuń')
            _button.clicked.connect(partial(self.DeleteTableTuple, button_row=row_number))
            self.tableWidget.setCellWidget(row_number, len(self.table_cols) - 1, _button)

        for column_number, data in enumerate(row_data):
            print(column_number)
            self.tableWidget.horizontalHeader().setEditable(column_number, True)


    def UpdateTableTuple(self, item):
        row = item.row()
        col = item.column()
        columnName = self.tableWidget.horizontalHeaderItem(col).text()
        id = self.tableWidget.item(row, 0).text()
        value = self.tableWidget.item(row, col).text()
        condition = '"%s" = "%s"' % (labels.ID, id,)
        base.update_table_data(file_name=_db_path, table_name=self.table_name,
                               column='"%s"' % (columnName,), value=value, condition=condition)

    def DeleteTableTuple(self, button_row):
        id = self.tableWidget.item(button_row, 0).text()
        condition = '"%s" = "%s"' % (labels.ID, id,)
        base.delete_table_data(file_name=_db_path, table_name=self.table_name, condition=condition)


    def chart(self):
        dlg = ChartPanel()
        dlg.exec_()

    def pdf(self):
        dlg = PdfPanel()
        dlg.exec_()

    def change(self):
        self.hide()
        MainWindow()


class run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
