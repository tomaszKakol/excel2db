from __future__ import unicode_literals
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
import hashlib
import os

from frontend.loginGui import Ui_Widget, LoginDialog
from backend import baseDb as base, labels, loginDb as db

# _db_path = ('../%s' % (labels.DB_FILE,))
_db_path = os.path.abspath('../%s' % (labels.DB_FILE,))


class LoginPanel(QDialog, QWidget, Ui_Widget):
    def __init__(self, *args, **kwargs):
        super(LoginPanel, self).__init__(*args, **kwargs)
        # wywołanie db.cnn() tworzy bazę danych logowania po uruchomieniu pliku exe, jeżeli taka baza nie istnieje
        db.cnn()
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.log_in)
        self.addBtn.clicked.connect(self.registration)
        self.endBtn.clicked.connect(self.end)

        # self.setLayout(layout)
        # self.show()
        # self.move(350, 200)

    def registration(self):
        login, ok = QInputDialog.getText(self, 'Rejestracja', 'Podaj login:')
        columns = '"%s"' % (login,)
        condition = '"%s" = \'%s\'' % (labels.LOGIN, login)
        data = base.select_table_data_2(_db_path, labels.TABLE_PERSONS, columns, condition)
        if data:
            QMessageBox.warning(self, 'Błąd',
                                'Już istnieje użytkownik o nazwie \'%s\'. Proszę użyć innej nazwy użytkownika.'
                                % (login, ), QMessageBox.Ok)
            return

        if ok:
            password, ok = QInputDialog.getText(self, 'Rejestracja', 'Podaj hasło:', QLineEdit.Password)
            repeat, ok = QInputDialog.getText(self, 'Rejestracja', 'Powtórz hasło:', QLineEdit.Password)
            if password != repeat:
                QMessageBox.warning(
                    self, 'Błąd', 'Powtórzone hasło musi być identyczne!', QMessageBox.Ok)
                return
            if not login or not password:
                QMessageBox.warning(
                    self, 'Błąd', 'Podaj login oraz hasło!', QMessageBox.Ok)
                return

            p_as_bytes = str.encode(password)
            h = hashlib.blake2b()
            h.update(p_as_bytes)
            hash_p = h.hexdigest()
            db.addClient(login=login, password=hash_p)
            QMessageBox.information(
                self, 'Dane rejestracji',
                'Dodano nowego klienta z loginem: \'' + login + '\'', QMessageBox.Ok)


    def log_in(self):
        login, password, ok = LoginDialog.getLoginPassword(self)
        if not ok:
            return

        if not login or not password:
            QMessageBox.warning(self, 'Błąd',
                                'Pusty login lub hasło!', QMessageBox.Ok)
            return

        columns = '"%s"' % (login,)
        condition = '"%s" = \'%s\'' % (labels.LOGIN, login)
        data = base.select_table_data_2(_db_path, labels.TABLE_PERSONS, columns, condition)
        if not data:
            QMessageBox.warning(self, 'Błąd',
                                'Użytkownik o nazwie \'%s\' nie istnieje.'
                                % (login,), QMessageBox.Ok)
            return

        p_as_bytes = str.encode(password)
        h = hashlib.blake2b()
        h.update(p_as_bytes)
        hash_p = h.hexdigest()
        columns = '"%s", "%s"' % (login, password)
        condition = '"%s" = \'%s\' and "%s" = "%s"' % (labels.LOGIN, login, labels.PASSWORD, hash_p)
        data = base.select_table_data_2(_db_path, labels.TABLE_PERSONS, columns, condition)
        if not data:
            QMessageBox.critical(self, 'Błąd', 'Błędne hasło!', QMessageBox.Ok)
            return
        self.accept()

    def end(self):
        self.close()

