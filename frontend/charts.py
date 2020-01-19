from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
import numpy as np
import math
import os
from backend import baseDb as base, labels

_db_path = os.path.abspath('../%s' % (labels.DB_FILE,))


def bar_chart(objects, values, title, ylabel):
    y_pos = np.arange(len(objects))

    plt.bar(y_pos, values, align='center', alpha=0.5)
    # plt.legend(users, loc=2)
    plt.xticks(y_pos, objects)
    plt.xticks(rotation=30)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gcf().autofmt_xdate()
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    plt.show()


def boxplot_chart(box_plot_data, xlabels, title, ylabel):
    print(box_plot_data)
    # print(xlabels)
    plt.boxplot(box_plot_data, labels=list(xlabels), patch_artist=True,)
    #  notch='True',
    plt.xticks(rotation=30)
    plt.title(title)
    plt.ylabel(ylabel)
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    plt.show()


def retrive_data(file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year):
    values = None
    answersNo = []
    if courseId:
        cols = base.select_table_columns(file, table)
        stat_cols = []
        print(cols)
        if cols:
            for col in cols:
                for show_column in show_columns:
                    if show_column in col:
                        stat_cols.append(col)

            # print(stat_cols)
            if stat_cols:
                one_str_cols = '{1}{0}{1}'.format('\", "'.join(stat_cols), "\"")
                stat_cols = tuple(stat_cols)

                print('stat_cols')
                print(stat_cols)
                #year jest zawarty w courseID, więc jego podanie nic nie zmienia
                # if year != labels.ALL:
                #     condition = '"%s" = %s and "%s" = %s and "%s" = %s and "%s" > %s and %s < %s' % (
                #         labels.USER_ID, userId, labels.DEPARTMENT_ID, departmentId, labels.COURSE_ID, courseId,
                #         labels.YEAR, year)
                # else:
                condition = '"%s" = %s and "%s" = %s and "%s" = %s' % (
                    labels.USER_ID, userId, labels.DEPARTMENT_ID, departmentId, labels.COURSE_ID, courseId)

                if type:
                    condition = '%s and "col1" = "%s"' % (condition, type)

                if attedanceId and attedanceId != labels.ALL:
                    condition = '%s and "%s" = %s' % (condition, labels.COL_ATTENDANCE, attedanceId)

                if presenceId and presenceId != labels.ALL:
                    condition = '%s and "%s" = %s' % (condition, labels.COL_PRESENCE, presenceId)

                if marksId and marksId != labels.ALL:
                    condition = '%s and "%s" = %s' % (condition, labels.COL_AVERAGE_MARKS, marksId)

                result = base.select_table_data_2(file, table, one_str_cols, condition)
                print('result')
                print(result)

                if result:
                    list_of_values = [list(elem) for elem in result]
                    # print(list_of_values)
                    #convert None to 0
                    values = []
                    for i in range(0, len(list_of_values)):
                        temp = [0 if v is None else v for v in list_of_values[i]]
                        values.append(temp)
                    box_plot_data = list(map(list, zip(*values)))
                    filtered = [list(xi for xi in x if xi is not 0) for x in box_plot_data]

                    # print('filtered')
                    # print(filtered)
                    stat_cols = list(stat_cols)

                    for i in range(0, len(filtered)):
                        a = stat_cols[i]
                        b = int(len(filtered[i]))
                        stat_cols[i] = '%s (%d)' % (a, b,)
                        answersNo.append(b)

                    stat_cols = tuple(stat_cols)
                else:
                    # QMessageBox.warning(self, 'Info', 'Brak danych do wyświetlenia.')
                    return None, None, None, None
            else:
                # QMessageBox.warning(self, 'Info', 'Brak oczekiwanych kolumn.')
                return None, None, None, None
        else:
            # QMessageBox.warning(self, 'Info', 'Brak kolumn.')
            return None, None, None, None
    else:
        # QMessageBox.warning(self, 'Info', 'Brak kursu.')
        return None, None, None, None

    return values, stat_cols, filtered, answersNo


