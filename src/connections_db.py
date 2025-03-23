import sqlite3
import tkinter.messagebox as mb

# Свои модули
import main_db_sqlite3 as db  # БД - общий


class ConnectionsDB(db.DB):
    """ Класс работы с таблицей типов подключения """
    def __init__(self):
        super().__init__()  # вызов __init__ базового класса

    #############################
    # Процедуры для connections #
    #############################
    def get_connection_by_id(self, id_connection):
        """ Процедура возврата данных подключения по переданному id_connection
        :param id_connection: id подключения
        :return: возвращает только одну запись по id
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_connection, id_company, id_connection_type, connection_ip, connection_description
                FROM connections WHERE id_connection=?''', [id_connection]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_company_connection_type_by_id_connection(self, id_connection):
        """ Процедура возвращает названия компании и типа подключения по id_connection
        :param id_connection:
        :return: названия компании и тип подключения
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT connections.id_connection, companies.company_name, connection_types.connection_type_name
                FROM connections, companies, connection_types
                WHERE  connections.id_company=companies.id_company
                AND connections.id_connection_type = connection_types.id_connection_type
                AND connections.id_connection = ?''', [id_connection]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_connection_for_update_by_id(self, id_connection):
        """ Процедура возвращает данные подключения для формы обновления по id_connection
        :param id_connection:
        :return: названия компании и тип подключения
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT connections.id_connection, companies.company_name, connection_types.connection_type_name,
                connections.connection_ip, connections.connection_description
                FROM connections, companies, connection_types
                WHERE  connections.id_company=companies.id_company
                AND connections.id_connection_type = connection_types.id_connection_type
                AND connections.id_connection = ?''', [id_connection]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
            # self.root.destroy()
        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_connections_by_filter(self, connections_filter_dict):
        """ Процедура возврата списка подключений согласно фильтра
        :param connections_filter_dict:
        :return: Набор кортежей
        """
        match connections_filter_dict:
            # id_company/id_connection_type/connection_ip
            case {'id_company': id_company, 'id_connection_type': id_connection_type,
                  'connection_ip': connection_ip, **remainder} if not remainder:
                like_connection_ip = ('%' + connection_ip.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_company = ?
                             AND connections.id_connection_type = ?
                             AND MY_LOWER(connections.connection_ip) LIKE ?
                        ''', [id_company, id_connection_type, like_connection_ip]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # id_company/id_connection_type
            case {'id_company': id_company, 'id_connection_type': id_connection_type, **remainder} if not remainder:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_company = ?
                             AND connections.id_connection_type = ?
                        ''', [id_company, id_connection_type]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # id_company/connection_ip
            case {'id_company': id_company, 'connection_ip': connection_ip, **remainder} if not remainder:
                like_connection_ip = ('%' + connection_ip.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_company = ? 
                             AND MY_LOWER(connections.connection_ip) LIKE ?
                        ''', [id_company, like_connection_ip]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # id_connection_type/connection_ip
            case {'id_connection_type': id_connection_type, 'connection_ip': connection_ip,
                  **remainder} if not remainder:
                like_connection_ip = ('%' + connection_ip.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_connection_type = ?
                             AND MY_LOWER(connections.connection_ip) LIKE ?
                        ''', [id_connection_type, like_connection_ip]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # id_company
            case {'id_company': id_company, **remainder} if not remainder:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_company = ?
                        ''', [id_company]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # id_connection_type
            case {'id_connection_type': id_connection_type, **remainder} if not remainder:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND connections.id_connection_type = ?
                        ''', [id_connection_type]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # connection_ip
            case {'connection_ip': connection_ip, **remainder} if not remainder:
                like_connection_ip = ('%' + connection_ip.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND MY_LOWER(connections.connection_ip) LIKE ?
                        ''', [like_connection_ip]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # connection_description
            case {'connection_description': connection_description, **remainder} if not remainder:
                like_connection_description = ('%' + connection_description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type
                             AND MY_LOWER(connections.connection_description) LIKE ?
                        ''', [like_connection_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT connections.id_connection,
                                  companies.company_name,
                                  connection_types.connection_type_name,
                                  connections.connection_ip,
                                  GET_DESCRIPTION(connections.connection_description)
                           FROM connections,
                                companies,
                                connection_types
                           WHERE connections.id_company = companies.id_company
                             AND connections.id_connection_type = connection_types.id_connection_type'''
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", 'get_connections_by_filter:\n' + err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def get_connection_ip_for_check_exists(self, id_company, id_connection_type, connection_ip):
        """ Процедура проверки наличия подключения по компании, типу подключения и ip/домену (проверка на дубль)
        :param id_company:
        :param id_connection_type:
        :param connection_ip:
        :return: connection_ip/None
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT connection_ip 
                   FROM connections 
                   WHERE id_company = ? 
                     AND id_connection_type = ?
                     AND connection_ip = ?
                ''', [id_company, id_connection_type, connection_ip]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def insert_new_connection(self, id_company, id_connection_type, connection_ip, connection_description):
        """ Процедура сохранения нового подключения
        :param id_company:
        :param id_connection_type:
        :param connection_ip:
        :param connection_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO connections(id_company, id_connection_type, connection_ip, connection_description) 
                VALUES(?, ?, ?, ?)''',
                (id_company, id_connection_type, connection_ip, connection_description)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_connection_by_id(self, id_connection, connection_ip, connection_description):
        """ Процедура обновления подключения по id_connection
        :param id_connection:
        :param connection_ip:
        :param connection_description:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE connections SET connection_ip=?, connection_description=?
                WHERE id_connection=?''',
                (connection_ip, connection_description, id_connection)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_connections(self, ids):
        """ Процедура удаления подключений
        :param ids: Список id подключений
        :return: No
        """
        try:
            for id in ids:
                self.c_sqlite3.execute(
                    '''DELETE FROM connections WHERE id_connection=?''', [id]
                )
                self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
