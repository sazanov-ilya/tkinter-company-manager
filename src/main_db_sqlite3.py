import os
import errno
import re
import sqlite3
import tkinter.messagebox as mb

# path_db = '../db'  # Относительный путь
path_db = 'db'  # Относительный путь

# current_dir = os.path.dirname(__file__)  # Получаем путь к текущей папке
# parent_dir = os.path.dirname(current_dir)  # Путь на уровень выше
# path_db = os.path.join(parent_dir, 'db')  # Путь к папке 'db' на уровень выше


def create_db_dir():
    # path = os.curdir  # Текущая папка
    # path = os.getcwd()  # Абсолютный путь
    try:
        os.makedirs(path_db)
    except OSError as exception:
        # Игнорируем ошибку "папка уже создана", но выводим все остальные
        if exception.errno != errno.EEXIST:
            mb.showerror("ОШИБКА!", exception)
            raise

    # if not os.path.exists('db'):  # Если на существует
    #    os.makedirs('db')
    #    print('Создана папка')

    # print(os.walk(path))
    # for dirs, folder, files in os.walk(path):
    #    print('Выбранный каталог: ', dirs)
    #    print('Вложенные папки: ', folder)
    #    print('Файлы в папке: ', files)
    #    print('\n')
    #    # Отобразит только корневую папку и остановит цикл
    #    break


