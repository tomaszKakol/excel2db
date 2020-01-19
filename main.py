# import niezbędnych pakietów
import sys
import os
from backend import baseDb
from backend import fillDb
from backend import labels
from backend import surveysSheet as ss
from backend import textDetection as td
from backend import findFiles
from backend import images2pdf as img


if __name__ == '__main__':
    env = sys.argv[1] if len(sys.argv) > 2 else 'dev'

_db_path = os.path.abspath(labels.DB_FILE)

# W tym miejscu dokonujemy dekomozycji nazw folderów z poziomu folderów pracowników naukowych
# na wartości userName i academicTitle
print('start: userName_attribute_decomposition')
findFiles.userName_attribute_decomposition(phrases=[" prof",
                                                    " nadzw ", " nadzw.",
                                                    " dr",
                                                    " hab ", " hab.",
                                                    " mgr",
                                                    " inz",  " inż"])

# Tworzymy podstawową strukturę bazy danych
print('start: create_db')
baseDb.create_db(db=_db_path)

# Uzupełniamy bazę danych stworzoną w poprzednim kroku oraz uzupełniamy strukturę bazy danych o nowe atrybuty i tabele
# odczytane z arkuszy kalkulacyjnych .xls
print('start: retrive_data_and_fill_db')
fillDb.retrive_data_and_fill_db(db=_db_path)

# Usuwamy zbędną tabelę normalizacyjną z naszej bazy danych, powstałej automatycznie po utworzeniu naszej bazy danych,
# a duplikującej dane zmagazynowane w tabelach zdefiniowanych przez nas
print('start: drop_table')
baseDb.drop_table(db=_db_path, table=labels.TABLE_NORM)

# W tym kroku usuwamy 'puste' odpowiedzi z komentarzy respondentów i zapisujemy je do stworzonego folderu "bin"
# Tworzymy odpowiednie pliki pdf ze scalonymi komentarzami oraz tworzymy nowy folder
# "komentarze", w którym zamieszczamy wszystkie utworzone pliki pdf
print('start: list_and_detection')
td.list_and_detection(east='frozen_east_text_detection.pb', min_confidence=0.95, width=448, height=448)

# Po wykonaniu redukcji plików graficznych i stworzeniu nowych plików pdf ponownie przeszukujemy strukturę odwróconego
# drzewa i uzupełniamy naszą bazę danych o pozostałe informacje, tj ścieżki pośrednie do plików graficznych i pdf
print('start: insert_pdf_and_photos_data')
fillDb.insert_pdf_and_photos_data(db=_db_path)

# Utworzenie i wypełnienie arkusza kalkulacyjnego "Ankiety.xls" zawierającego zmagazynowane dane pobrane z naszej bazy
# danych, a przedstawionych w formie raportu
print('start: create & fill xls sheets')
cols_base = ["Prowadzący", "Nazwa przedmiotu", "Rok ankiety", "Semestr"]
ss.create_menu(db=_db_path, cols_base=cols_base)
ss.fill_sheets(db=_db_path, cols_base=cols_base)
print('end: success')


