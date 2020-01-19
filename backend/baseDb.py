from backend import labels

import sqlite3
import itertools


# Instrukcja służąca do utworzenia wstępnej listy tabel
def create_db(db):
    # Tworzymy połączenie z SQLite DB
    cnn = sqlite3.connect(db)
    # chwytamy obiekt Cursor w celu wykonywania zapytań SQL
    cursor = cnn.cursor()

    # Tworzymy wstępną listę tabel naszej bazy danych (opis: rozdział 6 str 47)
    _table_Users = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_USERS + """\" (
                                           \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                           \"""" + labels.USER_NAME + """\" text NOT NULL, 
                                           \"""" + labels.ACADEMIC_TITLE + """\" text, 
                                           \"""" + labels.DEPARTMENT_ID + """\" integer NOT NULL,
                                           \"""" + labels.CREATED_AT + """\" integer NOT NULL,
                                           \"""" + labels.UPDATE_AT + """\" integer NOT NULL,

                                           UNIQUE(\"""" \
                       + labels.USER_NAME + """\", \"""" \
                       + labels.DEPARTMENT_ID + """\"),
                                           CONSTRAINT FK_UserDepartments FOREIGN KEY (\"""" \
                       + labels.DEPARTMENT_ID + """\")
                                            REFERENCES \"""" \
                       + labels.TABLE_DEPARTMENTS + """\"(\"""" \
                       + labels.ID + """\")
                                       ); """

    _table_Departments = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_DEPARTMENTS + """\" (
                                               \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                               \"""" + labels.DEPARTMENT_NAME + """\" text,
                                               \"""" + labels.CREATED_AT + """\" integer NOT NULL,
                                               \"""" + labels.UPDATE_AT + """\" integer NOT NULL,
                                           
                                               UNIQUE(\"""" + labels.DEPARTMENT_NAME + """\")
                                           ); """

    _table_Courses = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_COURSES + """\" (
                                               \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                               \"""" + labels.COURSE_NAME + """\"  text NOT NULL,
                                               \"""" + labels.USER_ID + """\" integer NOT NULL,
                                               \"""" + labels.DEPARTMENT_ID + """\" integer NOT NULL,
                                               \"""" + labels.YEAR + """\" text NOT NULL,
                                               \"""" + labels.TERM + """\" text NOT NULL,
                                               \"""" + labels.CREATED_AT + """\" integer NOT NULL,
                                               \"""" + labels.UPDATE_AT + """\" integer NOT NULL,

                                               UNIQUE(\"""" + labels.COURSE_NAME + """\"
                                               , \"""" + labels.USER_ID + """\" 
                                               , \"""" + labels.YEAR + """\"
                                               , \"""" + labels.TERM + """\"
                                               , \"""" + labels.CREATED_AT + """\"),
                                               CONSTRAINT FK_UserCourses FOREIGN KEY (\"""" \
                         + labels.USER_ID + """\") REFERENCES \"""" \
                         + labels.TABLE_USERS + """\"(\"""" \
                         + labels.ID + """\")
                                           ); """


    _table_Comments = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_COMMENTS + """\" (
                                               \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                               \"""" + labels.COMMENTS_FOLDER_ID + """\" integer NOT NULL,
                                               \"""" + labels.USER_ID + """\" integer NOT NULL,
                                               \"""" + labels.CATEGORY_ID + """\" integer NOT NULL,
                                               \"""" + labels.FILE_NAME + """\" text NOT NULL,

                                                UNIQUE(\"""" + labels.COMMENTS_FOLDER_ID + """\"
                                                , \"""" + labels.CATEGORY_ID + """\" 
                                                , \"""" + labels.USER_ID + """\"
                                                , \"""" + labels.FILE_NAME + """\"),

                                               CONSTRAINT FK_UserCommentsFiles FOREIGN KEY 
                                               (\"""" + labels.USER_ID + """\" ) REFERENCES \"""" \
                          + labels.TABLE_USERS + """\" (\"""" \
                          + labels.ID + """\" ),
                                               CONSTRAINT FK_CommentsFileInFolders FOREIGN KEY (\"""" \
                          + labels.COMMENTS_FOLDER_ID + """\") REFERENCES \"""" \
                          + labels.TABLE_MAP + """\" (\"""" \
                          + labels.COMMENTS_FOLDER_ID + """\"),
                                               CONSTRAINT FK_categoryCommentsFiles FOREIGN KEY (\"""" \
                          + labels.CATEGORY_ID + """\") REFERENCES \"""" \
                          + labels.TABLE_MAP + """\" (\"""" \
                          + labels.CATEGORY_ID + """\")
                                           ); """

    _table_PdfFiles = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_PDF_FILES + """\" (
                                                   \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   \"""" + labels.COMMENTS_FOLDER_ID + """\" integer NOT NULL,
                                                   \"""" + labels.USER_ID + """\" integer NOT NULL,
                                                   \"""" + labels.CATEGORY_ID + """\" integer NOT NULL,
                                                   \"""" + labels.FILE_PATH + """\" text NOT NULL,

                                                    UNIQUE(\"""" + labels.COMMENTS_FOLDER_ID + """\",
                                                     \"""" + labels.USER_ID + """\", 
                                                     \"""" + labels.FILE_PATH + """\"),

                                                   CONSTRAINT FK_UserCommentsPDF FOREIGN KEY 
                                                   (\"""" + labels.USER_ID + """\" ) REFERENCES \"""" \
                           + labels.TABLE_USERS + """\" (\"""" \
                           + labels.ID + """\" ),
                                                   CONSTRAINT FK_CommentsPDF FOREIGN KEY (\"""" \
                           + labels.COMMENTS_FOLDER_ID + """\") REFERENCES \"""" \
                           + labels.TABLE_MAP + """\" (\"""" \
                           + labels.COMMENTS_FOLDER_ID + """\")
                                               ); """

    _table_Map = """ CREATE TABLE IF NOT EXISTS \"""" + labels.TABLE_MAP + """\" (
                                                           \"""" + labels.ID + """\" INTEGER PRIMARY KEY AUTOINCREMENT,
                                                           \"""" + labels.COL_PRESENCE + """\" text,
                                                           \"""" + labels.COL_PRESENCE_MAP + """\" integer,	
                                                           \"""" + labels.COL_ATTENDANCE_2 + """\" text,                                               
                                                           \"""" + labels.COL_ATTENDANCE_MAP + """\" integer,
                                                           \"""" + labels.COL_AVERAGE_MARKS + """\" text, 
                                                           \"""" + labels.COL_AVERAGE_MARKS_MAP + """\" integer,
                                                           \"""" + labels.COMMENTS_FOLDER_NAME + """\" text, 
                                                           \"""" + labels.COMMENTS_FOLDER_ID + """\" integer, 
                                                           \"""" + labels.CATEGORY_NAME + """\" text,        
                                                           \"""" + labels.CATEGORY_ID + """\" integer,
                                                           
                                                           UNIQUE(\"""" \
                         + labels.COL_PRESENCE + """\" , \"""" \
                         + labels.COL_PRESENCE_MAP + """\"),
                                                           UNIQUE(\"""" \
                         + labels.COL_ATTENDANCE + """\" , \"""" \
                         + labels.COL_ATTENDANCE_MAP + """\"),
                                                           UNIQUE(\"""" \
                         + labels.COL_AVERAGE_MARKS + """\", \"""" \
                         + labels.COL_AVERAGE_MARKS_MAP + """\"),
                                                           UNIQUE(\"""" \
                         + labels.COMMENTS_FOLDER_NAME + """\"),
                                                           UNIQUE(\"""" \
                         + labels.CATEGORY_NAME + """\"),
                                                           
                                                           CONSTRAINT FK_presenceMap FOREIGN KEY (\"""" \
                         + labels.COL_PRESENCE + """\")
                                                            REFERENCES \"""" \
                         + labels.TABLE_RESULTS + """\"(\"""" \
                         + labels.COL_PRESENCE + """\"),
                                                           CONSTRAINT FK_attendanceMap FOREIGN KEY (\"""" \
                         + labels.COL_ATTENDANCE + """\")
                                                            REFERENCES \"""" \
                         + labels.TABLE_RESULTS + """\"(\"""" \
                         + labels.COL_ATTENDANCE + """\"),
                                                           CONSTRAINT FK_marksMap FOREIGN KEY (\"""" \
                         + labels.COL_AVERAGE_MARKS + """\")
                                                            REFERENCES """ \
                         + labels.TABLE_RESULTS + """(\"""" \
                         + labels.COL_AVERAGE_MARKS + """\"),
                                                           CONSTRAINT FK_commentsMap FOREIGN KEY (\"""" \
                         + labels.COMMENTS_FOLDER_NAME + """\")
                                                            REFERENCES """ \
                         + labels.TABLE_COMMENTS + """(\"""" \
                         + labels.COMMENTS_FOLDER_ID + """\"),
                                                           CONSTRAINT FK_categorysMap FOREIGN KEY (\"""" \
                         + labels.CATEGORY_NAME + """\")
                                                            REFERENCES """ \
                         + labels.TABLE_COMMENTS + """(\"""" \
                         + labels.CATEGORY_ID + """\")
                                                            ); """

    # wykonanie zapytań SQL do bazy danych
    try:
        cursor.execute(_table_Users)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_Users))

    try:
        cursor.execute(_table_Departments)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_Departments))
    try:
        cursor.execute(_table_Courses)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_Courses))
    try:
        cursor.execute(_table_Comments)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_Comments))
    try:
        cursor.execute(_table_PdfFiles)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_PdfFiles))
    try:
        cursor.execute(_table_Map)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, _table_Map))
    # zamknięcie połączenia z bazą danych
    cnn.close()


