import sqlite3
import tkinter.messagebox as mb

# Свои модули
import _service as srv
import main_db_sqlite3 as db  # БД - общий


# Администратор по умолчанию
admin_dict = {
    'admin_login': 'admin',
    'admin_password': 'admin',
    # 'role_name': 'admin',
    'admin_name': 'admin',
    'admin_description': 'Администратор по умолчанию',
    'is_admin': 1  # True
}
# admin_dict.get('admin_login', '')


def _get_user_is_base_admin(user_login):
    """ !Процедура получения признака "пользователь -> базовый admin"
        (для запрета на удаление и редактирование учетной записи)
    :param user_login:
    :return: True/False
    """
    if admin_dict.get('admin_login', '') == user_login:
        return True
    return False


def _get_login_for_admin():
    """Процедура получения логина для администратора (admin_login)
    (для создания связанной роли).
    :return: admin_login
    """
    login_for_admin = admin_dict['admin_login']
    return login_for_admin


def get_admin_dict():
    """Процедура возвращает копию словаря данных базового администратора."""
    return admin_dict.copy()


class RolesDB(db.DB):
    """Класс работы с таблицей ролей."""
    def __init__(self):
        super().__init__()  # Вызов __init__ базового класса

    @staticmethod
    def get_role_name_for_admin():
        """Процедура получения наименования роли базового админа.
        :return: role_name/None
        """
        role_name_for_admin = _get_login_for_admin()
        return role_name_for_admin

    def get_role_for_check_exists(self, role_name, user=0):
        """ !Процедура проверки наличия роли по наименованию (проверка на дубль)
        :param role_name:
        :param user:
        :return: role_name/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT role_name 
                   FROM roles 
                   WHERE role_name = ? 
                     AND user = ?
                ''', [role_name, user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_role_id_by_name(self, role_name, user=0):
        """ !Процедура получения id роли по ее имени
        :param role_name:
        :param user:
        :return: id_role/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_role 
                   FROM roles 
                   WHERE role_name = ? 
                     AND user = ?
                ''', [role_name, user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_role_name_by_id(self, id_role):
        """ Процедура получения имени роли по ее id
        :param id_role:
        :return: role_name/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT role_name FROM roles WHERE id_role = ?''',
                [id_role]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_role_by_id(self, id_role):
        """ Процедура получения данных роли по ее id
        :param id_role:
        :return:
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_role, role_name, role_description, user FROM roles WHERE id_role = ?''', [id_role]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data
        else:
            return None

    def get_role_list_all(self):
        """ Процедура возвращает список ролей
        :return: набор кортежей id_role и role_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_role, role_name FROM roles WHERE ifnull(user, 0) = 0'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_role_list_for_user(self, id_user):
        """ Процедура возвращает список ролей пользователя по id_user
        :return: набор кортежей id_role и role_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT r.id_role, r.role_name, r.role_description
                FROM roles as r, users_roles as ur, users as u\
                WHERE r.id_role = ur.id_role AND ur.id_user = u.id_user AND u.id_user = ?''',
                [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_role_list_for_user_roles(self, id_user):
        """ Процедура возвращает список ролей для формы управления ролями пользователя
        с отметкой назначенных пользователю ролей по id_login
        :return: набор кортежей id_role, role_name, exists_role (0/1), id_users_roles
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT r.id_role,
                          r.role_name,
                          ur.id_users_roles as id_users_roles,
                          CASE WHEN ur.id_users_roles is NULL THEN 0 ELSE 1 END as exists_role
                FROM(SELECT id_role, role_name FROM roles
                     WHERE user = 0) as r
                LEFT JOIN (select id_users_roles, id_role
                           from users_roles
                           where id_user = ?
                          ) as ur ON ur.id_role = r.id_role
                ORDER BY r.role_name''', [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_role_list_for_user_roles_by_like_role_name(self, id_user, role_name):
        """ Процедура возвращает список ролей пользователя для формы управления ролями пользователя
        с назначенными правами через LIKE по role_name
        :return: набор кортежей id_role, role_name, exists_role (0/1), id_users_roles
        """
        role_name_like = ('%' + role_name + '%')
        try:
            self.c_sqlite3.execute(
                '''SELECT r.id_role,
                          r.role_name,
                          ur.id_users_roles as id_users_roles,
                          CASE WHEN ur.id_users_roles is NULL THEN 0 ELSE 1 END as exists_role
                   FROM(SELECT id_role, role_name FROM roles
                        WHERE user = 0
                          AND role_name LIKE ?) AS r
                   LEFT JOIN (select id_users_roles, id_role
                              from users_roles
                              where id_user = ?
                             ) AS ur ON ur.id_role = r.id_role
                   ORDER BY r.role_name''', [role_name_like, id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_role_list_not_user(self, id_user):
        """ Процедура возвращает список ролей пользователя по id_user
        :return: набор кортежей id_role и role_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT r1.id_role, r1.role_name, r1.role_description
                FROM roles as r1
                WHERE ifnull(r1.user, 0) = 0
                AND r1.id_role NOT IN (SELECT r.id_role
                                       FROM roles as r, users_roles as ur, users as u
                                       WHERE r.id_role = ur.id_role
                                       AND ur.id_user = u.id_user AND u.id_user = ?)''',
                [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_roles_by_filter(self, role_name, role_description):
        """ Процедура возврата списка ролей согласно фильтрам
        :param role_name:
        :param role_description:
        :return: Набор кортежей со списком ролей согласно фильтрам
        """
        if role_name and role_description:  # Проверяем фильтр
            like_role_name = ('%' + role_name.lower() + '%')
            like_role_description = ('%' + role_description.lower() + '%')
            try:
                self.c_sqlite3.execute(
                    '''SELECT id_role,
                              role_name,
                              GET_DESCRIPTION(role_description)
                       FROM roles WHERE ifnull(user, 0) = 0 
                        AND MY_LOWER(role_name) LIKE ? 
                        AND MY_LOWER(role_description) LIKE ?
                    ''', [like_role_name, like_role_description]
                )
            except sqlite3.Error as err:
                mb.showerror("ОШИБКА!", err.__str__())

        elif role_name:  # Проверяем фильтр
            like_role_name = ('%' + role_name.lower() + '%')
            try:
                self.c_sqlite3.execute(
                    '''SELECT id_role,
                              role_name,
                              GET_DESCRIPTION(role_description)
                       FROM roles WHERE ifnull(user, 0) = 0 
                        AND MY_LOWER(role_name) LIKE ?
                    ''', [like_role_name]
                )
            except sqlite3.Error as err:
                mb.showerror("ОШИБКА!", err.__str__())

        elif role_description:  # Проверяем фильтр
            like_role_description = ('%' + role_description.lower() + '%')
            try:
                self.c_sqlite3.execute(
                    '''SELECT id_role,
                              role_name,
                              GET_DESCRIPTION(role_description)
                       FROM roles WHERE ifnull(user, 0) = 0 
                        AND MY_LOWER(role_description) LIKE ?
                    ''', [like_role_description]
                )
            except sqlite3.Error as err:
                mb.showerror("ОШИБКА!", err.__str__())

        else:
            try:
                self.c_sqlite3.execute(
                    '''SELECT id_role,
                              role_name,
                              GET_DESCRIPTION(role_description)
                       FROM roles WHERE ifnull(user, 0) = 0
                    '''
                )
            except sqlite3.Error as err:
                mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def insert_new_role(self, role_name, role_description='', user=0):
        """ Процедура создания новой роли
        :param role_name:
        :param role_description:
        :param user: Признак связанной с логином пользователя роли (0/1)
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO roles(role_name, role_description, user) VALUES(?, ?, ?)''',
                ([role_name, role_description, user])
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_roles(self, ids_roles):
        """ Процедура удаления ролей, кроме базовых
        :param ids_roles: Список id ролей
        :return: No
        """
        try:
            for id_role in ids_roles:
                # Пропускаем роль для администратора
                if self.get_role_name_by_id(id_role) != self.get_role_name_for_admin():
                    self.c_sqlite3.execute(
                        '''DELETE FROM roles WHERE id_role=?''', [id_role]
                    )
                    self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_role_by_id(self, id_role, role_name, role_description):
        """ Процедура обновления роли
        :param id_role:
        :param role_name:
        :param role_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE roles SET role_name = ?, role_description = ? WHERE id_role = ?''',
                [role_name, role_description, id_role]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'update_role_by_id:\n' + err.__str__())

    def update_role_name_by_user_id(self, role_name, role_description, id_user):
        """ Процедура обновления наименования связанной роли
        :param role_name:
        :param role_description:
        :param id_user:
        :return:
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE roles SET role_name = ?, role_description = ? WHERE user = ?''',
                [role_name, role_description, id_user]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_role_by_name(self, role_name):
        """ Процедура удаления роли по ее наименованию (для удаления связанных ролей)
        :param role_name:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''DELETE FROM roles WHERE role_name=?''', [role_name]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())


class UsersDB(db.DB):
    """ Класс работы с таблицей пользователей """
    def __init__(self):
        super().__init__()  # вызов __init__ базового класса

        self.roles_db = RolesDB()  # БД ролей
        self.user_roles_db = UsersRolesDB()  # БД роли пользователя

        self.check_count_admins()

    @staticmethod
    def get_user_login_for_admin():
        """ !Процедура получения наименования роли базового админа
        :return: role_name/None
        """
        # Получаем наименование роли по ключу 'is_admin': True
        # role_name = self.roles_dict[
        #     next((i for i, x in enumerate(self.roles_dict) if x['is_admin']), None)].get('role_name', None)
        # if role_name is not None:
        #     return role_name
        # else:
        #     return None

        user_login_for_admin = _get_login_for_admin()
        return user_login_for_admin

    def check_count_admins(self):
        """ !Процедура проверки количества администраторов и, если необходимо,
            создаем или открываем базового администратора
            :return: No
        """
        # Получаем число администраторов
        count_admins = len(self.get_admins_list())

        if count_admins == 0:  # Если нет, то
            if self.get_user_id_by_login(self.get_user_login_for_admin()):
                # Если есть, то открываем
                self.update_is_deleted_by_login(self.get_user_login_for_admin(), 0)
            else:
                # Создаем базового админа
                admin_dict_tmp = get_admin_dict()
                self.save_new_user(admin_dict_tmp.get('admin_login', 'admin'),
                                   admin_dict_tmp.get('admin_password', 'admin'),
                                   admin_dict_tmp.get('admin_name', ''),
                                   admin_dict_tmp.get('admin_description', ''),
                                   admin_dict_tmp.get('is_admin', 0))
        elif count_admins == 1:  # Если 1 администратор, то ничего не нужно
            pass
        else:  # Если больше 1, то блокируем базового администратора
            self.update_is_deleted_by_login(self.get_user_login_for_admin(), 1)

    def get_admins_list(self):
        """ !Процедура возвращает список всех активных администраторов
        :return: список кортежей id_user и user_login
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_user,
                          user_login
                   FROM users
                   WHERE is_deleted=0
                     AND is_admin=1
                ''',
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_admin_list:\n' + err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_user_list(self):
        """ Процедура возвращает список пользователей
        :return: набор кортежей id_user и user_login
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_user, user_login FROM users'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_user_list:\n' + err.__str__())

        data = []  # запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_users_by_filter(self, users_filter_dict):
        """ Процедура возврата списка пользователей согласно фильтрам
        :param users_filter_dict:
        :return: Набор кортежей со списком пользователей согласно фильтрам
        """
        self.check_count_admins()   # Для страховки

        match users_filter_dict:
            # user_login/user_name/user_description
            case {'user_login': user_login, 'user_name': user_name,
                  'user_description': user_description, **remainder} if not remainder:
                like_user_login = ('%' + user_login.lower() + '%')
                like_user_name = ('%' + user_name.lower() + '%')
                like_user_description = ('%' + user_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_login) LIKE ?
                             AND MY_LOWER(u.user_name) LIKE ?
                             AND MY_LOWER(u.user_description) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_login, like_user_name, like_user_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_login/user_name
            case {'user_login': user_login, 'user_name': user_name, **remainder} if not remainder:
                like_user_login = ('%' + user_login.lower() + '%')
                like_user_name = ('%' + user_name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_login) LIKE ?
                             AND MY_LOWER(u.user_name) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_login, like_user_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_login/user_description
            case {'user_login': user_login, 'user_description': user_description, **remainder} if not remainder:
                like_user_login = ('%' + user_login.lower() + '%')
                like_user_description = ('%' + user_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_login) LIKE ?
                             AND MY_LOWER(u.user_description) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_login, like_user_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_name/user_description
            case {'user_name': user_name, 'user_description': user_description, **remainder} if not remainder:
                like_user_name = ('%' + user_name.lower() + '%')
                like_user_description = ('%' + user_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_name) LIKE ?
                             AND MY_LOWER(u.user_description) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_name, like_user_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_login
            case {'user_login': user_login,  **remainder} if not remainder:
                like_user_login = ('%' + user_login.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                        FROM users AS u
                        JOIN users_roles AS ur ON ur.id_user = u.id_user
                        JOIN roles AS r ON r.id_role = ur.id_role
                        WHERE MY_LOWER(u.user_login) LIKE ?
                        GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                    ''', [like_user_login]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_name
            case {'user_name': user_name, **remainder} if not remainder:
                like_user_name = ('%' + user_name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_name) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # user_description
            case {'user_description': user_description, **remainder} if not remainder:
                like_user_description = ('%' + user_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           WHERE MY_LOWER(u.user_description) LIKE ?
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted
                        ''', [like_user_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT u.id_user,
                                  u.user_login,
                                  group_concat(r.role_name) AS role_name,
                                  u.user_name,
                                  GET_DESCRIPTION(u.user_description),
                                  u.is_deleted
                           FROM users AS u
                           JOIN users_roles AS ur ON ur.id_user = u.id_user
                           JOIN roles AS r ON r.id_role = ur.id_role
                           GROUP  BY u.id_user, u.user_login, u.user_name, u.user_description, u.is_deleted'''
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_users_by_filter:\n' + err.__str__())

        data = []  # Возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_user_id_by_login(self, user_login):
        """ Процедура получения id_user по user_login
        :param user_login:
        :return: id_user/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_user FROM users WHERE user_login = ?''',
                [user_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_user_login_by_id(self, id_user):
        """ Процедура возврата user_login по id_user
        :param id_user:
        :return: user_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT user_login FROM users WHERE id_user = ?''',
                [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_user_by_id(self, id_user):
        """ !Процедура возврата данных пользователя по id_user
            (все данные по пользователю, для формы обновления)
        :param id_user:
        :return: user_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_user,
                          user_login,
                          user_password,
                          user_name,
                          user_description,
                          is_admin,
                          is_deleted
                FROM users 
                WHERE id_user = ?
            ''', [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data
        else:
            return None

    def get_user_login_for_check_auth(self, user_login):
        """ !Процедура проверки наличия пользователя по логину
            (для проверки при авторизации)
        :param user_login:
        :return: user_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT user_login 
                   FROM users 
                   WHERE is_deleted = 0 
                     AND user_login = ?
                ''', [user_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_user_login_for_check_exists(self, user_login):
        """ !Процедура проверки наличия пользователя по логину
            (для проверки на дубль пользователя)
        :param user_login:
        :return: user_login/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT user_login 
                   FROM users 
                   WHERE user_login = ?
                ''', [user_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_password_by_login(self, user_login):
        """ Процедура получения пароля пользователя по логину
        :param user_login:
        :return: user_password
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT user_password FROM users WHERE user_login = ?''',
                [user_login]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_user_is_admin_by_user_id(self, id_user):
        """ !Процедура получения признака "пользователь -> admin"
        :param id_user:
        :return: True/False
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT is_admin
                   FROM users
                   WHERE id_user = ?
                ''', [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        is_admin = self.c_sqlite3.fetchone()
        if is_admin[0] == 1:
            return True
        else:
            return False

    def get_user_is_base_admin_by_login(self, user_login):
        """ !Процедура получения признака "пользователь -> базовый администратор"
        :param user_login:
        :return: True/False
        """
        if self.get_user_login_for_admin() == user_login:
            return True
        else:
            return False

    def save_new_user(self, user_login, user_password, user_name, user_description, is_admin):
        """ !Процедура сохранения нового пользователя с проверкой связанной роли
        :param user_login:
        :param user_password:
        :param user_name:
        :param user_description:
        :param is_admin:
        :return: No
        """
        # 1. Сохраняем пользователя и получаем его id
        id_new_user = self.insert_new_user(user_login, user_password, user_name, user_description, is_admin)

        # 2. Проверяем и создаем связанную роль
        if self.roles_db.get_role_id_by_name(user_login, id_new_user) is None:
            self.roles_db.insert_new_role(user_login,
                                          'Роль связанная с ' + user_login,
                                          id_new_user)

        # 3. Проверяем и добавляем пользователю связанную роль
        if not self.user_roles_db.get_user_role_for_check_exists(
                id_new_user, self.roles_db.get_role_id_by_name(user_login, id_new_user)):

            role_id = self.roles_db.get_role_id_by_name(user_login, id_new_user)
            self.user_roles_db.save_new_user_role(id_new_user, role_id)

    def insert_new_user(self, user_login, user_password, user_name, user_description, is_admin):
        """
        Процедура сохранения нового пользователя
        :param user_login:
        :param user_password:
        :param user_name:
        :param user_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO users(user_login, user_password, user_name, user_description, is_admin) 
                   VALUES(?, ?, ?, ?, ?)
                ''', [user_login, srv.compute_md5_hash(user_password), user_name, user_description, is_admin])
            self.conn_sqlite3.commit()
            return self.get_new_id_user()  # Возвращаем id_user по добавленной строке
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def get_new_id_user(self):
        """ Процедура получения нового id_user
        :return: id_user/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_user FROM users WHERE rowid=last_insert_rowid()'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_new_id_user:\n' + err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def update_is_deleted_by_login(self, user_login, is_deleted):
        """ !Процедура обновления is_deleted по логину
            (для блокирования/деболкирования базового администратора)
        :param user_login:
        :param is_deleted:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE users
                   SET is_deleted=?
                   WHERE user_login = ?
                ''', [is_deleted, user_login]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_user_by_id(self, id_user, user_login, user_password, user_name, user_description, is_admin, is_deleted):
        """ Процедура обновления пользователя по id_user
        :param id_user:
        :param user_login:
        :param user_password:
        :param user_name:
        :param user_description:
        :param is_admin:
        :param is_deleted:
        :return: No
        """
        # 1. Обновляем наименование связанной с пользователем роли
        self.roles_db.update_role_name_by_user_id(user_login,
                                                  'Роль связанная с ' + user_login,
                                                  id_user)

        # 2. Обновляем пользователя
        if user_password == '*':  # Если пароль не вводился
            self.update_user_by_id_without_password(id_user, user_login, user_name, user_description,
                                                    is_admin,  is_deleted)
        else:
            self.update_user_by_id_with_password(id_user, user_login, user_password, user_name, user_description,
                                                 is_admin, is_deleted)

    def update_user_by_id_with_password(self, id_user, user_login, user_password, user_name, user_description,
                                        is_admin, is_deleted):
        """ !Процедура обновления пользователя по id_user со сменой пароля
        :param id_user:
        :param user_login:
        :param user_password:
        :param user_name:
        :param user_description:
        :param is_admin:
        :param is_deleted:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE users 
                   SET user_login=?,
                       user_password=?,
                       user_name=?,
                       user_description=?,
                       is_admin=?,
                       is_deleted=?
                   WHERE id_user=?
                ''', [user_login, srv.compute_md5_hash(user_password), user_name, user_description,
                      is_admin, is_deleted, id_user]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_user_by_id_without_password(self, id_user, user_login, user_name, user_description,
                                           is_admin, is_deleted):
        """ !Процедура обновления пользователя по id_user без смены пароля
        :param id_user:
        :param user_login:
        :param user_name:
        :param user_description:
        :param is_admin:
        :param is_deleted:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE users
                   SET user_login=?,
                       user_name=?,
                       user_description=?,
                       is_admin=?,
                       is_deleted=?
                   WHERE id_user=?
                ''', [user_login, user_name, user_description, is_admin, is_deleted, id_user]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_users(self, ids):
        """ Процедура удаления пользователей
        :param ids: Список id пользователей
        :return:
        """
        for id_user in ids:
            # Проверка на базового админа
            if not _get_user_is_base_admin(self.get_user_login_by_id(id_user)):
                self.roles_db.delete_role_by_name(self.get_user_login_by_id(id_user))  # Удаляем связанную роль
                self.delete_user_by_id_user(id_user)  # Удаляем пользователя

    def delete_user_by_id_user(self, id_user):
        """ Процедура удаления пользователя по id_user
        :param id_user:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''DELETE FROM users WHERE id_user=?''', [id_user]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'delete_users:\n' + err.__str__())


class UsersRolesDB(db.DB):
    """ Класс работы с таблицей связей пользователей и ролей """
    def __init__(self):
        super().__init__()  # Вызов __init__ базового класса

        self.roles_db = RolesDB()  # Подключаем RolesDB
        # self.users_db = UsersDB()  # Подключаем UsersDB

    def get_count_user_role_by_user_id(self, id_user):
        """ Процедура возвращает список связей пользователь-роль по id_user (список id)
        :param id_user:
        :return:
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_users_roles, id_user, id_role FROM users_roles WHERE id_user = ?''',
                ([id_user])
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return [data]
        else:
            return None

    def get_user_role_list_by_user(self, id_user):
        """ Процедура возвращает список ролей пользователя по id_user (список name)
        :return: набор кортежей id_users_roles, user_login и role_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT ur.id_users_roles, r.role_name
                FROM users_roles as ur, roles as r, users as u
                WHERE ur.id_role = r.id_role AND ur.id_user = u.id_user AND ifnull(r.user, 0) = 0 AND ur.id_user = ?''',
                [id_user]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_user_role_for_check_exists(self, id_user, id_role):
        """ !Процедура проверки наличия роли у пользователя
        :param id_user:
        :param id_role:
        :return: id_users_roles / None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_users_roles 
                   FROM users_roles 
                   WHERE id_user = ? 
                     AND id_role = ?
                ''',
                [id_user, id_role]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'get_user_role_for_check_exists: ' + err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return [data]
        else:
            return None

    def save_new_user_role(self, id_user, id_role):
        """ Процедура сохранения новой связи пользователя и роли с проверкой базовой роли - user
        :param id_user:
        :param id_role:
        :return: No
        """
        # Создаем связь Пользователь - Роль (указанная на форме)
        self.insert_new_user_role(id_user, id_role)

    def insert_new_user_role(self, id_user, id_role):
        """ Процедура создания новой связи пользователя и роли
        :param id_user:
        :param id_role:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO users_roles(id_user, id_role)
                VALUES(?, ?)''', (id_user, id_role)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'insert_new_user_role:\n' + err.__str__())
        self.conn_sqlite3.commit()

    def update_user_role_by_user_id(self, id_user, id_role):
        """ Процедура обновления связи пользователя и роли по id пользователя
        :param id_user:
        :param id_role:
        :return: No
        """
        if len(self.get_count_user_role_by_user_id(id_user)) == 1:  # Если у пользователя одна роль
            try:
                self.c_sqlite3.execute(
                    '''UPDATE users_roles SET id_role=? WHERE id_user=?''', (id_role, id_user)
                )
                self.conn_sqlite3.commit()
            except sqlite3.Error as err:
                mb.showerror("ОШИБКА!", err.__str__())

    def update_user_role_by_id_users_roles(self, id_user, id_role, id_users_roles):
        """ Процедура обновления связи пользователя и роли по id_users_roles
        :param id_user:
        :param id_role:
        :param id_users_roles:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE users_roles SET id_user=?, id_role = ? WHERE id_users_roles=?''',
                (id_user, id_role, id_users_roles)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_user_roles(self, ids):
        """ Процедура удаления ролей пользователя по списку id
        :param ids: Список id
        :return:
        """
        try:
            for id_user_role in ids:
                self.c_sqlite3.execute(
                    '''DELETE FROM users_roles WHERE id_users_roles=?''', [id_user_role]
                )
                self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'delete_user_roles:\n' + err.__str__())

    def delete_user_role(self, id_user, id_role):
        """ Процедура удаления ролей пользователя по id_user и id_role
        :param id_user:
        :param id_role:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''DELETE FROM users_roles WHERE id_user=? AND id_role = ?''', [id_user, id_role]
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", 'delete_user_role:\n' + err.__str__())

