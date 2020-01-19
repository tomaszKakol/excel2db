from PyQt5.QtWidgets import QTableView, QPushButton
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtWidgets import QGridLayout

'''
Interfejs logowania
'''
class Ui_Widget(object):

    def setupUi(self, Widget):
        Widget.setObjectName("Widget")

        # # tabelaryczny widok danych
        # self.view = QTableView()

        # przyciski Push ###
        self.loginBtn = QPushButton("Zaloguj")
        self.addBtn = QPushButton("Dodaj")
        self.endBtn = QPushButton("&Koniec")

        # układ przycisków Push ###
        layout = QHBoxLayout()
        layout.addWidget(self.loginBtn)
        layout.addWidget(self.addBtn)
        layout.addWidget(self.endBtn)

        # główny układ okna ###
        layoutV = QVBoxLayout(self)
        # layoutV.addWidget(self.view)
        layoutV.addLayout(layout)

        # właściwości widżetu ###
        self.setWindowTitle("Zarejestruj klienta")
        self.resize(300, 200)

        self.setLayout(layout)


class LoginDialog(QDialog):
    """ Okno dialogowe logowania """

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)

        # etykiety, pola edycyjne i przyciski ###
        loginLbl = QLabel('Login')
        passwordLbl = QLabel('Hasło')
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        # układ główny ###
        layout = QGridLayout(self)
        layout.addWidget(loginLbl, 0, 0)
        layout.addWidget(self.login, 0, 1)
        layout.addWidget(passwordLbl, 1, 0)
        layout.addWidget(self.password, 1, 1)
        layout.addWidget(self.btns, 2, 0, 2, 0)

        # sygnały i sloty ###
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        # właściwości widżetu ###
        self.setModal(True)
        self.setWindowTitle('Logowanie')

    def loginPassword(self):
        return (self.login.text().strip(),
                self.password.text().strip())

    # metoda statyczna, tworzy dialog i zwraca (login, haslo, ok)
    @staticmethod
    def getLoginPassword(parent=None):
        dialog = LoginDialog(parent)
        dialog.login.setFocus()
        ok = dialog.exec_()
        login, password = dialog.loginPassword()
        return (login, password, ok == QDialog.Accepted)