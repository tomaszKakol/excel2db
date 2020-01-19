from backend import baseDb as base, excel2db as e2db, labels, findFiles as files

import os.path

"""
Istrukcja w której wyciągamy podstawowe informacje zawarte w nazwach folderów zawartych w strukturze
katalogów oraz wywołanie obiektu instrukcji e2db.convert_xls2db odczytującej i konwertującej
dane z plików xls.
Istrukcje wywołujemy po utworzeniu naszej bazy danych, to jest wykonaniu instrukcji base.create_db(db)
"""
def retrive_data_and_fill_db(db):
    # wyciągnięcie nazw katalogów z poziomu lat przeprowadzenia ankiet
    years = files.all_folders_in_path(labels.ROOT_DATA_FOLDER)
    for year in years:
        # ustawienie pośredniej ścieżki dostępu do pliku
        year_path = '%s/%s' % (labels.ROOT_DATA_FOLDER, year)

        # wyciągnięcie roku ankiety, przykład:
        # "Ankiety 2014_15" -> "2014"
        _yearValue = year.split(" ", 1)[1].split("_", 1)[0]

        # wyciągnięcie nazw katalogów z poziomu semestrów
        terms = files.all_folders_in_path(year_path)

        # próba wyciągnięcia nazwy semestru z nazwy katalogu (letni / zimowy)
        for term in terms:
            termName=None
            if (term.find("let") != -1 and term.find("zim") == -1):
                termName = labels.SUMMER
            elif (term.find("let") == -1 and term.find("zim") != -1):
                termName = labels.WINTER
            elif (term.find("let") != -1 and term.find("zim") != -1):
                termName = labels.OUTSTANDING
            else:
                termName = labels.INVALID

            term_path = '%s/%s' % (year_path, term)

            # wyciągnięcie nazw katalogów z poziomu wydziałów
            departments = files.all_folders_in_path(term_path)
            for department in departments:
                department_path = '%s/%s' % (term_path, department)
                # Wyciągnięcie wartości daty utworzenia katalogu
                file_create = int(os.stat(department_path).st_ctime)
                # Wyciągnięcie wartości daty ostatniej modyfikacji katalogu
                file_modify = int(os.stat(department_path).st_mtime)

                # ------- Zapisanie danych do tabeli Departments -------
                columns = '"%s", "%s", "%s"' % (labels.DEPARTMENT_NAME, labels.CREATED_AT, labels.UPDATE_AT)
                values = [department, file_create, file_modify]
                try:
                    base.insert_table_data(db, labels.TABLE_DEPARTMENTS, columns, values)
                except:
                    pass

                # ------- wyciągnięcie wartości departmentID -------
                #createdAt nie działa bo folder wydziału moze wystąpić kilka razy w różnych latach ankiet
                columns = '"%s"' % (labels.ID,)
                condition = '"%s" = \'%s\'' % (labels.DEPARTMENT_NAME, department)
                rows = base.select_table_data_2(db, labels.TABLE_DEPARTMENTS, columns, condition)
                department_id = None
                if rows:
                    department_id = (rows[0])[0]

                # wyciągnięcie nazw katalogów z poziomu pracowników naukowych
                users = files.all_folders_in_path(department_path)
                for user in users:
                    user_path = '%s/%s' % (department_path, user)
                    file_create = int(os.stat(user_path).st_ctime)
                    file_modify = int(os.stat(user_path).st_mtime)

                    #dokonanie dekompozycji nazwy katalogu na imię&nazwisko pracownika oraz jego tytuł naukowy
                    # separatorem jest znak przecinka
                    userName = user.split(labels.COMMA, 1)[0]
                    academicTitle = user.split(labels.COMMA, 1)[1]

                    # ------- INSERT DATA TO USERS TABLE -------
                    columns = '"%s", "%s", "%s", "%s", "%s"' %\
                              (labels.USER_NAME, labels.ACADEMIC_TITLE,
                               labels.DEPARTMENT_ID, labels.CREATED_AT, labels.UPDATE_AT)
                    values = [userName, academicTitle, department_id, file_create, file_modify]
                    try:
                        base.insert_table_data(db, labels.TABLE_USERS, columns, values)
                    except:
                        pass

                    # ------- RETRIVE USER ID -------
                    # TODO: w przypadku poprawy klucza głównego w tabeli Users
                    # należy poprawić zapytanie służące do wyciągnięcia wartości userId
                    columns = '"%s"' % (labels.ID,)
                    condition = '"%s" = \'%s\' and "%s" = %s' % (
                        labels.USER_NAME, userName, labels.DEPARTMENT_ID, department_id)
                    rows = base.select_table_data_2(db, labels.TABLE_USERS, columns, condition)

                    user_id = None
                    if rows:
                        user_id = (rows[0])[0]

                    # wyciągnięcie nazw plików zamieszczonych w katalogach pracowników naukowych
                    all_files = files.all_files_in_path(path=user_path, exclude=['.xls', '.xlsx'])
                    for file in all_files:
                        file_path = '%s/%s' % (user_path, file)

                        # ------- INSERT DATA TO Courses TABLE -------
                        columns = '"%s", "%s", "%s", "%s", "%s", "%s", "%s"' % \
                                  (labels.COURSE_NAME, labels.USER_ID, labels.DEPARTMENT_ID,
                                   labels.YEAR, labels.TERM, labels.CREATED_AT, labels.UPDATE_AT)

                        #Wyciągnięcie nazw kursów z nazwy plików xls (separatorem jest znak kropki)
                        index_dot = file.rfind(labels.DOT)
                        courseName = file[:index_dot]
                        # print("courseName: ", courseName)

                        file_create = int(os.stat(file_path).st_ctime)
                        file_modify = int(os.stat(file_path).st_mtime)
                        values = [courseName, user_id, department_id, _yearValue, termName, file_create, file_modify]
                        try:
                            base.insert_table_data(db, labels.TABLE_COURSES, columns, values)
                        except:
                            pass
                            print('Error: Executed \'base.insert_table_data(db, labels.TABLE_COURSES, columns, values)\' failed.')

                        # ------- RETRIVE USER ID -------
                        columns = '"%s"' % (labels.ID,)
                        condition = '"%s" = \'%s\' and "%s" = %s and "%s" = \'%s\' and "%s" = %s ' % (
                            labels.COURSE_NAME, courseName, labels.YEAR, _yearValue,
                            labels.TERM, termName, labels.USER_ID, user_id)
                        rows = base.select_table_data_2(db, labels.TABLE_COURSES, columns, condition)

                        course_id = None
                        if rows:
                            course_id = (rows[0])[0]

                        print("convert: insert data from .xls files to .db file")
                        print('course_id: ', course_id, ', user_id: ', user_id, ', department_id: ', department_id)
                        # wywołujemy obiekt instrukcji do konwersji danych z plików xls do naszej bazy danych
                        e2db.convert_xls2db(infile=file_path, outfile=labels.DB_FILE_RESULTS,
                                            user_id=user_id, department_id=department_id, course_id=course_id)

    # dokonujemy scalenia atrybutów definiująych tą samą cechę podmiotu reprezentowanego przez tabelę 'wyniki'
    # kolumny  'A_pierwsze zajecia' i 'A_Obecnosc 1 zajecia' dotyczą tej samej cechy, dlatego
    # scalamy je i tworzymy jeden atrybut
    columns = '"%s", "%s"' % (labels.ID, labels.COL_PRESENCE_2,)
    condition = '"%s" IS NOT NULL;' % (labels.COL_PRESENCE_2,)
    rows = base.select_table_data_2(db, labels.TABLE_RESULTS, columns, condition)
    for row in rows:
        id = str(row[0])
        value = str(row[1])
        condition = '"%s" = "%s"' % (labels.ID, id,)
        base.update_table_data(file_name=db, table_name=labels.TABLE_RESULTS,
                               column='"%s"' % (labels.COL_PRESENCE,), value=value, condition=condition)
    results_cols = base.select_table_columns(db, labels.TABLE_RESULTS)
    if labels.COL_PRESENCE_2 in results_cols:
        results_cols.remove(labels.COL_PRESENCE_2)

    new_cols = '", "'.join(results_cols)
    new_cols = '"%s"' % (new_cols,)

    # usuwamy argument duplikat (tj. 'A_pierwsze zajecia')
    base.drop_column(db, labels.TABLE_RESULTS, new_cols)

