import os
from backend import labels


def userName_attribute_decomposition(phrases=[]):
    # skrypt ma na celu wykonanie dekomozycji atrybutu userName na imię&nazwisko prowadzącego i jego tytuł naukowy
    # problem rozwiązano w taki sposób, że przed każdą frazą tytułu naukowego dajemy znak przecinka, a następnie
    # pozostawiamy tylko pierwszy przecinek, a pozostałe zastępujemy znakiem spacji
    # na samym końcu tej instrukcji aktualizujemy ściezkę do katalogu
    years = all_folders_in_path(labels.ROOT_DATA_FOLDER)
    for year in years:
        year_path = '%s/%s' % (labels.ROOT_DATA_FOLDER, year)
        terms = all_folders_in_path(year_path)
        for term in terms:
            term_path = '%s/%s' % (year_path, term)
            departments = all_folders_in_path(term_path)
            for department in departments:
                    department_path = '%s/%s' % (term_path, department)
                    users = all_folders_in_path(department_path)
                    for user in users:
                        user_path = '%s/%s' % (department_path, user)
                        # print("user: \"", user, "\"")
                        userOrgin = user
                        for ele in phrases:
                            if user.find(ele) != -1:
                                idx = user.index(ele)
                                if idx > 1:
                                    userOrgin = userOrgin[:idx] + labels.COMMA + userOrgin[idx+1:]

                        # print("edit: \"", userOrgin, "\"")
                        idx_char = userOrgin.find(labels.COMMA)
                        userName=None
                        userTitle=None
                        if idx_char != -1:
                            userName = userOrgin[:idx_char]
                            if idx_char < len(userOrgin):
                                userTitle = userOrgin[idx_char:]
                                idx_other_chars = userTitle.find(labels.COMMA)
                                if idx_other_chars != -1:
                                    userTitle = userTitle.replace(labels.COMMA, ' ', 10)

                        if userTitle and userName is not None:
                            new_user = str(userName) + labels.COMMA + str(userTitle[1:])
                            new_user_path = '%s/%s' % (department_path, new_user)

                            print(user_path)
                            print(new_user_path)
                            # if userName is not None:
                            if user_path != new_user_path:
                                os.rename(user_path, new_user_path)
                        else:
                            print('Nieoczekiwana nazwa folderu prowadzącego:')
                            print('Nazwa prowadzącego: ', userOrgin)
                            print('Tytuł naukowy: ', userTitle)



def all_folders_in_path(folder):
    folders = next(os.walk(folder))[1]
    return folders


def all_files_in_path(path=labels.ROOT_DATA_FOLDER, exclude=['.']): #'.db', '.tmp', "
    files = []
    if not os.path.isdir(path):
        print(path)
    else:
        for item in os.listdir(path):
            if any(x in item for x in exclude):
                files.append(item)
    return files


def save_files_path_to_file(outputfile='all.txt', folder=labels.ROOT_DATA_FOLDER, exclude=['.db', '.tmp'], pathsep="\\"):
    """
        Rozpocznij konwersję
        :param outputfile: plik, aby zapisać wyniki
        :param folder: folder do eksploracji
        :param  exclude: wyklucz pliki zawierające te ciągi
        :param  pathsep: path seperator ('/' for linux, '\' for Windows)
    """

    with open(outputfile, "w") as txtfile:
        for path, dirs, files in os.walk(folder):
            sep = "\n---------- " + path.split(pathsep)[len(path.split(pathsep)) - 1] + " ----------"
            # print(sep)
            txtfile.write("%s\n" % sep)

            for fn in sorted(files):
                if not any(x in fn for x in exclude):
                    # filename = os.path.splitext(fn)[0]
                    filename = fn
                    txtfile.write("%s\n" % filename)

    txtfile.close()


def all_subdirectories(folder='all'):
        print([x[0] for x in os.walk(folder)])