class DB:
    """Класс подключения к БД sqlite3."""
    def __init__(self):
        create_db_dir()  # Создаем папку для БД
        self.conn_sqlite3 = sqlite3.connect(path_db + '/' + 'company_manager.db')  # Создаем БД
        self.c_sqlite3 = self.conn_sqlite3.cursor()

        self.c_sqlite3.execute("PRAGMA foreign_keys=ON")  # Для работы каскадного удаления

        # #########################
        # Создаем свою функцию sql для приведения к нижнему регистру
        # Через связывание с процедурой _to_lowercase
        # Поскольку стандартная lower не работает с кириллицей
        # ####################################################
        self.conn_sqlite3.create_function("MY_LOWER", 1, self._to_lowercase)

        self.conn_sqlite3.create_function("GET_DESCRIPTION", 1, self._get_text_before_first_enter)

        # #####
        # roles
        # #####
        """Таблица ролей пользователя, для назначения прав доступа."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS roles (
                   id_role integer primary key autoincrement not null,
                   role_name text not null,
                   role_description text,
                   user integer,
                   CONSTRAINT roles_unq UNIQUE(role_name, user))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            print('Ошибка: ' + err.__str__())

        # #####
        # users
        # #####
        """Таблица пользователей."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS users (
                   id_user integer primary key autoincrement not null,
                   user_login text not null,
                   user_password text,
                   user_name text,
                   user_description text,
                   is_admin int default(0),
                   is_deleted int default(0),
                   CONSTRAINT users_unq UNIQUE (user_login))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            print('Ошибка: ' + err.__str__())

        # ###########
        # users_roles
        # ###########
        """Таблица для связи пользователей и ролей (многие-ко-многим)."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS users_roles (
                   id_users_roles integer primary key autoincrement not null,
                   id_user integer not null,
                   id_role integer not null,
                   FOREIGN KEY(id_user) REFERENCES users(id_user) ON DELETE CASCADE,
                   FOREIGN KEY(id_role) REFERENCES roles(id_role) ON DELETE CASCADE,
                   CONSTRAINT users_roles_unq UNIQUE(id_user, id_role))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            print('Ошибка: ' + err.__str__())

        # #########
        # companies
        # #########
        """Таблица компаний."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS companies (
                   id_company integer primary key autoincrement not null,
                   company_name text not null,
                   company_description text,
                   CONSTRAINT companies_unq UNIQUE(company_name))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            print('Ошибка: ' + err.__str__())

        # ################
        # connection_types
        # ################
        """Таблица типов подключения."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS connection_types(
                   id_connection_type integer primary key autoincrement not null,
                   connection_type_name text not null,
                   connection_type_description text,
                   CONSTRAINT connection_types_unq UNIQUE(connection_type_name))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        # ###########
        # connections
        # ###########
        """
        Таблица подключений, является связкой таблицы компании и 
        типа подключения (многие-ко-многим).
        """
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS connections (
                   id_connection integer primary key autoincrement not null,
                   id_company integer not null,
                   id_connection_type integer not null,
                   connection_ip text, connection_description text,
                   FOREIGN KEY(id_company) REFERENCES companies(id_company) ON DELETE CASCADE,
                   FOREIGN KEY(id_connection_type) REFERENCES connection_types(id_connection_type) ON DELETE CASCADE,
                   CONSTRAINT connections_unq UNIQUE(id_company, id_connection_type, connection_ip))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        # ######
        # logins
        # ######
        """Таблица логинов для подключения."""
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS logins(
                   id_login integer primary key autoincrement not null,
                   id_connection integer not null,
                   login_name text,
                   login_password text,
                   login_description text,
                   id_creator integer,
                   FOREIGN KEY(id_connection) REFERENCES connections(id_connection) ON DELETE CASCADE,
                   FOREIGN KEY(id_creator) REFERENCES users(id_user) ON DELETE SET NULL,
                   CONSTRAINT logins_unq UNIQUE(id_connection, login_name))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        # ###################
        # permission_by_roles
        # ###################
        """
        Таблица для связи логинов и ролей (многие-ко-многим),
        используется для назначения прав доступа через роли.
        """
        try:
            self.c_sqlite3.execute(
                '''CREATE TABLE IF NOT EXISTS permission_by_roles(
                   id_permission integer primary key autoincrement not null,
                   id_login integer not null,
                   id_role integer not null,
                   FOREIGN KEY(id_login) REFERENCES logins(id_login) ON DELETE CASCADE,
                   FOREIGN KEY(id_role) REFERENCES roles(id_role) ON DELETE CASCADE,
                   CONSTRAINT permission_by_roles_unq UNIQUE(id_login, id_role))
                '''
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    @staticmethod
    def _to_lowercase(string):
        """Возвращает строку в нижнем регистре."""
        return str(string).lower()

    @staticmethod
    def _get_text_before_first_enter(text):
        """
        Возвращает только первую строку из текста (до первого переноса на новую строку),
        если текст состоит из нескольких строк, то в конец возвращаемой строки
        добавляется многоточие (...).
        """
        text_dict = re.split(r'\n', str(text), maxsplit=1)
        # Если больше одной строки, то выводим только первую
        if len(text_dict) > 1:
            return text_dict[0] + ' ...'
        else:
            return text_dict[0]

    # ###########
    # стиль qmark
    # curs.execute("SELECT weight FROM Equipment WHERE name = ? AND price = ?",
    #             ['lead', 24])

    # названный стиль
    # curs.execute("SELECT weight FROM Equipment WHERE name = :name AND price = :price",
    #         {name: 'lead', price: 24})

    # Именованные параметры
    # sql = "SELECT column FROM table WHERE col1=%s AND col2=%s"
    # params = (col1_value, col2_value)
    # cursor.execute(sql, params)

    # curs.execute("SELECT weight FROM Equipment WHERE name = :name AND price = :price",
    #         {name: 'lead', price: 24})

# # Множественная вствыка
# weekdays = ["Воскресенье", "Понедельник", "Вторник", "Среда",
#  "Четверг", "Пятница", "Суббота",
# "Воскресенье"]
#  import sqlite as db
#  c = db.connect(database="tvprogram")
#  cu = c.cursor()
#  cu.execute("""DELETE FROM wd;""")
#  cu.executemany("""INSERT INTO wd VALUES (%s, %s);""",
#  enumerate(weekdays))
#  c.commit()
#  c.close()


#    # пример 1
#    try:
#        cursor.execute("INSERT INTO ...", params)
#    except sqlite3.Error as err:
#        logger.error(err.message)

#    # пример 2
#    import sqlite3 as lite
#
#    con = lite.connect('test.db')
#
#    with con:
#        cur = con.cursor()
#        cur.execute("CREATE TABLE Persons(Id INT, Name TEXT)")
#        cur.execute("INSERT INTO Persons VALUES(1,'Joe')")
#        cur.execute("INSERT INTO Persons VALUES(1,'Jenny')")
#
#        try:
#            cur.execute("INSERT INTO Persons VALUES(1,'Jenny', 'Error')")
#            self.con.commit()
#
#        except lite.Error as er:
#            print
#            'er:', er.message
#
#        # Retrieve data
#        cur.execute("SELECT * FROM Persons")
#        rows = cur.fetchall()
#        for row in rows:
#            print
#            row
