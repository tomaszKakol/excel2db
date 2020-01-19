from backend import baseDb as base, labels

import os.path
import sys, os, itertools, logging
import sqlite3 as sqlite
import xlrd
from openpyxl import load_workbook


if sys.version_info >= (3,):
    string_types = str,

# NO debug, no info. But logs warnings
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
#log.setLevel(logging.DEBUG)


# instrukcje obsługujące mapowanie danych
def insert_mapping_data():
    # --- attendance ---
    columns = u'"%s", "%s"' % (labels.COL_ATTENDANCE_2, labels.COL_ATTENDANCE_MAP,)
    params = [labels.PRESENCE_OVER_70, 3]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.PRESENCE_BETWEEN_30_AND_70, 2]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.PRESENCE_LESS_30, 1]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)

    # --- presence ---
    columns = u'"%s", "%s"' % (labels.COL_PRESENCE, labels.COL_PRESENCE_MAP,)
    params = [labels.YES, 2]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.NO, 1]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)

    # --- marks ---
    columns = u'"%s", "%s"' % (labels.COL_AVERAGE_MARKS, labels.COL_AVERAGE_MARKS_MAP,)
    params = [labels.AVERAGE_OVER_4_DOT_5, 4]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.AVERAGE_BETWEEN_4_AND_4_DOT_5, 3]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.AVERAGE_BETWEEN_3_DOT_5_AND_4, 2]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)
    params = [labels.AVERAGE_LESS_3_DOT_5, 1]
    base.insert_table_data(labels.DB_FILE, labels.TABLE_MAP, columns, params)


def mapping_attendance(value):
    if value == labels.PRESENCE_OVER_70:
        return 3
    elif value == labels.PRESENCE_BETWEEN_30_AND_70:
        return 2
    elif value == labels.PRESENCE_LESS_30:
        return 1
    else:
        return value


def mapping_presence(value):
    if value.lower() == labels.YES:
        return 2
    elif value.lower() == labels.NO:
        return 1
    else:
        return value


def mapping_marks(value):
    if value == labels.AVERAGE_OVER_4_DOT_5:
        return 4
    elif value == labels.AVERAGE_BETWEEN_4_AND_4_DOT_5:
        return 3
    elif value == labels.AVERAGE_BETWEEN_3_DOT_5_AND_4:
        return 2
    elif value == labels.AVERAGE_LESS_3_DOT_5:
        return 1
    else:
        return value


