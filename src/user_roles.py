# Файл форм для модуля "Роли выбранного пользователя"
# Форма Список ролей выбранного пользователя
# Добавление, Удаление ролей пользователю
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb


# Импортируем свои модули
import users as users  # Формы пользователей
import users_db as users_db  # БД для форм пользователей


class UserRoles(tk.Frame):
    """ Класс формы списка ролей выбранного пользователя """
    def __init__(self, root, main, id_user):
        super().__init__(root)

        self.root = root  # frm_content_all
        self.main = main  # Main
        self.id_user = id_user

        self.roles_db = users_db.RolesDB()  # БД ролей
        self.role_list_not_user = self.roles_db.get_role_list_not_user(self.id_user)  # Кортеж (id, name) списка ролей
        self.users_db = users_db.UsersDB()  # БД пользователей
        self.users_roles = users_db.UsersRolesDB()  # БД роли-пользователей

        self.init_user_roles()
        self.show_user_name()  # Вывод данных пользователя на форму
        self.show_roles_by_id_user()  # Список ролей пользователя

    def init_user_roles(self):
        # self.title('Список логинов')

        # резиновая ячейка с таблицей
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # для отображения данных на форме
        self.pack(fill=tk.BOTH, expand=True)

        # # базовая рамка для модуля
        # frm_logins = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        # frm_logins.pack(fill=tk.BOTH, expand=True)

        # Рамка для верхнего toolbar
        frm_top_toolbar = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        frm_top_toolbar.grid(row=0, column=0, columnspan=2, sticky='nwse')

        # Кнопки
        # 1
        btn_open_filter = tk.Button(frm_top_toolbar, text='Фильтр', **self.main.options_btn_top_menu,
                                    command=self.open_filter_user_role)
        btn_open_filter.pack(side=tk.LEFT, **self.main.pack_btn_top_menu)
        # 2
        btn_open_new = tk.Button(frm_top_toolbar, text='Добавить', **self.main.options_btn_top_menu,
                                 command=self.open_new_user_role)
        btn_open_new.pack(side=tk.LEFT, **self.main.pack_btn_top_menu)
        # 3
        btn_open_update = tk.Button(frm_top_toolbar, text='Редактировать', **self.main.options_btn_top_menu,
                                    command=self.open_update_user_role)
        btn_open_update.pack(side=tk.LEFT, **self.main.pack_btn_top_menu)
        # 4
        btn_delete = tk.Button(frm_top_toolbar, text='Удалить', **self.main.options_btn_top_menu,
                               command=self.delete_user_roles)
        btn_delete.pack(side=tk.LEFT, **self.main.pack_btn_top_menu)

        # Рамка метки с именем пользователя
        frm_title_user = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        frm_title_user.grid(row=1, column=0, columnspan=2, sticky='nwse')
        self.lbl_company_name = tk.Label(frm_title_user, bg='#d7d8e0', text='Компания - > Тип подключения')
        self.lbl_company_name.pack(side=tk.LEFT, padx=5, pady=7)

        # Таблица через Treeview
        self.table = ttk.Treeview(self, columns=('id_users_roles', 'role_name'),
                                         height=10, show='headings')
        # Параметры столбцов
        self.table.column("id_users_roles", width=40, anchor=tk.CENTER)
        # self.table.column("user_login", anchor=tk.CENTER)
        self.table.column("role_name", anchor=tk.CENTER)
        # Названия столбцов
        self.table.heading('id_users_roles', text='ID')
        # self.table.heading('user_login', text='Логин пользователя')
        self.table.heading('role_name', text='Название роли')

        self.table.grid(row=2, column=0, sticky='nwse')
        # Вешаем контекстное меню на ЛКМ
        self.table.bind('<Button-3>', self.show_context_menu)

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self, command=self.table.yview)
        scroll.grid(row=2, column=1, sticky='nwse')
        self.table.configure(yscrollcommand=scroll.set)

        # Рамка для нижнего toolbar
        frm_bottom_toolbar = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        frm_bottom_toolbar.grid(row=3, column=0, columnspan=2, sticky='nwse')

        # Кнопки
        # 1
        self.btn_back_to_users = tk.Button(frm_bottom_toolbar, text='Назад на список пользователей',
                                           **self.main.options_btn_top_menu,
                                           command=self.open_users)
        self.btn_back_to_users.pack(side=tk.RIGHT, **self.main.pack_btn_top_menu)

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.table, tearoff=0)
        self.context_menu.add_command(
            command=self.copy_to_clipboard,
            label="Копировать")

    def copy_to_clipboard(self):
        """ Процедура копирования в буфер обмена """
        id_login = self.table.set(self.table.selection()[0], '#1')

        # data_company = self.connections_db.get_company_connection_type_by_id_connection(self.id_connection)
        # data_login = self.logins_db.get_login_by_id(id_login)
        #
        # # clipboard =   data_login[1] + '\n' + data_login[2] + '\n' + data_login[3]
        # clipboard = data_company[1] + '\n===\n' + data_company[2] + '\n===\n' + \
        #             data_login[1] + '\n---\n' + data_login[2] + '\n---\n' + data_login[3]
        # self.root.clipboard_clear()
        # self.root.clipboard_append(clipboard)

    def show_context_menu(self, event):
        """ Процедура вывода контекстного меню
        :param event:
        :return:
        """
        if self.table.focus() != '':
            self.table.identify_row(event.y)
            self.context_menu.post(event.x_root, event.y_root)

    def show_user_name(self):
        """ Процедура вывода на форму логина и имени выбранного пользователя """
        data = self.users_db.get_user_by_id(self.id_user)
        label = (data[1]) + '  ( ' + (data[3]) + ' )'
        self.lbl_company_name.config(text=label)

    def show_roles_by_id_user(self):
        """ Процедура перезаполнения списка логинов """
        [self.table.delete(i) for i in self.table.get_children()]  # Очистка таблицы
        data = self.users_roles.get_user_role_list_by_user(self.id_user)
        [self.table.insert('', 'end', values=row) for row in data]

    def open_users(self):
        """ Возврат на окно со списком пользователей """
        self.main.clear_frm_content_all()  # Чистим форму
        self.destroy()  # Убиваем текушую форму
        users.Users(self.main.frm_content_all, self.main)  # Вывод пользователей

    def open_filter_user_role(self):
        """ Открываем окно фильтров """
        # if len(self.role_list_not_user) > 0:  # Если есть роли неназначенные пользователю
        #     NewUserRole(self.main, self, self.id_user)
        # else:
        #     mb.showwarning('Предупреждение', 'У пользователя уже есть все роли.')

    def open_new_user_role(self):
        """ Открываем окно для ввода нового логина по выбранному подключению
        Передаем app и id первого выбранного в списке подключения """
        if len(self.role_list_not_user) > 0:  # Если есть роли неназначенные пользователю
            NewUserRole(self.main, self, self.id_user)
        else:
            mb.showwarning('Предупреждение', 'У пользователя уже есть все роли.')

    def open_update_user_role(self):
        """ Открываем окно для обновления выбранной роли """
        if len(self.role_list_not_user) > 0:  # Если есть роли, которые не назначены пользователю
            if self.table.focus() != '':  # Выбран элемент в таблице?
                UpdateUserRole(self.main,
                               self,
                               self.id_user,
                               self.table.set(self.table.selection()[0], '#1'))
            else:
                mb.showwarning('Предупреждение', 'Выберите роль')
        else:
            mb.showwarning('Предупреждение', 'У пользователя уже есть все роли.')

    def delete_user_roles(self):
        """ Процедура удаления выбранных ролей пользователя """
        if self.table.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # Если Да = True
                ids = []  # Кортеж id выделенных элементов
                for selection_item in self.table.selection():
                    ids.append(self.table.set(selection_item, '#1'),)
                self.users_roles.delete_user_roles(ids)
                self.show_roles_by_id_user()  # Перезагружаем список
                self.role_list_not_user = self.roles_db.get_role_list_not_user(self.id_user)  # Перезаполняем словарь
                self.users_db.check_count_admins()  # Проверяем число админов (для блока базового)
        else:
            mb.showwarning('Предупреждение', 'Выберите роль (роли)')