# Instrukcje używane do wykonywania zapytań SQL
def select_tables(file_name):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = None
    try:
        cursor.execute(query)
        tables = cursor.fetchall()
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cursor.close()
    return tables


def select_table_columns(file_name, table_name):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()
    query = "SELECT * FROM \"%s\"" % table_name
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    col_names = [i[0] for i in cursor.description]
    cursor.close()
    return col_names


def select_tables_with_columns(file_name):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    tables_schemas = None
    try:
        cursor.execute(query)
        tables_schemas = cursor.fetchall()
        for i in range(0, len(tables_schemas)):
            col_names = ()
            for tbl in tables_schemas[i]:
                col_names = tuple(select_table_columns(file_name, tbl))
            tables_schemas[i] = tables_schemas[i] + (col_names, )

    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cursor.close()
    return tables_schemas


def select_table_data(file_name, table_name):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'SELECT * FROM \"%s\"' % table_name
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    rows = cursor.fetchall()
    cnn.commit()
    cursor.close()
    return rows


def select_table_data_1(file_name, table_name, columns):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'SELECT %s FROM \"%s\"' % (columns, table_name)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    rows = cursor.fetchall()
    cnn.commit()
    cursor.close()
    return rows


def select_table_data_2(file_name, table_name, columns, condition):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'SELECT %s FROM \"%s\" WHERE %s' % (columns, table_name, condition)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    rows = cursor.fetchall()
    cnn.commit()
    cursor.close()
    return rows