def convert_xls2db(infile, outfile=None, column_name_start_row=0, data_start_row=1, user_id=0, department_id=0, course_id=0):
    if isinstance(infile, string_types):
        wb = xlrd.open_workbook(infile)
    elif isinstance(infile, xlrd.Book):
        wb = infile
        infile = "default"
    else:
        raise TypeError("Oczekiwano na wejściu pliku xlrd")

    # przekazanie połączenia sqlite
    if outfile is None:
        outfile = os.path.splitext(infile)[0] + '.sqlite'

    if isinstance(outfile, string_types):
        cnn = sqlite.connect(outfile)
        cursor = cnn.cursor()
    elif isinstance(outfile, sqlite.Connection):
        cnn = outfile
        cursor = cnn.cursor()
    else:
        raise TypeError("Na wyjściu oczekiwano string lub sqlite.Connection")

    column_name_start_row = int(column_name_start_row)
    data_start_row = int(data_start_row)

    for s in wb.sheets():
        if s.name == "Statystyka inżynierska":
            s.name = "wyniki"

        print('aktualna zakładka w pliku xlrd: ', s.name)
        # Jeżeli jest nowy typ danych to tworzymy nową tabelę dla tego typu danych
        if s.nrows > column_name_start_row:
            tmp_sql = """ CREATE table IF NOT EXISTS \"""" + s.name + """\"(
                                                           id integer NOT NULL,
                                                           """ + labels.USER_ID + """ integer NOT NULL, 
                                                           """ + labels.DEPARTMENT_ID + """ integer NOT NULL,
                                                           """ + labels.COURSE_ID + """ integer NOT NULL,
                                                           UNIQUE(id),
                                                           PRIMARY KEY (id)
                                                       ); """
            log.debug('DDL %r', tmp_sql)

            try:
                cursor.execute(tmp_sql)
            except:
                pass
                print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, tmp_sql))

            #odczytujemy kolumny i dodajemy nowe do stworzonej tablicy
            column_names = []
            for j in range(s.ncols):
                colname = s.cell(column_name_start_row, j).value
                if colname:
                    colname = '"c%d"' % (colname,) if isinstance(colname, int) else \
                              u'"%s"' % (colname,)
                else:
                    colname = '"col%d"' % (j + 1,)
                column_names.append(colname)
                tmp_sql = u'ALTER TABLE  "' + s.name + '" ADD COLUMN ' + colname + ' integer'
                log.debug('DDL %r', tmp_sql)
                try:
                    cursor.execute(tmp_sql)
                except:
                    pass
                    print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, tmp_sql))
            print('Nazwy kolumn w pliku xlrd: ', column_names)
        all_columns = ""
        for i in column_names:
            all_columns = all_columns + ", " + i

        base_columns = u', "%s", "%s", "%s"' % \
                       (labels.USER_ID, labels.DEPARTMENT_ID, labels.COURSE_ID)
        all_columns = all_columns + base_columns
        # TODO: replace '3' with base_columns attributes value
        tmp_sql = 'INSERT INTO "' + s.name + '" (' + all_columns[1:] +\
                  ') VALUES (' + ','.join(itertools.repeat('?', s.ncols + 3)) + ");"

        # Mapujemy wartości w kolumnie frekwencji respondenta (COL_ATTENDANCE lub COL_ATTENDANCE_2)
        print('mapowanie wartości w kolumach frekwencji respondentów')
        for rownum in range(data_start_row, s.nrows):
            bind_params = s.row_values(rownum)
            index = -1
            try:
                val = '"%s"' % (labels.COL_ATTENDANCE,)
                val_2 = '"%s"' % (labels.COL_ATTENDANCE_2,)
                if val in column_names:
                    index = [column for column in column_names].index(val)
                elif val_2 in column_names:
                    index = [column for column in column_names].index(val_2)
            except ValueError:
                index = -1
            if index != -1:
                bind_params[index] = mapping_attendance(bind_params[index])

            # Mapujemy wartości w kolumnie średnich ocen respondenta (COL_AVERAGE_MARKS)
            print('mapowanie wartości w kolumnie średniej oceny respondentów')
            try:
                val = '"%s"' % (labels.COL_AVERAGE_MARKS,)
                index = [column for column in column_names].index(val)
            except ValueError:
                index = -1
            if index != -1:
                bind_params[index] = mapping_marks(bind_params[index])

            # Mapujemy wartości w kolumnach obecności respondentów (COL_ATTENDANCE lub COL_ATTENDANCE_2)
            print('mapowanie wartości w kolumnach obecnosci respondentów')
            try:
                val = '"%s"' % (labels.COL_PRESENCE,)
                val_2 = '"%s"' % (labels.COL_PRESENCE_2,)
                if val in column_names:
                    index = [column for column in column_names].index(val)
                elif val_2 in column_names:
                    index = [column for column in column_names].index(val_2)
            except ValueError:
                index = -1
            if index != -1:
                bind_params[index] = mapping_presence(bind_params[index])

            #zamieniamy wartości 'zero' na '0'
            print('zamiana \'zero\' na \'0\' w db')
            [i if i != 'zero' else 0 for i in bind_params]

            # dodajemy dane do bazy danych
            bind_params.insert(len(bind_params), user_id)
            bind_params.insert(len(bind_params), department_id)
            bind_params.insert(len(bind_params), course_id)

            log.debug('DML %r, %r', tmp_sql, bind_params)
            # print(bind_params)
            try:
                cursor.execute(tmp_sql, bind_params)
            except:
                pass
            print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, str(tmp_sql)))
    cnn.commit()

    #Zrób to tylko, jeśli nie pracujemy na zewnętrznej db
    if isinstance(outfile, string_types):
        cursor.close()
        cnn.close()

    # wywołujemy instrukcję do zapisu danych mapowania do db
    print('zapisie danych mapowania do db')
    insert_mapping_data()