class UserRole(tk.Toplevel):
    """ Базовый класс всплывающей фломы для отображения роли пользователя """
    def __init__(self, root, parent, id_user):
        """
        :param root: класс Main
        :param parent:
        :param id_user: id пользователя
        :param id_users_roles: id связи Пользователь-Роль
        """
        super().__init__()
        self["bg"] = '#d7d8e0'  # Цвет фона формы

        self.title("Роли пользователя")
        # тема
        self.style = ttk.Style()
        self.style.theme_use("default")
        # self.geometry('260x90+400+300')
        self.geometry('300x90+400+300')
        self.resizable(False, False)

        # # Классы-переменные - для связки значений виджетов
        # self.is_deleted = tk.BooleanVar()

        self.root = root
        self.parent = parent
        self.id_user = id_user

        self.init_user_role()  # Строим форму

    def init_user_role(self):
        # Добавляем функции модального, прехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        lbl_padding = {'sticky': 'w', 'padx': 10, 'pady': 10}
        ent_padding = {'sticky': 'we', 'padx': 10}

        # Резиновая ячейка для списка ролей
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        # 2 Роль
        lbl_role = ttk.Label(self, text="Роль", width=10)
        lbl_role.grid(row=1, column=0, **lbl_padding)
        self.cmb_role = ttk.Combobox(self)
        self.cmb_role.grid(row=1, column=1, columnspan=4, **ent_padding)

        # 3 Кнопки
        self.btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        self.btn_cancel.grid(row=2, column=4, sticky=tk.W + tk.E, pady=10, padx=10)

    def check_empty(self):
        """ Процедура проверки на пустые поля формы
        :return: True/False
        """
        if (self.cmb_role.current()) == -1:
            mb.showwarning('Предупреждение', 'Выберите роль')
            return False
        return True

    def check_exists(self, id_user, id_role):
        """ Процедура проверки дублей логина по введенным данным
        :return: True/False
        """
        data = self.parent.users_roles.get_user_role_for_check_exists(id_user, id_role)
        if data:
            mb.showwarning('Предупреждение', 'У пользователя уже есть данная роль')
            return False
        return True

    def show_role_list_not_user(self):
        """ Процедура заполнения списка ролей (которых еще нет у пользователя) """
        self.cmb_role['values'] = [role[1] for role in self.parent.role_list_not_user]
        self.cmb_role.current(0)  # Значение по умолчанию


class NewUserRole(UserRole):
    """ Класс фомы для добавления новой роли пользователю """
    def __init__(self, root, parent, id_user):
        """
        :param root:
        :param parent:
        :param id_user:
        """
        super().__init__(root, parent, id_user)
        # self.geometry("500x300+300+200")

        self.root = root  # Main
        self.parent = parent  # Users
        self.id_user = id_user

        self.init_new_user_role()
        self.show_role_list_not_user()  # Заполняем список ролей

    def init_new_user_role(self):
        self.title("Добавить роль")

        # 3 - Кнопки
        btn_save = ttk.Button(self, text='Сохранить', command=self.save_new_user_role
                              )
        btn_save.grid(row=2, column=3, sticky=tk.W + tk.E, pady=10, padx=10)

    def save_new_user_role(self):
        """ Процедура сохранения новой связи пользователь-роль """
        if self.check_empty():  # Проверка на пустые поля
            self.parent.users_roles.insert_new_user_role(self.id_user,
                                                         self.parent.role_list_not_user[self.cmb_role.current()][0])
            self.parent.show_roles_by_id_user()  # Список ролей пользователя
            # Перезаполняем словарь
            self.parent.role_list_not_user = self.parent.roles_db.get_role_list_not_user(self.id_user)
            self.parent.users_db.check_count_admins()  # Проверяем число админов (для блокировки базового админа)
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateUserRole(UserRole):
    """ Класс фомы для добавления новой роли пользователю """
    def __init__(self, root, parent, id_user, id_user_role):
        """
        :param root:
        :param parent:
        :param id_user:
        """
        super().__init__(root, parent, id_user)
        # self.geometry("500x300+300+200")

        self.root = root  # Main
        self.parent = parent  # Users
        self.id_user = id_user
        self.id_user_role = id_user_role

        # self.users_roles = users_db.UsersRolesDB()  # БД роли пользователей

        self.init_update_user_role()
        self.show_role_list_not_user()  # Заполняем список ролей

    def init_update_user_role(self):
        self.title("Обновить роль")

        # 3 Кнопки
        btn_save = ttk.Button(self, text='Обновить', command=self.update_new_user_role)
        btn_save.grid(row=2, column=3, sticky=tk.W + tk.E, pady=10, padx=10)

    def update_new_user_role(self):
        """ Процедура сохранения новой связи пользователь-роль """
        if self.check_empty() and self.check_exists(self.id_user,
                                                    self.parent.role_list_not_user[self.cmb_role.current()][0]):

            self.parent.users_roles.update_user_role_by_id_users_roles(self.id_user,
                                                                       self.parent.role_list_not_user
                                                                       [self.cmb_role.current()][0],
                                                                       self.id_user_role)
            self.parent.show_roles_by_id_user()  # Список ролей пользователя
            # Перезаполняем словарь
            self.parent.role_list_not_user = self.parent.roles_db.get_role_list_not_user(self.id_user)
            self.parent.users_db.check_count_admins()  # Проверяем число админов (для блокировки базового админа)
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"
