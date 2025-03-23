import ctypes
from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import Description, MyButton, TopMenuButtons
import _service as srv
import _styles as style
import logins as logins
import connections_db as connections_db            # БД для форм подключения
import companies_db as companies_db                # БД для форм компаний
import connection_types_db as connection_types_db  # БД для форм типов подключения


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
# connections_filter_dict = {
#     'id_company': '',
#     'id_connection_type': '',
#     'connection_ip': '',
#     'connection_description': '',
# }
connections_filter_dict = {}


class Connections(tk.Frame):
    """ Базовый класс формы списка подключений """
    def __init__(self, root, main, is_admin: bool) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                # frm_content_all
        self.main = main                # Main
        self.is_admin: bool = is_admin  # Признак "администратор"
        self.connections_db = connections_db.ConnectionsDB()  # БД подключений
        self.logins = None          # Класс формы списка логинов для выбранного подключения
        self.connections_list = []  # Список кортежей подключений

        # ----
        # Окно
        # !ВАЖНО для отображения данных на форме
        self.pack(fill=tk.BOTH, expand=True)

        # Свойства
        # self.title('Список подключений')

        # (визуальный макет формы)
        # Резиновая ячейка с таблицей
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # --------------------------
        # Рамка для верхнего toolbar
        self.frm_top_toolbar = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        self.frm_top_toolbar.grid(row=0, column=0, sticky='nwse')

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
                'is_admin': False,
                'callbacks': [self.open_logins],
                'options': {'text': 'Открыть логины', 'width': 20},
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

        # ----------------
        # Таблица Treeview
        self.treeview_options = {'height': 10, 'show': 'headings'}  # , 'selectmode': 'browse'}
        self.columns = {
            'id_connection': {
                'displaycolumns': False,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'company_name': {
                'displaycolumns': True,
                'column': {'width': 110, 'anchor': tk.W},
                'heading': {'text': 'Компания'},
            },
            'connection_type_name': {
                'displaycolumns': True,
                'column': {'width': 110, 'anchor': tk.W},
                'heading': {'text': 'Тип подключения'},
            },
            'connection_ip': {
                'displaycolumns': True,
                'column': {'width': 100, 'anchor': tk.W},
                'heading': {'text': 'Ip/домен'},
            },
            'connection_description': {
                'displaycolumns': True,
                'column': {'width': 300, 'anchor': tk.W},
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

        self.table_list.grid(row=0, column=0, sticky='nwse')

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self.frm_treeview, command=self.table_list.yview)
        scroll.grid(row=0, column=1, sticky='nwse')
        self.table_list.configure(yscrollcommand=scroll.set)

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.table_list, tearoff=0)
        self.context_menu.add_command(
            label='Копировать компанию', command=self.copy_company)
        self.context_menu.add_command(
            label='Копировать тип подкл.', command=self.copy_conn_type)
        self.context_menu.add_command(
            label='Копировать домен', command=self.copy_domain)
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

        # Выводим данные
        self.show_connections()

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
            self.open_logins()

    def show_context_menu(self, event=None):
        """
        Отображение контекстного меню.
        :param event:
        :return: Нет
        """
        if self.select_row(event):  # Если строка была выделена
            self.context_menu.post(event.x_root, event.y_root)

    def copy_company(self):
        """Копирование наименования в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1'))

    def copy_conn_type(self):
        """Копирование типа подключения в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#2'))

    def copy_domain(self):
        """Копирование ip/домена в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#3'))

    def copy_description(self):
        """Копирование описания в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#4'))

    def copy_all(self):
        """Копирование выделенной строки в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#2') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#3') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#4'))

    def color_btn_filter(self):
        """Смены цвета кнопки Фильтр."""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if connections_filter_dict:  # Если есть фильтры
            self.top_menu_buttons[0].configure(style=style.BUTTON_FILTER)
        else:
            self.top_menu_buttons[0].configure(style=style.BUTTON_CONTROL)

    @staticmethod
    def set_filter(id_company, id_connection_type, connection_ip, connection_description):
        """
        Сохранения и применения фильтра.
        :param id_company:
        :param id_connection_type:
        :param connection_ip:
        :param connection_description:
        :return: Нет
        """
        connections_filter_dict.clear()  # Чистим словарь
        # Пересоздаем словарь
        if id_company:
            connections_filter_dict['id_company'] = id_company
        if id_connection_type:
            connections_filter_dict['id_connection_type'] = id_connection_type
        if connection_ip:
            connections_filter_dict['connection_ip'] = connection_ip
        # Поле заблокировано
        # if connection_description:
        #     connections_filter_dict['connection_description'] = srv.get_text_in_one_line(connection_description)

    def show_connections(self):
        """Заполнение таблицы подключений согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.table_list.delete(i) for i in self.table_list.get_children()]  # Чистим таблицу
        self.connections_list = self.connections_db.get_connections_by_filter(connections_filter_dict)
        srv.sorted_table(self.connections_list)  # Сортировка
        [self.table_list.insert('', 'end', values=row) for row in self.connections_list]  # Выводим список на форму

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров для списка подключений."""
        FilterConnections(self)

    def open_new(self, event: Any = None) -> None:
        """Отображение окна для ввода нового подключения."""
        NewConnection(self)

    def open_update(self, event: Any = None) -> None:
        """Отображение окна для редактирования выбранного подключения."""
        if self.table_list.focus() != '':
            # Получаем первую выделенную строку
            item = self.table_list.item(self.table_list.focus())
            connection_id = item["values"][0]
            UpdateConnection(self, connection_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите подключение')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных подключений."""
        if self.table_list.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # Если Да = True
                ids = []  # Список id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.table_list.selection():
                    item = self.table_list.item(selected_item)
                    ids.append(item["values"][0])
                self.connections_db.delete_connections(ids)  # Удаление данных
                self.show_connections()                      # Обновляем таблицу
        else:
            mb.showwarning('Предупреждение', 'Выберите подключение')

    def open_logins(self, event: Any = None) -> None:
        """
        Отображение окна со списком всех логинов выделенного подключения.
        Передаем app и id первого выбранного в списке подключения.
        """
        if self.table_list.focus() != '':
            # Получаем первую выделенную строку
            item = self.table_list.item(self.table_list.focus())
            connection_id = int(item["values"][0])
            self.main.clear_frm_content_all()                                                 # Чистим форму
            self.logins = logins.Logins(self.main.frm_content_all, self.main, connection_id, self.is_admin)
        else:
            mb.showwarning('Предупреждение', 'Выберите подключение в списке')