def retrive_data2(file, table, userId, departmentId, courseId, show_columns):
    values = None
    answersNo = []
    if courseId:
        cols = base.select_table_columns(file, table)
        stat_cols = []
        # print(cols)
        if cols:
            for col in cols:
                for show_column in show_columns:
                    if show_column in col:
                        stat_cols.append(col)

            # print(stat_cols)
            if stat_cols:
                one_str_cols = '{1}{0}{1}'.format('\", "'.join(stat_cols), "\"")
                stat_cols = tuple(stat_cols)

                condition = '"%s" = %s and "%s" = %s and "%s" = %s' % (
                    labels.USER_ID, userId, labels.DEPARTMENT_ID, departmentId, labels.COURSE_ID, courseId)

                # result = base.select_table_data_2(_db_path, table, one_str_cols, condition)
                result = base.select_table_data_2(file, table, one_str_cols, condition)
                # print(result)

                if result:
                    list_of_values = [list(elem) for elem in result]
                    # print(list_of_values)
                    #convert None to 0
                    values = []
                    for i in range(0, len(list_of_values)):
                        temp = [0 if v is None else v for v in list_of_values[i]]
                        values.append(temp)
                    box_plot_data = list(map(list, zip(*values)))
                    filtered = [list(xi for xi in x if xi is not 0) for x in box_plot_data]

                    # print('filtered')
                    # print(filtered)
                    stat_cols = list(stat_cols)

                    for i in range(0, len(filtered)):
                        a = stat_cols[i]
                        b = int(len(filtered[i]))
                        stat_cols[i] = '%s (%d)' % (a, b,)
                        answersNo.append(b)

                    stat_cols = tuple(stat_cols)
                else:
                    # QMessageBox.warning(self, 'Info', 'Brak danych do wyświetlenia.')
                    return None, None, None, None
            else:
                # QMessageBox.warning(self, 'Info', 'Brak oczekiwanych kolumn.')
                return None, None, None, None
        else:
            # QMessageBox.warning(self, 'Info', 'Brak kolumn.')
            return None, None, None, None
    else:
        # QMessageBox.warning(self, 'Info', 'Brak kursu.')
        return None, None, None, None

    return values, stat_cols, filtered, answersNo


def create_title(year, userId, table, type, courseId, attedanceId, presenceId, marksId):
    # if _from != labels.ALL:
    #     _from = datetime.utcfromtimestamp(_from).strftime('%Y')

    columns = '"%s"' % (labels.USER_NAME,)
    condition = '"%s" = %s' % (labels.ID, userId)
    data = base.select_table_data_2(_db_path, labels.TABLE_USERS, columns, condition)
    userName = None
    if data:
        userName = (data[0])[0]
    # print(userName)

    columns = '"%s"' % (labels.COURSE_NAME,)
    condition = '"%s" = %s' % (labels.ID, courseId)
    data = base.select_table_data_2(_db_path, labels.TABLE_COURSES, columns, condition)
    courseName = None
    if data:
        courseName = (data[0])[0]
    # print(courseName)

    title = '%s - Tabela \'%s\' dla %s \n' % (userName, table, courseName)
    if year != labels.ALL:
        title = '%s, %s' % (title, year)
    if type:
        title = '%s, %s' % (title, type)
    if attedanceId:
        cols = '"%s"' % (labels.COL_ATTENDANCE,)
        attedance = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                             '"%s" = %s' % (labels.COL_ATTENDANCE_MAP, attedanceId))
        title = '%s, (frekwencja: %s)' % (title, attedance[0][0])
    if presenceId:
        cols = '"%s"' % (labels.COL_PRESENCE,)
        presence = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                             '"%s" = %s' % (labels.COL_PRESENCE_MAP, presenceId))
        title = '%s, (obecność: %s)' % (title, presence[0][0])
    if marksId:
        cols = '"%s"' % (labels.COL_AVERAGE_MARKS,)
        marks = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols,
                                            '"%s" = %s' % (labels.COL_AVERAGE_MARKS_MAP, marksId))
        title = '%s, (średnia ocen: %s)' % (title, marks[0][0])

    return title


def show_boxplot_chart(self, file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year):
    values, stat_cols, filtered, answersNo = retrive_data(file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year)
    if values:
        title = create_title(year, userId, table, type, courseId, attedanceId, presenceId, marksId)
        title = '%s\n%s' % (labels.BOXPLOT, title,)
        # print("ELO MAKRELO")
        print("\nvalues: ")
        print(values)
        print("\nstat_cols: ")
        print(stat_cols)
        print("\nfiltered: ")
        print(filtered)
        print("\ntitle: ")
        print(title)
        print("\nanswersNo: ")
        print(answersNo)
        boxplot_chart(box_plot_data=filtered, xlabels=stat_cols, title=title, ylabel=labels.VALUES)
    else:
        QMessageBox.warning(self, 'Info', 'Brak danych do wyświetlenia...')