"""
Instrukcja uzupełniająca bazę danych o ścieżki pośrednie do plików graficznych i plików pdf
"""
def insert_pdf_and_photos_data(db):
    tmp_comments_folder_id = 1
    tmp_category_folder_id = 1
    tuple_pdf = []
    tuple_photos = []

    #analogiczne przeszukanie struktury katalogów jak w instrukcji retrive_data_and_fill_db()
    years = files.all_folders_in_path(labels.ROOT_DATA_FOLDER)
    for year in years:
        root_path = '%s/%s' % (labels.ROOT_DATA_FOLDER, year)
        terms = files.all_folders_in_path(root_path)
        for term in terms:
            root_path = '%s/%s/%s' % (labels.ROOT_DATA_FOLDER, year, term)
            departments = files.all_folders_in_path(root_path)
            for department in departments:
                root_path = '%s/%s/%s/%s' % (labels.ROOT_DATA_FOLDER, year, term, department)
                # ------- RETRIVE department ID -------
                columns = '"%s"' % (labels.ID,)
                condition = '"%s" = \'%s\'' % (labels.DEPARTMENT_NAME, department)
                rows = base.select_table_data_2(db, labels.TABLE_DEPARTMENTS, columns, condition)
                department_id = None
                if rows:
                    departmentId = (rows[0])[0]
                if departmentId:
                    users = files.all_folders_in_path(root_path)
                    # print('department: "%s",  user: "%s"' % (department, users))
                    for user in users:
                        root_path = '%s/%s/%s/%s/%s' % (labels.ROOT_DATA_FOLDER, year, term, department, user)
                        userName = user.split(labels.COMMA, 1)[0]
                        # print(userName)

                         # ------- RETRIVE USER ID -------
                        columns = '"%s"' % (labels.ID,)
                        condition = '"%s" = \'%s\' and "%s" = "%s"' % (
                            labels.USER_NAME, userName, labels.DEPARTMENT_ID, departmentId)
                        rows = base.select_table_data_2(db, labels.TABLE_USERS, columns, condition)
                        user_id = None
                        if rows:
                            user_id = (rows[0])[0]
                        if user_id:
                            comments_folders = files.all_folders_in_path(root_path)
                            # print(comments_folders)

                            for comments_folder in comments_folders:
                                root_path = '%s/%s/%s/%s/%s/%s' % (
                                    labels.ROOT_DATA_FOLDER, year, term, department, user, comments_folder)
                                pdf_root_path = root_path
                                # ------- INSERT DATA TO TABLE_MAP -------
                                columns = '"%s", "%s"' % (labels.COMMENTS_FOLDER_NAME, labels.COMMENTS_FOLDER_ID)
                                values = [comments_folder, str(tmp_comments_folder_id)]
                                try:
                                    base.insert_table_data(db, labels.TABLE_MAP, columns, values)
                                    tmp_comments_folder_id = int(tmp_comments_folder_id) + 1
                                    # w tym miejscu inkrementujemy wartość identyfikatora (id) dla danego folderu
                                    # komentarza. W przypadku, gdy wystąpi folder o takiej samej nazwie to baza danych
                                    # odrzuci takie zapytanie, a licznik zwiększy się o jeden. Z tego powodu następny
                                    # poprawny identyfikator będzie zwiększony o więcej niż 1
                                except:
                                    pass

                                # ------- RETRIVE comments_folder_id -------
                                columns = '"%s"' % (labels.COMMENTS_FOLDER_ID,)
                                condition = '"%s" = \'%s\'' % (labels.COMMENTS_FOLDER_NAME, comments_folder)
                                rows = base.select_table_data_2(db, labels.TABLE_MAP, columns, condition)
                                comments_folder_id = None
                                if rows:
                                    comments_folder_id = (rows[0])[0]
                                if comments_folder_id:
                                    pdf_files = files.all_files_in_path(path=root_path,  exclude=['.pdf'])
                                    # print(pdf_files)

                                    category_folders = files.all_folders_in_path(root_path)
                                    for category_folder in category_folders:
                                        root_path = '%s/%s/%s/%s/%s/%s/%s' % (
                                            labels.ROOT_DATA_FOLDER, year, term, department, user, comments_folder, category_folder)
                                        # ------- INSERT DATA TO TABLE_MAP -------
                                        columns = '"%s", "%s"' % (labels.CATEGORY_NAME, labels.CATEGORY_ID)
                                        values = [category_folder, str(tmp_category_folder_id)]
                                        try:
                                            base.insert_table_data(db, labels.TABLE_MAP, columns, values)
                                            tmp_category_folder_id = int(tmp_category_folder_id) + 1
                                        except:
                                            pass

                                        # ------- RETRIVE category_folder_id -------
                                        columns = '"%s"' % (labels.CATEGORY_ID,)
                                        condition = '"%s" = \'%s\'' % (labels.CATEGORY_NAME, category_folder)
                                        rows = base.select_table_data_2(db, labels.TABLE_MAP, columns, condition)
                                        category_folder_id = None
                                        if rows:
                                            category_folder_id = (rows[0])[0]

                                        # pliki pdf znajdują się poziom wyżej od plików graficznych w strukturze katalogów
                                        # ------- przygotowanie kolekcji krotek dla danych plików pdf  -------
                                        if pdf_files:
                                            for pdf_file in pdf_files:
                                                if category_folder in pdf_file:
                                                    values = [int(comments_folder_id), int(user_id), '%s/%s' % (
                                                        pdf_root_path, pdf_file), int(category_folder_id)]
                                                    tuple_pdf.append(tuple(values))

                                        # ------- przygotowanie kolekcji krotek dla danych plików graficznych   -------
                                        photo_filesName = files.all_files_in_path(root_path)
                                        for photo_fileName in photo_filesName:
                                            values = [int(comments_folder_id), int(category_folder_id),
                                                      user_id, photo_fileName]
                                            tuple_photos.append(tuple(values))

    # # ------- INSERT DATA TO TABLE_COMMENTS -------
    # zebranie wszystkich danych i wykoanie ich zapisu do bazy danych wykonuje się dużo szybciej niż kilkaset
    # pojedyńczych zapytań
    try:
        columns = '"%s", "%s", "%s", "%s"' % \
                  (labels.COMMENTS_FOLDER_ID, labels.CATEGORY_ID, labels.USER_ID, labels.FILE_NAME)
        #usunięcie duplikatów, których wystąpienie będzie skutkować niepowodzeniem zapisu do bazy danych
        without_duplicates_tuple_photo = [t for t in (set(tuple(i) for i in tuple_photos))]
        # print(without_duplicates_tuple_photo)
        # print(tuple_photos)
        base.insert_tuple_data(db, labels.TABLE_COMMENTS, columns, without_duplicates_tuple_photo)
    except:
        pass

    # ------- INSERT DATA TO TABLE_PDF_FILES -------
    try:
        columns = '\'%s\', \'%s\', \'%s\', \'%s\'' % \
                  (labels.COMMENTS_FOLDER_ID, labels.USER_ID, labels.FILE_PATH, labels.CATEGORY_ID)
        without_duplicates_tuple_pdf = [t for t in (set(tuple(i) for i in tuple_pdf))]
        base.insert_tuple_data(db, labels.TABLE_PDF_FILES, columns, without_duplicates_tuple_pdf)
    except:
        pass


