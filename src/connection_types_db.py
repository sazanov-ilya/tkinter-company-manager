import sqlite3
import tkinter.messagebox as mb

# Импортируем свои модули
import main_db_sqlite3 as db  # БД общая


class ConnectionTypesDB(db.DB):
    """ Класс работы с таблицей типов подключения """
    def __init__(self):
        super().__init__()  # Вызов __init__ базового класса

    ##################################
    # Процедуры для connection_types #
    ##################################
    def get_connection_type_by_id(self, id_connection_type):
        """ Процедура возврата данных типа подключения по переданному id
        :param id_connection_type: id типа подключения
        :return: возвращает только одну запись по id
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_connection_type, connection_type_name, connection_type_description
                FROM connection_types WHERE id_connection_type=?''', [id_connection_type]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
            # self.root.destroy()
        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_connection_type_name_by_name(self, connection_type_name):
        """ Процедура проверки наличия типа подключения по его имени
        :param connection_type_name: Название типа подключения
        :return: connection_type_name/None
        """
        connection_type_name = connection_type_name.lower()
        try:
            self.c_sqlite3.execute(
                '''SELECT connection_type_name FROM connection_types WHERE LOWER(connection_type_name) = ?''',
                [connection_type_name]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
        # self.root.destroy()
        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_connection_type_list_by_filter(self, connection_types_filter_dict):
        """ Процедура возврата результата списка типов подключения согласно переданных фильтров
        :param connection_types_filter_dict:
        :return: Набор кортежей
        """
        match connection_types_filter_dict:
            # name/description
            case {'name': name,
                  'description': description}:
                like_name = ('%' + name.lower() + '%')
                like_description = ('%' + description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_connection_type,
                                  connection_type_name,
                                  GET_DESCRIPTION(connection_type_description)
                           FROM connection_types 
                           WHERE MY_LOWER(connection_type_name) LIKE ?
                            AND MY_LOWER(connection_type_description) LIKE ?
                        ''', [like_name, like_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # name
            case {'name': name}:
                like_name = ('%' + name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_connection_type,
                                  connection_type_name,
                                  GET_DESCRIPTION(connection_type_description)
                           FROM connection_types 
                           WHERE MY_LOWER(connection_type_name) LIKE ?
                        ''', [like_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # description
            case {'description': description}:
                like_description = ('%' + description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_connection_type,
                                  connection_type_name,
                                  GET_DESCRIPTION(connection_type_description)
                           FROM connection_types 
                           WHERE MY_LOWER(connection_type_description) LIKE ?
                        ''', [like_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_connection_type,
                                  connection_type_name,
                                  GET_DESCRIPTION(connection_type_description)
                           FROM connection_types
                        '''
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
        data = []  # Запрос возвращает набор кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_connection_type_for_list(self):
        """ Процедура возвращает список типов подключений
        :return: набор кортежей id и connection_type_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_connection_type, connection_type_name FROM connection_types'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
            # self.root.destroy()

        data = []  # запрос возвращает набор кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def insert_new_connection_type(self, connection_type_name, connection_type_description):
        """ Процедура сохранения нового типа подключения
        :param connection_type_name:
        :param connection_type_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO connection_types(connection_type_name, connection_type_description) VALUES(?, ?)''',
                (connection_type_name, connection_type_description)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_connection_type_by_name(self, connection_type_name, connection_type_description):
        """ Процедура обновления данных типа подключения по его имени
        :param connection_type_name: Название типа подключения
        :param connection_type_description: Комментарий для типа подключения
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE connection_types SET connection_type_name=?, connection_type_description=? 
                WHERE LOWER(connection_type_name) = ?''',
                (connection_type_name.lower(), connection_type_description, connection_type_name.lower())
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_connection_type_by_id(self, id_connection_type, connection_type_name, connection_type_description):
        """ Процедура обновления данных первого выделенного в списке типа подключения
        :param connection_type_name: Название типа подключения
        :param connection_type_description: Комментарий для типа подключения
        :return No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE connection_types SET connection_type_name=?, connection_type_description=?
                WHERE id_connection_type=?''',
                (connection_type_name, connection_type_description, id_connection_type)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_connection_types(self, ids):
        """ Процедура удаления выбранных типов подключения
        :param ids: Список id типов подключения
        :return: No
        """
        try:
            for id in ids:
                self.c_sqlite3.execute(
                    '''DELETE FROM connection_types WHERE id_connection_type=?''', [id]
                )
                self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())