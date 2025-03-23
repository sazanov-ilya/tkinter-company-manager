import sqlite3
import tkinter.messagebox as mb

# Свои модули
import main_db_sqlite3 as db  # БД - общий


class CompaniesDB(db.DB):
    """ Класс работы с таблицей компаний """
    def __init__(self):
        super().__init__()  # Вызов __init__ базового класса

    ###########################
    # Процедуры для companies #
    ###########################
    def get_company_by_id(self, id_company):
        """ Процедура возврата данных компании по переданному id
        :param id_company:
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_company, company_name, company_description FROM companies WHERE id_company=?''',
                [id_company]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()  # Возвращает только одну запись
        return data

    def get_company_name_by_name(self, company_name):
        """ Процедура проверки наличия компании по ее имени
        :param company_name: Название компании
        :return: company_name/None
        """
        company_name = company_name.lower()
        try:
            self.c_sqlite3.execute(
                '''SELECT company_name FROM companies WHERE LOWER(company_name) = ?''', [company_name]
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = self.c_sqlite3.fetchone()
        if data is not None:
            return data[0]
        else:
            return None

    def get_company_list_by_filter(self, filter_dict):
        """ Процедура возврата списка компаний согласно фильтрам
        :param filter_dict: словарь фильтров
        :return: Набор кортежей
        """
        match filter_dict:
            # company_name/company_description
            case {'name': name, 'company_description': description}:
                like_name = ('%' + name.lower() + '%')
                like_description = ('%' + description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_company,
                                  company_name,
                                  GET_DESCRIPTION(company_description)
                           FROM companies 
                           WHERE MY_LOWER(company_name) LIKE ? 
                             AND MY_LOWER(company_description) LIKE ?
                        ''', [like_name, like_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # company_name
            case {'name': name}:
                like_name = ('%' + name.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_company,
                                  company_name,
                                  GET_DESCRIPTION(company_description)
                           FROM companies 
                           WHERE MY_LOWER(company_name) LIKE ?
                        ''', [like_name]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # company_description
            case {'description': description}:
                like_description = ('%' + description.lower() + '%')
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_company,
                                  company_name,
                                  GET_DESCRIPTION(company_description)
                           FROM companies 
                           WHERE MY_LOWER(company_description) LIKE ?
                        ''', [like_description]
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
            # Прочее
            case _:
                try:
                    self.c_sqlite3.execute(
                        '''SELECT id_company,
                                  company_name,
                                  GET_DESCRIPTION(company_description)
                           FROM companies
                        '''
                    )
                except sqlite3.Error as err:
                    mb.showerror("ОШИБКА!", err.__str__())
        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]

        return data

    def get_company_for_list(self):
        """ Процедура возвращает список компаний для выпадающего списка
        :return: набор кортежей id и company_name
        """
        try:
            self.c_sqlite3.execute(
                '''SELECT id_company, company_name FROM companies'''
            )
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

        data = []  # Запрос возвращает список кортежей
        [data.append(row) for row in self.c_sqlite3.fetchall()]
        return data

    def insert_new_company(self, company_name, company_description):
        """ Процедура сохранения данных новой компании
        :param company_name: Название компании
        :param company_description: Описание для компании
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''INSERT INTO companies(company_name, company_description) VALUES(?, ?)''',
                (company_name, company_description)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_company_by_name(self, company_name, company_description):
        """ Процедура обновления данных компании по ее имени
        :param company_name: Название компании
        :param company_description: Комментарий для компании
        :return: No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE companies SET company_name=?, company_description=? WHERE LOWER(company_name) = ?''',
                (company_name.lower(), company_description, company_name.lower())
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def update_company_by_id(self, id_company, company_name, company_description):
        """ Процедура обновления данных компании по ее id
        :param id_company: Id компании
        :param company_name: Название компании
        :param company_description: Комментарий для компании
        :return No
        """
        try:
            self.c_sqlite3.execute(
                '''UPDATE companies SET company_name=?, company_description=? WHERE id_company=?''',
                (company_name, company_description, id_company)
            )
            self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())

    def delete_companies(self, ids):
        """ Процедура удаления выбранных в списке компаний
        :param ids: Список id компаний
        :return: No
        """
        try:
            for id in ids:
                self.c_sqlite3.execute(
                    '''DELETE FROM companies WHERE id_company=?''', [id]
                    )
                self.conn_sqlite3.commit()
        except sqlite3.Error as err:
            mb.showerror("ОШИБКА!", err.__str__())