def select_table_data_3(file_name, table_name, columns, condition, orderBy, how='DESC'):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'SELECT %s FROM \"%s\" WHERE %s ORDER BY %s %s' % (columns, table_name, condition, orderBy, how)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    rows = cursor.fetchall()
    cnn.commit()
    cursor.close()
    return rows


def alter_table(file_name, table_name, column, type='varchar(32)'):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    # dodanie nowej kolumny w istniejącej tabeli
    query = 'ALTER TABLE \'%s\' ADD COLUMN \'%s\' \'%s\'' % (table_name, column, type)

    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.close()


def update_table_data(file_name, table_name, column, value, condition):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'UPDATE \"%s\" SET %s = %s WHERE %s' % (table_name, column, value, condition)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.commit()
    cursor.close()


def insert_table_data(file_name, table_name, columns, params):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'INSERT INTO \"' + table_name + '\" (' + columns + ') VALUES (' + \
            ','.join(itertools.repeat('?', len(params))) + ');'
    # print(query)
    try:
        cursor.execute(query, params)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.commit()
    cursor.close()


def insert_list_data(file_name, table_name, columns, list):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    var_string = ', '.join('?' * len(list))
    query = 'INSERT INTO \"%s\" (%s) VALUES (%s);' % (table_name, columns, var_string)

    try:
        cursor.execute(query, var_string)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.commit()
    cursor.close()


def insert_tuple_data(file_name, table_name, columns, list):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    values = ', '.join(map(str, list))
    query = 'INSERT INTO \'' + table_name + '\' (' + columns + ')  VALUES {}'.format(values)

    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.commit()
    cursor.close()


def delete_table_data(file_name, table_name, condition):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'DELETE FROM \"%s\" WHERE %s' % (table_name, condition)
    # print(query)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    rows = cursor.fetchall()
    cnn.commit()
    cursor.close()
    return rows


def drop_table(db, table):
    cnn = sqlite3.connect(db)
    cursor = cnn.cursor()
    query = 'DROP TABLE IF EXISTS %s' % (table, )
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))
    cnn.commit()
    cursor.close()


def drop_column(file_name, table_name, correct_columns):
    cnn = sqlite3.connect(file_name)
    cursor = cnn.cursor()

    query = 'CREATE TABLE table_backup (%s)' % (correct_columns, )
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    query = 'INSERT INTO table_backup SELECT %s FROM \"%s\"' % (correct_columns, table_name)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    query = 'DROP TABLE \"%s\"' % (table_name, )
    try:
        cursor.execute(query)
    except:
        pass
        # print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    query = "CREATE TABLE \"%s\" (%s)" % (table_name, correct_columns)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    query = "INSERT INTO \"%s\" SELECT %s FROM table_backup" % (table_name, correct_columns)
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    query = "DROP TABLE table_backup"
    try:
        cursor.execute(query)
    except:
        pass
        print('%s %s' % (labels.ERROR_SQL_QUERY_FAIL, query))

    cnn.commit()
    cursor.close()


