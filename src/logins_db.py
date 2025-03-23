import sqlite3
import tkinter.messagebox as mb

# Свои модули
import main_db_sqlite3 as db  # БД - общий
import users_db as users_db


class LoginsDB(db.DB):
    """ Класс работы с таблицей типов подключения """
    def __init__(self):
        super().__init__()  # вызов __init__ базового класса

        self.roles_db = users_db.RolesDB()  # Подключаем роли (для назначения прав)

    ########################
    # Процедуры для logins #
    ########################
    def get_login_by_id(self, id_login):
        """ Процедура возврата данных логина по переданному id_login
        :param id_login:
        :return: Кортеж значений
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT l.id_login, l.login_name, l.login_password, l.login_description, u.user_login
                FROM logins as l, users as u
                WHERE l.id_creator=u.id_user AND id_login=?''', [id_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_login_by_id:\n' + err.__str__())

        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_logins_list_by_id_connection_for_admin(self, id_connection, logins_filter_dict):
        """ Процедура возврата списка логинов по id_connection (вывод на форму)
        :param id_connection:
        :param logins_filter_dict: Словарь фильтров
        :return: Набор кортежей со списком логинов согласно фильтров
        """
        match logins_filter_dict:
            # login_name/login_description
            case {'login_name': login_name, 'login_description': login_description, **remainder} if not remainder:
                like_login_name = ('%' + login_name.lower() + '%')
                like_login_description = ('%' + login_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_login,
                                  login_name,
                                  login_password,
                                  GET_DESCRIPTION(login_description)
                           FROM logins 
                           WHERE id_connection = ?
                             AND MY_LOWER(login_name) LIKE ?
                             AND MY_LOWER(login_description) LIKE ?
                        ''', [id_connection, like_login_name, like_login_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_admin:\n' + err.__str__())
            # login_name
            case {'login_name': login_name, **remainder} if not remainder:
                like_login_name = ('%' + login_name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_login,
                                  login_name,
                                  login_password,
                                  GET_DESCRIPTION(login_description)
                           FROM logins 
                           WHERE id_connection = ?
                             AND MY_LOWER(login_name) LIKE ?
                        ''', [id_connection, like_login_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_admin:\n' + err.__str__())
            # login_description
            case {'login_description': login_description, **remainder} if not remainder:
                like_login_description = ('%' + login_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_login,
                                  login_name,
                                  login_password,
                                  GET_DESCRIPTION(login_description)
                           FROM logins 
                           WHERE id_connection = ?
                             AND MY_LOWER(login_description) LIKE ?
                        ''', [id_connection, like_login_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_admin:\n' + err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_login,
                                  login_name,
                                  login_password,
                                  GET_DESCRIPTION(login_description)
                           FROM logins 
                           WHERE id_connection = ?
                        ''',  [id_connection]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_admin:\n' + err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_logins_list_by_id_connection_for_user(self, id_connection, id_user, logins_filter_dict):
        """ Процедура возврата списка логинов по id_connection и id_user (вывод на форму)
        :param id_connection:
        :param id_user:
        :param logins_filter_dict: Словарь фильтров
        :return: Набор кортежей со списком логинов согласно фильтров
        """
        match logins_filter_dict:
            # login_name/login_description
            case {'login_name': login_name, 'login_description': login_description, **remainder} if not remainder:
                like_login_name = ('%' + login_name.lower() + '%')
                like_login_description = ('%' + login_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT l.id_login,
                                  l.login_name,
                                  l.login_password,
                                  GET_DESCRIPTION(l.login_description)
                           FROM logins as l,
                                permission_by_roles as pr,
                                users_roles as ur
                           WHERE l.id_connection = ?
                             AND l.id_login =  pr.id_login
                             AND pr.id_role = ur.id_role
                             AND ur.id_user = ?
                             AND MY_LOWER(l.login_name) LIKE ?
                             AND MY_LOWER(l.login_description) LIKE ?
                        ''', [id_connection, id_user, like_login_name, like_login_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_user:\n' + err.__str__())
            # login_name
            case {'login_name': login_name, **remainder} if not remainder:
                like_login_name = ('%' + login_name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT l.id_login,
                                  l.login_name,
                                  l.login_password,
                                  GET_DESCRIPTION(l.login_description)
                           FROM logins as l,
                                permission_by_roles as pr,
                                users_roles as ur
                           WHERE l.id_connection = ?
                             AND l.id_login =  pr.id_login
                             AND pr.id_role = ur.id_role
                             AND ur.id_user = ?
                             AND MY_LOWER(l.login_name) LIKE ?
                        ''', [id_connection, id_user, like_login_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_user:\n' + err.__str__())
            # login_description
            case {'login_description': login_description, **remainder} if not remainder:
                like_login_description = ('%' + login_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT l.id_login,
                                  l.login_name,
                                  l.login_password,
                                  GET_DESCRIPTION(l.login_description)
                           FROM logins as l,
                                permission_by_roles as pr,
                                users_roles as ur
                           WHERE l.id_connection = ?
                             AND l.id_login =  pr.id_login
                             AND pr.id_role = ur.id_role
                             AND ur.id_user = ?
                             AND MY_LOWER(l.login_description) LIKE ?
                        ''', [id_connection, id_user, like_login_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_user:\n' + err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT l.id_login,
                                  l.login_name,
                                  l.login_password,
                                  GET_DESCRIPTION(l.login_description)
                           FROM logins as l,
                                permission_by_roles as pr,
                                users_roles as ur
                           WHERE l.id_connection = ?
                             AND l.id_login =  pr.id_login
                             AND pr.id_role = ur.id_role
                            AND ur.id_user = ?''', [id_connection, id_user]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_logins_list_by_id_connection_for_user:\n' + err.__str__())

        data = []  # запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_login_name_for_check_exists(self, id_connection, login_name):
        """ Процедура проверки наличия логина по id_connection и login_name
            (проверка на дубль)
        :param id_connection:
        :param login_name:
        :return: login_name/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT login_name
                   FROM logins
                   WHERE id_connection = ?
                     and login_name = ?
                ''', [id_connection, login_name]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_login_name_for_check_exists:\n' + err.__str__())

        data = self.c_sqlite3.fetchone()

        if data is not None:
            return data[0]
        else:
            return None

    def get_id_login(self, id_connection, login_name):
        """ Процедура получения id_login
        :param id_connection:
        :param login_name:
        :return: id_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_login FROM logins WHERE id_connection = ? AND login_name = ?''',
                [id_connection, login_name]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_id_login:\n' + err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_permission_by_id_login(self, id_login):
        """ Процедура возвращает список ролей с назначенными правами по id_login
        :return: набор кортежей id_role, role_name, permission (0/1), id_permission
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT r.id_role,
                          r.role_name || " " || CASE WHEN r.user = 0 THEN "(role)" ELSE "(user)" END as role,
                          pr.id_permission as id_permission,
                          CASE WHEN pr.id_permission is NULL THEN 0 ELSE 1 END as permission
                   FROM(SELECT id_role, role_name, user FROM roles) as r
                   LEFT JOIN (select id_permission, id_role
                              from permission_by_roles
                              where id_login = ?
                             ) as pr ON pr.id_role = r.id_role
                   ORDER BY r.role_name''', [id_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_permission_by_like_role_name(self, id_login, role_name):
        """ Процедура возвращает список ролей с назначенными правами через LIKE по role_name
        :return: набор кортежей id_role, role_name, permission (0/1), id_permission
        """
        role_name_like = ('%' + role_name.lower() + '%')
        try:
            self.c_sqlite3.execute(
                '''SELECT r.id_role,
                          r.role_name,
                          pr.id_permission as id_permission,
                          CASE WHEN pr.id_permission is NULL THEN 0 ELSE 1 END as permission
                   FROM(SELECT id_role, role_name 
                        FROM roles
                        WHERE LOWER(role_name) LIKE ?
                        ) as r
                   LEFT JOIN (select id_permission, id_role
                              from permission_by_roles
                              where id_login = ?
                             ) as pr ON pr.id_role = r.id_role
                   ORDER BY r.role_name''', [role_name_like, id_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def save_new_login(self, id_connection, login_name, login_password, login_description, id_creator, id_role):
        """ Процедура сохранения нового логина для подключения и добавления прав на сохраненный логин
        :param id_connection:
        :param login_name:
        :param login_password:
        :param login_description:
        :param id_creator:
        :param id_role:
        :return: No
        """
        # Сохраняем логин
        new_id_login = self.insert_new_login(id_connection, login_name, login_password, login_description, id_creator)
        # Сохраняем права на логин
        self.insert_permission_by_roles(new_id_login, id_role)
        # self.insert_permission_by_users(id_login, id_creator)

    def insert_new_login(self, id_connection, login_name, login_password, login_description, id_creator):
        """ Процедура сохранения нового логина для подключения через id_connection
        :param id_connection:
        :param login_name:
        :param login_password:
        :param login_description:
        :param id_creator:
        :return: new_id_login
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO logins(id_connection, login_name, login_password, login_description, id_creator)
                VALUES(?, ?, ?, ?, ?)''', (id_connection, login_name, login_password, login_description, id_creator)
            )
            self.conn_sqlite3.commit()
            return self.get_new_id_login()  # Возвращаем id_login по добавленной строке
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'insert_new_login:\n' + err.__str__())

    def get_new_id_login(self):
        """ Процедура получения нового id_login
        :return: id_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_login FROM logins WHERE rowid=last_insert_rowid()'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_new_id_login:\n' + err.__str__())
        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def insert_permission_by_roles(self, id_login, id_role):
        """ Процедура добавления прав на роль
        :param id_login:
        :param id_role:
        :return:
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO permission_by_roles(id_login, id_role) VALUES(?, ?)''', (id_login, id_role)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'insert_permission_by_roles:\n' + err.__str__())

    def delete_permission_by_id(self, id_permission):
        """ Процедура удаления прав на роль
        :param id_permission:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''DELETE FROM permission_by_roles WHERE id_permission=?''', [id_permission]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'delete_permission_by_id:\n' + err.__str__())

    def update_login_by_id(self, id_login, login_name, login_password, login_description):
        """ Процедура обновления логина по id_login
        :param id_login:
        :param login_name:
        :param login_password:
        :param login_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE logins SET login_name=?, login_password=?, login_description=?
                WHERE id_login=?''',
                (login_name, login_password, login_description, id_login)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'update_login_by_id:\n' + err.__str__())

    def delete_logins(self, ids):
        """ Процедура удаления логинов
        :param ids: Список id логинов
        :return:
        """
        try:
            for id in ids:
                self.c_sqlite3.execute(
                    '''DELETE FROM logins WHERE id_login=?''', [id]
                )
                self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'delete_logins:\n' + err.__str__())