def show_bar_chart(self, file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year):
    values, stat_cols, filtered, answersNo = retrive_data(file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year)
    if values:
        # print(values)

        chart_data = []
        for i in range(0, len(values)):
            temp = [0 if v is None else v for v in values[i]]
            chart_data.append(temp)
        chart_data = list(map(list, zip(*chart_data)))
        chart_data = [list(xi for xi in x) for x in chart_data]

        values_array = np.asarray(chart_data)

        values = list(values_array.sum(1) / (values_array != 0).sum(1).astype(float))
        values = [float('%.2f' % round(elem, 2)) for elem in values]
        print(values)

        title = create_title(year, userId, table, type, courseId, attedanceId, presenceId, marksId)
        bar_chart(objects=stat_cols, values=values, title=title, ylabel=labels.VALUES, )
    else:
        QMessageBox.warning(self, 'Info', 'Brak danych do wyświetlenia...')


def show_respondent_data(self, file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year):
    # show_columns.sort()
    values, stat_cols, filtered, answersNo = retrive_data(
        file, table, userId, departmentId, courseId, type, attedanceId, presenceId, marksId, show_columns, year)
    print(values)
    print(stat_cols)
    print(filtered)
    print(answersNo)

    if values and stat_cols and filtered:
        # ()
        # print(values)
        valuesT = []
        for i in range(0, len(values)):
            temp = [0 if v is None else v for v in values[i]]
            valuesT.append(temp)
        valuesT = list(map(list, zip(*valuesT)))

        cols = base.select_table_columns(file, labels.TABLE_MAP)

        stat_cols_sort = []
        if list(stat_cols):
            for stat_col in list(stat_cols):
                for show_col in show_columns:
                    if show_col in stat_col :
                        stat_cols_sort.append(show_col)
        else:
            QMessageBox.warning(self, 'Info', 'Niespodziewany format kolumn...')
        # print(show_columns)
        # print(stat_cols)
        # print(stat_cols_sort)
        # print(len(valuesT))
        if len(stat_cols_sort) == len(valuesT):
            for i in range(0, len(valuesT)):
                plt.subplot(len(valuesT)+1, 1, i+1)
                x = []
                y = []
                cols = '"%s","%s","%s","%s"' % \
                       (stat_cols_sort[i], labels.COL_PRESENCE_MAP, labels.COL_AVERAGE_MARKS_MAP, labels.COL_ATTENDANCE_MAP)
                condition = '"%s" IS NOT NULL' % (stat_cols_sort[i],)
                result = base.select_table_data_2(_db_path, labels.TABLE_MAP, cols, condition)
                print(result)
                list_of_lists = [list(xi for xi in elem if xi is not None) for elem in result]
                if list_of_lists:
                    for j in range(0, len(list_of_lists)):
                        # print(valuesT[i])
                        print('%s - ilość: %d' % (list_of_lists[j][0], valuesT[i].count(list_of_lists[j][1]),))
                        x.append(int(valuesT[i].count(list_of_lists[j][1])))
                        y.append(list_of_lists[j][0])
                    print('Brak odpowiedzi - ilość: %d' % (valuesT[i].count(0),))
                    x.append(valuesT[i].count(0),)
                    y.append('Brak odpowiedzi')

                # print(x)
                # print(y)
                plt.barh(y, x, align='center', alpha=0.5)
                xint = range(min(x), math.ceil(max(x)) + 1)
                plt.xticks(xint)

                stat_cols_sort[i]
                plt.title('\nDane z: \'%s\'' % (stat_cols_sort[i], ))

            title = create_title(year, userId, table, type, courseId, attedanceId, presenceId, marksId)
            plt.suptitle(title)
            mng = plt.get_current_fig_manager()
            mng.window.state("zoomed")
            plt.tight_layout()
            plt.show()

        else:
            QMessageBox.warning(self, 'Info', 'Niespodziewany format danych...')
    else:
        QMessageBox.warning(self, 'Info', 'Brak danych do wyświetlenia...')

