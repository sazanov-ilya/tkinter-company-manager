from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import Description, PermissionCheckButton, MyButton, TopMenuButtons
import _service as srv
import _styles as style
import connections as connections
import logins_db as logins_db            # БД для форм логинов
import connections_db as connections_db  # БД для форм подключения
import users_db as users_db


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
# logins_filter_dict = {'name': '', 'description': ''}
logins_filter_dict = {}


class Logins(tk.Frame):
    """ Класс формы списка логинов """
    def __init__(self, root, main, id_connection: int, is_admin: bool = None) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                       # frm_content_all
        self.main = main                       # Main
        self.is_admin: bool = is_admin  # Признак "администратор"
        self.id_connection = id_connection     # Id подключения
        self.logins_db = logins_db.LoginsDB()  # БД логинов
        self.connections_db = connections_db.ConnectionsDB()  # БД подключений
        self.users_db = users_db.UsersDB()                    # БД пользователей
        self.logins_list = []                                 # Список кортежей логинов

        # ----
        # Окно
        # !ВАЖНО для отображения данных на форме
        self.pack(fill=tk.BOTH, expand=True)

        # Свойства
        # self.title('Список логинов')

        # (визуальный макет формы)
        # Резиновая ячейка с таблицей
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # --------------------------
        # Рамка для верхнего toolbar
        self.frm_top_toolbar = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        self.frm_top_toolbar.grid(row=0, column=0, sticky='we')

        # # Резиновая строка,
        # # каждая ячейка является резиновой (настраивается в TopMenuButtons)
        # self.frm_top_toolbar.rowconfigure(0, weight=1)

        # Словарь параметров для кнопок верхнего toolbar
        self.top_menu_button_options = [
            {
                'is_admin': False,
                'callbacks': [self.open_filter],
                'options': {'text': 'Фильтр', 'width': 14},
            },
            {
                'is_admin': False,
                'callbacks': [self.open_new],
                'options': {'text': 'Добавить', 'width': 14},
            },
            {
                'is_admin': False,
                'callbacks': [self.open_update],
                'options': {'text': 'Редактировать', 'width': 14},
            },
            {
                'is_admin': False,
                'callbacks': [self.open_delete],
                'options': {'text': 'Удалить', 'width': 14},
            },
            {
                'is_admin': True,
                'callbacks': [self.open_permission],
                'options': {'text': 'Управление правами', 'width': 20},
            },
        ]
        # Создание верхнего меню
        self.top_menu_buttons = TopMenuButtons(
            self.frm_top_toolbar,
            is_admin=self.is_admin,
            options=self.top_menu_button_options
        )

        # ------------------
        # Рамка для treeview
        self.frm_treeview = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        self.frm_treeview.grid(row=1, column=0, sticky='nwse')

        # Резиновая ячейка с таблицей
        self.frm_treeview.rowconfigure(0, weight=1)
        self.frm_treeview.columnconfigure(0, weight=1)

        # Таблица Treeview
        self.treeview_options = {'height': 10, 'show': 'headings'}  # , 'selectmode': 'browse'}
        self.columns = {
            'id_login': {
                'displaycolumns': False,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'login_name': {
                'displaycolumns': True,
                'column': {'width': 50, 'anchor': tk.W},
                'heading': {'text': 'Логин'},
            },
            'login_password': {
                'displaycolumns': True,
                'column': {'width': 50, 'anchor': tk.W},
                'heading': {'text': 'Пароль'},
            },
            'login_description': {
                'displaycolumns': True,
                'column': {'width': 150, 'anchor': tk.W},
                'heading': {'text': 'Описание'},
            },
        }
        # Настраиваем таблицу по словарю
        self.table_list = ttk.Treeview(self.frm_treeview, columns=([key for key in self.columns]),
                                       displaycolumns=(
                                           [key for key in self.columns if self.columns[key]['displaycolumns']]),
                                       **self.treeview_options)
        for key, value in self.columns.items():
            self.table_list.column(key, **value['column'])
            self.table_list.heading(key, **value['heading'])

        self.table_list.grid(row=0, column=0, sticky='nswe')

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self.frm_treeview, command=self.table_list.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.table_list.configure(yscrollcommand=scroll.set)

        # ---------------------
        # Рамка нижнего toolbar
        self.frm_bottom_toolbar = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        self.frm_bottom_toolbar.grid(row=2, column=0, sticky='we')

        # Резиновая ячейка с меткой, чтобы прижать кнопку к правому краю
        self.frm_bottom_toolbar.rowconfigure(0, weight=1)
        self.frm_bottom_toolbar.columnconfigure(0, weight=1)

        # Метка Компания - > Тип подключения
        self.lbl_company_name = ttk.Label(
            self.frm_bottom_toolbar, text='Компания - > Тип подключения', style=style.LABEL_CAPTION
        )
        self.lbl_company_name.grid(row=0, column=0, pady=10, padx=7, sticky='nswe')

        # Кнопка нижнего toolbar
        self.btn_back = MyButton(
            self.frm_bottom_toolbar,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.open_connections],
            text='Назад на список доступов', width=25,
        )
        self.btn_back.grid(row=0, column=1, pady=10, padx=7, sticky='nswe')

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.table_list, tearoff=0)
        self.context_menu.add_command(
            label='Копировать логин', command=self.copy_login)
        self.context_menu.add_command(
            label='Копировать пароль', command=self.copy_password)
        self.context_menu.add_command(
            label='Копировать описание', command=self.copy_description)
        # self.context_menu.add_command(
        #     label='Копировать все', command=self.copy_all)

        # -------
        # События
        # Привязываем события клавиш на таблицу
        self.table_list.bind('<Button-2>', self.select_row)  # СКМ, выделить строку
        self.table_list.bind('<Button-3>', self.show_context_menu)  # ЛКМ, контекстное меню
        self.table_list.bind('<Double-Button-1>', self.double_click)  # СКМ, выделить строку

        # Вызов процедур
        self.show_logins_by_id_connection()  # Отображаем таблицу
        self.show_company_name()             # Отображаем компанию и тип подключения

    def select_row(self, event=None):
        """Выделение строки в таблице."""
        # Получаем идентификатор строки под курсором
        iid = self.table_list.identify_row(event.y)
        if iid:
            # Выделяем строку под курсором по ее идентификатору
            self.table_list.selection_set(iid)
            return iid
        else:
            # Указатель мыши не находится над элементом
            # Возникает, когда элементы не заполняют рамку
            # Действие не требуется
            pass

    def double_click(self, event=None):
        """
        Двойной клик ЛКМ.
        :param event:
        :return: Нет
        """
        if self.select_row(event):  # Если строка была выделена
            self.open_update()

    def show_context_menu(self, event=None):
        """
        Отображение контекстного меню.
        :param event:
        :return: Нет
        """
        if self.select_row(event):  # Если строка была выделена
            self.context_menu.post(event.x_root, event.y_root)

    def copy_login(self):
        """Копирование наименования в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1'))

    def copy_password(self):
        """Копирование пароля в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#2'))

    def copy_description(self):
        """Копирование описания в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#3'))

    def copy_all(self):
        """Копирование выделенной строки в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#2') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#3'))

    def color_btn_filter(self):
        """Смены цвета кнопки Фильтр."""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if logins_filter_dict:  # Если есть фильтры
            self.top_menu_buttons[0].configure(style=style.BUTTON_FILTER)
        else:
            self.top_menu_buttons[0].configure(style=style.BUTTON_CONTROL)

    @staticmethod
    def get_filter():
        """Сохранения и применения фильтра."""
        return logins_filter_dict

    def set_filter(self, filter_dict):
        """
        Сохранения и применения фильтра.
        :param filter_dict:
        :return: Нет
        """
        logins_filter_dict.clear()              # Чистим словарь
        logins_filter_dict.update(filter_dict)  # Обновляем словарь
        self.show_logins_by_id_connection()     # Обновляем таблицу

    def show_company_name(self):
        """Вывод на форму названия компании и типа подключения."""
        data = self.connections_db.get_company_connection_type_by_id_connection(self.id_connection)
        label = (data[1]) + '  ->  ' + (data[2])
        self.lbl_company_name.config(text=label)

    def show_logins_by_id_connection(self):
        """Заполнение таблицы логинов согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.table_list.delete(i) for i in self.table_list.get_children()]  # Очистка таблицы
        if self.main.is_admin:  # Если администратор
            self.logins_list = self.logins_db.get_logins_list_by_id_connection_for_admin(self.id_connection,
                                                                                         self.get_filter())
        else:
            self.logins_list = self.logins_db.get_logins_list_by_id_connection_for_user(self.id_connection,
                                                                                        self.main.id_user,
                                                                                        self.get_filter())
        srv.sorted_table(self.logins_list)  # Сортировка
        [self.table_list.insert('', 'end', values=row) for row in self.logins_list]

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров для списка подключений."""
        FilterLogin(self.main, self, self.id_connection)

    def open_new(self, event: Any = None) -> None:
        """
        Отображение окна для ввода нового логина по выбранному подключению.
        Передаем app и id первого выбранного в списке подключения.
        """
        NewLogin(self.main, self, self.id_connection)
        self.show_logins_by_id_connection()  # Обновляем таблицу-список

    def open_update(self, event: Any = None) -> None:
        """Отображение окна для редактирования выбранного логина."""
        if self.table_list.focus() != '':
            # Получаем первую выделенную строку
            item = self.table_list.item(self.table_list.focus())
            login_id = item["values"][0]
            UpdateLogin(self.main, self, self.id_connection, login_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите логин')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных логинов."""
        if self.table_list.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # если Да = True
                ids = []  # Список id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.table_list.selection():
                    item = self.table_list.item(selected_item)
                    ids.append(item["values"][0])
                self.logins_db.delete_logins(ids)
                self.show_logins_by_id_connection()  # Обновляем таблицу-список
        else:
            mb.showwarning('Предупреждение', 'Выберите логин (логины)')

    def open_permission(self, event: Any = None) -> None:
        """Отображаем окно назначения прав для выбранного логина."""
        if self.table_list.focus() != '':
            # Получаем первую выделенную строку
            item = self.table_list.item(self.table_list.focus())
            login_id = item["values"][0]
            Permission(self, login_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите логин')

    def open_connections(self, event: Any = None) -> None:
        """Возврат на окно со списком подключений."""
        self.main.clear_frm_content_all()  # Чистим форму
        self.destroy()                     # Убиваем текущую форму
        connections.Connections(self.main.frm_content_all, self.main, self.is_admin)  # Вывод таблицы


class Login(tk.Toplevel):
    """Базовый класс всплывающего окна логина."""
    def __init__(self, main, parent, id_connection):
        super().__init__()
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins
        self.id_connection = id_connection
        self.logins_db = logins_db.LoginsDB()  # БД логинов

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title("Логин")
        self.geometry('415x250+400+300')
        self.resizable(False, False)

        # Парамеры для единой стилизации меток для текстовых полей
        self.options_lbl = {'width': 10}
        self.grid_lbl = {'sticky': 'nw', 'padx': 10, 'pady': 10}
        # Парамеры для единой стилизации однострочных текстовых полей
        self.grid_ent = {'sticky': 'we', 'padx': 10}
        # Парамеры для единой стилизации многострочного текстового поля
        self.grid_txt = {'sticky': 'nwse', 'pady': 10, 'padx': 10}
        # Парамеры для единой стилизации кнопок управления
        self.grid_btn_control = {'sticky': 'we', 'pady': 10, 'padx': 10}

        # Главная рамка, для наследования стилей
        self.frm_main = ttk.Frame(self)
        self.frm_main.pack(fill=tk.BOTH, expand=True)

        # Резиновая ячейка для описания
        self.frm_main.columnconfigure(1, weight=1)
        self.frm_main.rowconfigure(2, weight=1)

        # 1 Логин
        lbl_name = ttk.Label(
            self.frm_main, text="Логин", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_name.grid(row=0, column=0, **self.grid_lbl)
        self.ent_login_name = ttk.Entry(self.frm_main)
        self.ent_login_name.grid(row=0, column=1, columnspan=4, **self.grid_ent)
        self.ent_login_name.focus()
        self.ent_login_name.bind("<Control-KeyPress>", srv.keys)

        # 2 Пароль
        self.lbl_password = ttk.Label(
            self.frm_main, text="Пароль", style=style.LABEL_CAPTION, **self.options_lbl
        )
        self.lbl_password.grid(row=1, column=0, **self.grid_lbl)
        self.ent_login_password = ttk.Entry(self.frm_main)
        self.ent_login_password.grid(row=1, column=1, columnspan=4, **self.grid_ent)
        self.ent_login_password.bind("<Control-KeyPress>", srv.keys)

        # 3 Описание
        lbl_description = ttk.Label(
            self.frm_main, text="Описание", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_description.grid(row=2, column=0, **self.grid_lbl)
        self.txt_description = Description(self.frm_main)
        self.txt_description.grid(row=2, column=1, columnspan=4, **self.grid_txt)

        # 4 Создатель
        lbl_creator = ttk.Label(
            self.frm_main, text="Создана", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_creator.grid(row=3, column=0, **self.grid_lbl)
        self.ent_creator = ttk.Entry(self.frm_main)
        self.ent_creator.grid(row=3, column=1, columnspan=4, **self.grid_ent)
        self.ent_creator.bind("<Control-KeyPress>", srv.keys)

        # 5 кнопки
        # self.btn_cancel = ttk.Button(self.frm_main, text='Отмена', command=self.click_btn_cancel)
        self.btn_cancel = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_cancel],
            text='Отмена', width=12,
        )
        self.btn_cancel.grid(row=4, column=4, **self.grid_btn_control)

        # -------
        # События
        # Виртуальное событие "Сохранить и закрыть окно"
        # Нужно для вызова из текстового поля для перехвата события KeyPress-Return
        self.event_generate('<<GlobalExit>>')  # doesn't trigger child binding
        self.bind('<<GlobalExit>>', self.click_btn_ok)

        # Привязываем события клавиш на окно
        self.bind('<Return>', self.click_btn_ok)  # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

    def click_btn_ok(self, event=None):
        """Клик по кнопке Ok (Применить/Обновить и т.п.)."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        # Заглушка, для создания события, реальная процедура в наследующем классе
        pass

    def click_btn_cancel(self, event=None):
        """Клик по кнопке Отмена, закрываем окно."""
        self.parent.show_logins_by_id_connection()  # Обновляем таблицу-список
        self.destroy()

    def check_empty(self):
        """
        Проверка на пустые поля формы.
        :return: True/False
        """
        if len(self.ent_login_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите логин')
            return False
        elif len(self.ent_login_password.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите пароль')
            return False
        return True

    def check_exists(self):
        """
        Проверка дублей логина по введенным данным.
        :return: True/False
        """
        id_connection = self.id_connection
        login_name = self.ent_login_name.get()
        data = self.logins_db.get_login_name_for_check_exists(id_connection, login_name)

        if data:
            mb.showwarning('Предупреждение', 'Дубль логина <' + data + '> для выбранного подключения')
            return False
        return True


class FilterLogin(Login):
    """Класс формы добавления нового логина по id_connection."""
    def __init__(self, main, parent, id_connection):
        super().__init__(main, parent, id_connection)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins
        self.id_connection = id_connection

        # ----
        # Окно
        self.title("Добавить новый логин")

        # Блокируем (normal, readonly и disabled)
        self.ent_creator.insert(0, self.main.user_login)
        self.ent_creator.configure(state="disabled")
        #
        self.lbl_password.configure(state="disabled")
        self.ent_login_password.configure(state="disabled")

        # 5 Добавляем кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Применить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Применить', width=12,
        )
        self.btn_ok.grid(row=4, column=2, **self.grid_btn_control)
        #
        # btn_clear_filter = ttk.Button(self.frm_main, text='Сбросить', command=self.click_btn_clear_filter)
        self.btn_clear_filter = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_clear_filter],
            text='Сбросить', width=12,
        )
        self.btn_clear_filter.grid(row=4, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_filter()

    def get_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        tmp_logins_filter_dict = {}
        tmp_logins_filter_dict.update(self.parent.get_filter())  # Получаем текущий фильтр

        if tmp_logins_filter_dict:
            if tmp_logins_filter_dict.get('login_name', ''):
                self.ent_login_name.insert(0, tmp_logins_filter_dict.get('login_name', ''))
            if tmp_logins_filter_dict.get('login_description', ''):
                self.txt_description.insert(tmp_logins_filter_dict.get('login_description', ''))

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        tmp_logins_filter_dict = {}
        if len(self.ent_login_name.get()) > 0:
            tmp_logins_filter_dict['login_name'] = self.ent_login_name.get()
        if len(srv.get_text_in_one_line(self.txt_description.get())) > 0:
            tmp_logins_filter_dict['login_description'] = \
                srv.get_text_in_one_line(self.txt_description.get())

        self.parent.set_filter(tmp_logins_filter_dict)  # Сохраняем новый фильтр
        self.btn_cancel.invoke()  # Имитация клика по кнопке "Закрыть"

    def click_btn_clear_filter(self, event=None):
        """Клик по кнопке Сбросить, очистка фильтров."""
        self.parent.set_filter({})
        self.btn_cancel.invoke()  # Имитация клика по кнопке "Закрыть"


class NewLogin(Login):
    """Класс формы добавления нового логина по id_connection."""
    def __init__(self, main, parent, id_connection):
        super().__init__(main, parent, id_connection)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins
        self.id_connection = id_connection

        # ----
        # Окно
        self.title("Добавить новый логин")

        # Владелец, вывод значения и блокировка поля
        self.ent_creator.insert(0, self.main.user_login)
        self.ent_creator.configure(state="disabled")  # normal, readonly и disabled

        # 5 Добавляем кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Сохранить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=4, column=3, **self.grid_btn_control)

    def click_btn_ok(self, event=None):
        """
        Сохранение нового логина.
        :return: Нет
        """
        if self.check_empty() and self.check_exists():  # Проверка на пустые поля и дубль
            self.logins_db.save_new_login(self.id_connection,
                                          self.ent_login_name.get(),
                                          self.ent_login_password.get(),
                                          self.txt_description.get(),
                                          self.main.id_user,
                                          self.main.id_role)
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateLogin(Login):
    """Класс формы обновления логина по id_connection и id_login."""
    def __init__(self, main, parent, id_connection, id_login):
        super().__init__(main, parent, id_connection)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins
        self.id_connection = id_connection
        self.id_login = id_login

        # ----
        # Окно
        self.title("Редактировать логин")

        # 5 Добавляем кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Обновить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=4, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_login_for_update()

    def get_login_for_update(self):
        """Получение и вывода на форму данных логина для обновления."""
        data = self.logins_db.get_login_by_id(self.id_login)
        # выводим значения в поля формы
        self.ent_login_name.insert(0, data[1])
        self.ent_login_password.insert(0, data[2])
        self.txt_description.insert(data[3])
        self.ent_creator.insert(0, data[4])
        self.ent_creator.configure(state="disabled")  # normal, readonly и disabled

    def click_btn_ok(self, event=None):
        """Обновление логина."""
        if self.check_empty():  # проверка на пустые поля
            # данные с формы
            login_name = self.ent_login_name.get()
            login_password = self.ent_login_password.get()
            login_description = self.txt_description.get()
            self.logins_db.update_login_by_id(self.id_login, login_name, login_password, login_description)  # обновляем
            self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть


class Permission(tk.Toplevel):
    """Класс формы управления правами для логинов."""
    def __init__(self, parent, id_login):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Logins
        self.id_login = id_login
        self.logins_db = logins_db.LoginsDB()  # БД логинов
        # Список кортежей прав для логина (id_role, role, id_permission, permission)
        self.permission_list = self.logins_db.get_permission_by_id_login(self.id_login)
        self.checks = []  # Список объектов "Галочка" с ролями пользователей

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title("Управление правами")
        self.width = 415
        self.height = 350
        self.posx = 400
        self.posy = 300
        # self.geometry('415x350+400+300')  # Высота по высоте canvas
        self.geometry("%dx%d+%d+%d" % (self.width, self.height, self.posx, self.posy))
        self.resizable(False, False)

        # TODO: Вынести общие параметры виджетов, по возможности переделать ввод на grid
        # Общая рамка
        self.frm_main = ttk.Frame(self)
        self.frm_main.pack(fill=tk.BOTH, expand=True)
        # Резиновая ячейка для описания для общей рамки
        self.frm_main.columnconfigure(0, weight=1)
        self.frm_main.rowconfigure(1, weight=1)

        # -------------------------------
        # Верхний toolbar (первая строка)
        self.frm_top_toolbar = ttk.Frame(self.frm_main, relief=tk.RAISED, borderwidth=0)
        self.frm_top_toolbar.grid(row=0, column=0, sticky="nesw")

        # Резиновая ячейка для текстового поля на весь экран
        self.frm_top_toolbar.columnconfigure(1, weight=1)
        self.frm_top_toolbar.rowconfigure(0, weight=1)

        # Кнопка
        self.btn_filter = MyButton(
            self.frm_top_toolbar,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.apply_filter],
            text='Применить фильтр', width=18,
        )
        self.btn_filter.grid(row=0, column=0, pady=10, padx=10)

        # Текстовое поле
        self.ent_filter = ttk.Entry(self.frm_top_toolbar)
        self.ent_filter.grid(row=0, column=1, sticky='we', pady=10, padx=10)

        # --------------------------------
        # Рамка для canvas (вторая строка)
        frm_canvas = ttk.Frame(self.frm_main)
        frm_canvas.grid(row=1, column=0, sticky="nesw")

        # Резиновая ячейка для canvas
        frm_canvas.columnconfigure(0, weight=1)
        frm_canvas.rowconfigure(0, weight=1)

        # Создаем Canvas
        # TODO: Вынести Canvas в отдельный класс, со всеми событиями и полосами прокрутки
        #  и использовать в том числе для управления ролями пользователя
        self.canvas = tk.Canvas(frm_canvas)
        self.canvas.grid(row=0, column=0, sticky="nesw")

        # Полоса прокрутки на рамку для Canvas
        canvas_y_scroll = ttk.Scrollbar(frm_canvas, orient="vertical", command=self.canvas.yview)
        canvas_y_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=canvas_y_scroll.set)

        # Рамка для списка Checkbutton
        self.frm_permission = ttk.Frame(self.canvas, relief=tk.RAISED, borderwidth=0)

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frm_permission, anchor="nw")

        # -------
        # События
        self.frm_permission.bind("<Enter>", self._bound_to_mousewheel)  # Курсор над рамкой
        self.frm_permission.bind("<Leave>", self._unbound_to_mousewheel)  # Курсов покинул рамку
        # Подключение работы полосы прокрутки колесиком мышки
        self.frm_permission.bind('<Configure>', self._on_configure)
        # Изменения размеров вложенного frame
        self.canvas.bind("<Configure>", self._on_resize_canvas)

        # ------------------------------
        # Нижний toolbar (третья строка)
        self.frm_bottom_toolbar = ttk.Frame(self.frm_main, relief=tk.RAISED, borderwidth=0)
        self.frm_bottom_toolbar.grid(row=2, column=0, sticky="nesw")

        # self.btn_cancel = ttk.Button(frm_bottom_toolbar, text='Отмена', command=self.click_btn_cancel)
        self.btn_cancel = MyButton(
            self.frm_bottom_toolbar,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_cancel],
            text='Отмена', width=12,
        )
        self.btn_cancel.pack(side=tk.RIGHT, pady=10, padx=10)

        # btn_ok = ttk.Button(frm_bottom_toolbar, text='Сохранить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_bottom_toolbar,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.pack(side=tk.RIGHT, pady=10, padx=10)

        # -------
        # События
        # Привязываем события клавиш на окно
        self.bind('<Return>', self.click_btn_ok)      # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

        # Выводим данные
        self.show_permission()

    def _on_resize_canvas(self, event):
        canvas_width, canvas_height = event.width - 5, event.height - 5
        # Ширина внутренней рамки по ширине canvas
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Выстора внутренней рамки по высоте canvas, если ролей недостаточно для полной высоты
        if self.frm_permission.winfo_height() < canvas_height:
            self.canvas.itemconfig(self.canvas_frame, height=canvas_height)

    def _bound_to_mousewheel(self, event):
        """
        Обработка события входа курсора мыши в область canvas
        (для прокрутки колесиком мышки).
        :param event:
        :return: Нет
        """
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """
        Обработки события выхода курсора мыши из области canvas.
        :param event:
        :return: Нет
        """
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """
        Прокрутки области canvas колесиком мышки.
        :param event:
        :return: Нет
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def show_permission(self):
        """
        Вывод массива галочек со списком ролей.
        :return: Нет
        """
        self.checks = []
        for iter in range(len(self.permission_list)):
            self.checks.append(PermissionCheckButton(self.frm_permission,
                                                     iter,
                                                     self.permission_list[iter][0],
                                                     self.permission_list[iter][1],
                                                     self.permission_list[iter][2],
                                                     self.permission_list[iter][3]))

    def clear_frm_permission(self):
        """Очистки формы со списком ролей."""
        for widget in self.frm_permission.winfo_children():
            widget.destroy()

    def apply_filter(self, event=None):
        """
        Клик по кнопке Применить фильтр,
        применения фильтрации по введенной строке.
        :return: Нет
        """
        self.clear_frm_permission()  # Чистим форму с павами
        self.permission_list = []  # Перезаполняем словарь прав
        if len(self.ent_filter.get()) == 0:
            self.permission_list = self.logins_db.get_permission_by_id_login(self.id_login)
        else:
            self.permission_list = self.logins_db.get_permission_by_like_role_name(self.id_login,
                                                                                   self.ent_filter.get())
        self.show_permission()  # Перезаполняем список ролей

    def click_btn_ok(self, event=None):
        """
        Клик по кнопке Сохранить, применение назначенных прав.
        :return: Нет
        """
        for check in self.checks:
            if self.permission_list[check.iter][3] != check.permission.get():  # Значение изменилось
                if check.permission.get():  # На True
                    # print('Изменен элемент № ' + str(check.iter) + ' Добавлена роль ' + check.role_name)
                    self.add_permission(check.id_role)
                else:
                    # print('Изменен элемент № ' + str(check.iter) + ' Удалена роль ' + check.role_name)
                    self.delete_permission(check.id_permission)
        self.btn_cancel.invoke()  # Имитация клика по "Отмена"

    def click_btn_cancel(self, event=None):
        """Нажатие кнопки Отмена, закрываем окно."""
        self.destroy()

    def add_permission(self, id_role):
        """Добавления прав на новую роль."""
        self.logins_db.insert_permission_by_roles(self.id_login, id_role)

    def delete_permission(self, id_permission):
        """Удаление прав с роли."""
        self.logins_db.delete_permission_by_id(id_permission)