class Connection(tk.Toplevel):
    """Базовый класс всплывающего окна подключений."""
    def __init__(self, parent=None):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main
        self.connections_db = connections_db.ConnectionsDB()                # БД подключений
        self.companies_db = companies_db.CompaniesDB()                      # БД компаний
        self.connection_types_db = connection_types_db.ConnectionTypesDB()  # БД типов подключений
        self.comps_list = None       # Список компаний, загружаем при выводе формы
        self.conn_types_list = None  # Список типов подключения

        # ----
        # Окно
        # Тема
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title("Подключения")
        self.geometry('450x250+400+300')
        self.resizable(False, False)

        # Парамеры для единой стилизации меток для текстовых полей
        self.options_lbl = {'width': 17}
        self.grid_lbl = {'sticky': 'nw', 'padx': 10, 'pady': 10}
        # Парамеры для единой стилизации однострочных текстовых полей
        self.grid_ent = {'sticky': 'we', 'padx': 10}  # ent_padding
        # Парамеры для единой стилизации многострочного текстового поля
        self.grid_txt = {'sticky': 'nwse', 'pady': 10, 'padx': 10}
        # Парамеры для единой стилизации кнопок управления
        self.grid_btn_control = {'sticky': 'we', 'pady': 10, 'padx': 10}

        # Главная рамка, для наследования стилей
        self.frm_main = ttk.Frame(self)
        self.frm_main.pack(fill=tk.BOTH, expand=True)

        # Резиновая ячейка для описания
        self.frm_main.columnconfigure(1, weight=1)
        self.frm_main.rowconfigure(3, weight=1)

        # 1
        lbl_comps_list = ttk.Label(
            self.frm_main, text="Компания", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_comps_list.grid(row=0, column=0, **self.grid_lbl)
        self.cmb_comps_list = ttk.Combobox(self.frm_main, width=50, height=20)
        self.cmb_comps_list.grid(row=0, column=1, columnspan=4, **self.grid_ent)

        # 2
        lbl_conn_types_list = ttk.Label(
            self.frm_main, text="Тип подключения", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_conn_types_list.grid(row=1, column=0, **self.grid_lbl)
        self.cmb_conn_types_list = ttk.Combobox(self.frm_main, width=50, height=20)
        self.cmb_conn_types_list.grid(row=1, column=1, columnspan=4, **self.grid_ent)

        # 3
        lbl_conn_name = ttk.Label(
            self.frm_main, text="Ip-адрес/домен", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_conn_name.grid(row=2, column=0, **self.grid_lbl)
        self.ent_conn_name = ttk.Entry(self.frm_main)
        self.ent_conn_name.grid(row=2, column=1, columnspan=4, **self.grid_ent)
        self.ent_conn_name.bind("<Control-KeyPress>", srv.keys)

        # 4
        self.lbl_conn_description = ttk.Label(
            self.frm_main, text="Описание", style=style.LABEL_CAPTION, **self.options_lbl
        )
        self.lbl_conn_description.grid(row=3, column=0, **self.grid_lbl)
        self.txt_description = Description(self.frm_main)
        self.txt_description.grid(row=3, column=1, columnspan=4, **self.grid_txt)

        # 5 Кнопки
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
        self.parent.show_connections()  # Обновляем таблицу-список
        self.destroy()

    def get_comps_list(self):
        """Заполнение выпадающего списка компаний."""
        self.comps_list = self.companies_db.get_company_for_list()
        # first, second- первые 2 элемента, *other - все остальные элементы
        # self.cmb_comps_list['values'] = [second for first, second, *other in data]
        self.cmb_comps_list['values'] = [elem[1] for elem in self.comps_list]
        # self.cmb_comps_list.current(0)

    def get_conn_types_list(self):
        """Заполнение выпадающего списка типов подключения."""
        self.conn_types_list = self.connection_types_db.get_connection_type_for_list()
        self.cmb_conn_types_list['values'] = [elem[1] for elem in self.conn_types_list]

    def check_empty(self):
        """
        Проверка на пустые поля формы.
        :return: True/False
        """
        if (self.cmb_comps_list.current()) == -1:
            mb.showwarning('Предупреждение', 'Выберите компанию')
            return False
        elif (self.cmb_conn_types_list.current()) == -1:
            mb.showwarning('Предупреждение', 'Выберите тип доступа')
            return False
        elif len(self.ent_conn_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите Ip-адрес/домен')
            return False
        return True

    def check_exists(self):
        """
        Проверка дублей подключения по введенным данным.
        :return: True/False
        """
        id_company = self.comps_list[self.cmb_comps_list.current()][0]
        id_connection_type = self.conn_types_list[self.cmb_conn_types_list.current()][0]
        conn_name = self.ent_conn_name.get()
        data = self.connections_db.get_connection_ip_for_check_exists(id_company, id_connection_type, conn_name)
        if data:
            mb.showwarning('Предупреждение', 'Данное подключение уже существует')
            return False
        return True


class FilterConnections(Connection):
    """Класс формы ввода фильтров для списка подключений."""
    def __init__(self, parent):  # Конструктор
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ----
        # Окно
        self.title('Фильтр подключений')

        # Блокируем "Описание"
        self.lbl_conn_description.configure(state="disabled")  # normal, readonly и disabled
        self.txt_description.disabled()  # normal, readonly и disabled

        # 5 Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Применить', width=12,
        )
        self.btn_ok.grid(row=4, column=2, **self.grid_btn_control)

        self.btn_clear_filter = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_clear_filter],
            text='Сбросить', width=12,
        )
        self.btn_clear_filter.grid(row=4, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_comps_list()       # Список компаний
        self.get_conn_types_list()  # Список типов подключения
        self.get_connection_filter()

    def get_connection_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        if connections_filter_dict:
            # Получаем текущие фильтры
            id_company = connections_filter_dict.get('id_company', '')
            id_connection_type = connections_filter_dict.get('id_connection_type', '')
            connection_ip = connections_filter_dict.get('connection_ip', '')
            connection_description = connections_filter_dict.get('connection_description', '')

            # Компания по фильтру
            if id_company:
                index_company = 0
                for items in self.comps_list:
                    if items[0] == id_company:
                        break
                    index_company += 1
                self.cmb_comps_list.current(index_company)

            # Тип подключения по фильтру
            if id_connection_type:
                index_connection_type = 0
                for items in self.conn_types_list:
                    if items[0] == id_connection_type:
                        break
                    index_connection_type += 1
                self.cmb_conn_types_list.current(index_connection_type)

            if connection_ip:
                self.ent_conn_name.insert(0, connection_ip)
            if connection_description:
                self.txt_description.insert(connection_description)

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        # Получаем компанию с формы
        if (self.cmb_comps_list.current()) == -1:
            id_company = ''
        else:
            id_company = self.comps_list[self.cmb_comps_list.current()][0]
        # Получаем тип подключения с формы
        if (self.cmb_conn_types_list.current()) == -1:
            id_connection_type = ''
        else:
            id_connection_type = self.conn_types_list[self.cmb_conn_types_list.current()][0]
        # Сохраняем фильтр
        self.parent.set_filter(id_company,
                               id_connection_type,
                               self.ent_conn_name.get(),
                               self.txt_description.get())
        self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть

    def click_btn_clear_filter(self, event=None):
        """Клик по кнопке Сбросить, очистка фильтров."""
        self.parent.set_filter(None, None, None, None)
        self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть


class NewConnection(Connection):
    """Класс формы ввода нового подключения."""
    def __init__(self, parent):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ----
        # Окно
        self.title('Добавить подключение')

        # 5 Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=4, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_comps_list()       # Список компаний
        self.get_conn_types_list()  # Список типов подключения

    def click_btn_ok(self, event=None):
        """Сохранение нового подключения."""
        if self.check_empty() and self.check_exists():  # проверка на пустые поля и дубль
            # Данные с формы
            id_company = self.comps_list[self.cmb_comps_list.current()][0]
            id_connection_type = self.conn_types_list[self.cmb_conn_types_list.current()][0]
            # Сохраняем
            self.connections_db.insert_new_connection(id_company,
                                                      id_connection_type,
                                                      self.ent_conn_name.get(),
                                                      self.txt_description.get())
            self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть


class UpdateConnection(Connection):
    """Класс формы обновления подключения."""
    def __init__(self, parent, id_connection):  # конструктор
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main
        self.id_connection = id_connection

        # ----
        # Окно
        self.title('Обновить подключение')

        # 5 Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=4, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_connection_for_update()

    def get_connection_for_update(self):
        """Получение и вывода на форму данных подключения для обновления."""
        data = self.connections_db.get_connection_for_update_by_id(self.id_connection)
        # Выводим значения в поля формы
        self.cmb_comps_list['values'] = [data[1]]
        self.cmb_comps_list.current(0)
        self.cmb_comps_list.configure(state="disabled")  # normal, readonly и disabled
        self.cmb_conn_types_list['values'] = [data[2]]
        self.cmb_conn_types_list.current(0)
        self.cmb_conn_types_list.configure(state="disabled")  # normal, readonly и disabled
        self.ent_conn_name.insert(0, data[3])
        self.txt_description.insert(data[4])

    def click_btn_ok(self, event=None):
        """Обновление подключения."""
        if self.check_empty():  # Проверка на пустые поля
            self.connections_db.update_connection_by_id(self.id_connection,
                                                        self.ent_conn_name.get(),
                                                        self.txt_description.get())  # Обновляем
            self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть
