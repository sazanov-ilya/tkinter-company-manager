from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import Description, MyButton, TopMenuButtons
import _service as srv
import _styles as style
import connection_types_db as connection_types_db  # БД типов подключения


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
# connection_types_filter_dict = {'name': '', 'description': ''}
connection_types_filter_dict = {}


class ConnectionTypes(tk.Frame):
    """Базовый класс для типов подключения, меню и список типов подключения."""
    def __init__(self, root, main, is_admin: bool = None) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                # frm_content_all
        self.main = main                # Main
        self.is_admin: bool = is_admin  # Признак "администратор"
        self.connection_types_db = connection_types_db.ConnectionTypesDB()  # БД типов подключений
        self.connectiontypes_list = []  # Список кортежей типов подключения

        # ----
        # Окно
        # !ВАЖНО для отображения данных на форме
        self.pack(fill=tk.BOTH, expand=True)

        # Свойства
        # self.title('Список типов подключения')

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
            'id': {
                'displaycolumns': False,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'name': {
                'displaycolumns': True,
                'column': {'width': 150, 'anchor': tk.W},
                'heading': {'text': 'Наименование'},
            },
            'description': {
                'displaycolumns': True,
                'column': {'width': 355, 'anchor': tk.W},
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
            label='Копировать наименование', command=self.copy_name)
        self.context_menu.add_command(
            label='Копировать описание', command=self.copy_description)
        self.context_menu.add_command(
            label='Копировать все', command=self.copy_all)

        # -------
        # События
        # Привязываем события клавиш на таблицу
        self.table_list.bind('<Double-Button-1>', self.double_click)  # ЛКМ, двойной клик
        self.table_list.bind('<Button-2>', self.select_row)           # СКМ, выделить строку
        self.table_list.bind('<Button-3>', self.show_context_menu)    # ПКМ, контекстное меню

        # Вызов процедур
        self.show_connection_types()  # Вывод таблицы

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

    def copy_name(self):
        """Копирование наименования в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1'))

    def copy_description(self):
        """Копирование описания в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#2'))

    def copy_all(self):
        """Копирование выделенной строки в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.table_list.set(self.table_list.selection()[0], '#1') + '\n' +
                                   self.table_list.set(self.table_list.selection()[0], '#2'))

    def color_btn_filter(self):
        """Смены цвета кнопки Фильтр."""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if connection_types_filter_dict:  # Если есть фильтры
            self.top_menu_buttons[0].configure(style=style.BUTTON_FILTER)
        else:
            self.top_menu_buttons[0].configure(style=style.BUTTON_CONTROL)

    @staticmethod
    def set_filter(name, description):
        """
        Сохранения и применения фильтра.
        :param name:
        :param description:
        :return: Нет
        """
        connection_types_filter_dict.clear()  # Чистим словарь
        # Пересоздаем словарь
        if name:
            connection_types_filter_dict['name'] = name
        if description:
            connection_types_filter_dict['description'] = srv.get_text_in_one_line(description)

    def show_connection_types(self):
        """Заполнение таблицы типов подключений согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.table_list.delete(i) for i in self.table_list.get_children()]  # Очистка таблицы
        self.connectiontypes_list = self.connection_types_db.get_connection_type_list_by_filter(
            connection_types_filter_dict)
        srv.sorted_table(self.connectiontypes_list)
        [self.table_list.insert('', 'end', values=row) for row in self.connectiontypes_list]

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров для списка типов подключений."""
        FilterConnectionTypes(self)

    def open_new(self, event: Any = None) -> None:
        """Отображение окна для ввода нового типа подключения."""
        NewConnectionType(self)

    def open_update(self, event: Any = None) -> None:
        """Отображение окна для редактирования выбранного типа подключения."""
        if self.table_list.focus() != '':
            # Получаем первую выделенную строку
            item = self.table_list.item(self.table_list.focus())
            connection_type_id = item["values"][0]
            UpdateConnectionType(self, connection_type_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите тип подключения')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных типов подключений."""
        if self.table_list.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # если Да = True
                ids = []  # Список id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.table_list.selection():
                    item = self.table_list.item(selected_item)
                    ids.append(item["values"][0])
                self.connection_types_db.delete_connection_types(ids)  # Удаление данных
                self.show_connection_types()                           # Обновляем таблицу
        else:
            mb.showwarning('Предупреждение', 'Выберите тип подключения')


class ConnectionType(tk.Toplevel):
    """Базовый класс всплывающего окна типа подключения."""
    def __init__(self, parent=None):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main
        self.connection_types_db = connection_types_db.ConnectionTypesDB()  # БД типов подключений

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title("Тип подключения")
        self.geometry('415x200+400+300')
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
        self.frm_main.rowconfigure(1, weight=1)

        # 1 Наименование
        lbl_name = ttk.Label(self.frm_main, text='Тип', style=style.LABEL_CAPTION, **self.options_lbl)
        lbl_name.grid(row=0, column=0, **self.grid_lbl)
        self.ent_name = ttk.Entry(self.frm_main)
        self.ent_name.grid(row=0, column=1, columnspan=4, **self.grid_ent)
        self.ent_name.focus()
        self.ent_name.bind("<Control-KeyPress>", srv.keys)

        # 2 Описание
        lbl_description = ttk.Label(self.frm_main, text='Описание', style=style.LABEL_CAPTION, **self.options_lbl)
        lbl_description.grid(row=1, column=0, **self.grid_lbl)
        self.txt_description = Description(self.frm_main)
        self.txt_description.grid(row=1, column=1, columnspan=4, **self.grid_txt)

        # 3 Кнопки
        # self.btn_cancel = ttk.Button(self.frm_main, text='Отмена', command=self.click_btn_cancel)
        self.btn_cancel = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_cancel],
            text='Отмена', width=12,
        )
        self.btn_cancel.grid(row=2, column=4, **self.grid_btn_control)

        # -------
        # События
        # Виртуальное событие "Сохранить и закрыть окно"
        # Нужно для вызова из текстового поля для перехвата события KeyPress-Return
        self.event_generate('<<GlobalExit>>')  # doesn't trigger child binding
        self.bind('<<GlobalExit>>', self.click_btn_ok)

        # Привязываем события клавиш на окно
        self.bind('<Return>', self.click_btn_ok)      # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

    def click_btn_ok(self, event=None):
        """Клик по кнопке Ok (Применить/Обновить и т.п.)."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        # Заглушка, для создания события, реальная процедура в наследующем классе
        pass

    def click_btn_cancel(self, event=None):
        """Клик по кнопке Отмена, закрываем окно."""
        self.parent.show_connection_types()  # Обновляем таблицу-список
        self.destroy()

    def check_empty(self):
        """
        Проверка на пустые поля формы.
        :return: True/False
        """
        if len(self.ent_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите тип подключения')
            return False
        return True

    def check_exists(self):
        """
        Проверка дублей компании по введенным данным.
        :return: True/False
        """
        data = self.connection_types_db.get_connection_type_name_by_name(self.ent_name.get())
        if data:
            mb.showwarning('Предупреждение', 'Дубль логина <' + data + '>')
            return False
        return True


class FilterConnectionTypes(ConnectionType):
    """Класс формы фильтров для отображения списка подключений."""
    def __init__(self, parent):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ####
        # Окно
        self.title('Фильтр типов доступа')

        # 3 Добавляем кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Применить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Применить', width=12,
        )
        self.btn_ok.grid(row=2, column=2, **self.grid_btn_control)
        #
        # btn_clear_filter = ttk.Button(self.frm_main, text='Сбросить', command=self.click_btn_clear_filter)
        self.btn_clear_filter = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_clear_filter],
            text='Сбросить', width=12,
        )
        self.btn_clear_filter.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_filter()

    def get_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        if connection_types_filter_dict:
            if connection_types_filter_dict.get('name', ''):
                self.ent_name.insert(0, connection_types_filter_dict.get('name', ''))
            if connection_types_filter_dict.get('description', ''):
                self.txt_description.insert(connection_types_filter_dict.get('description', ''))

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        self.parent.set_filter(self.ent_name.get(),
                               self.txt_description.get())
        self.btn_cancel.invoke()  # Имитация клика по "Отмена"

    def click_btn_clear_filter(self, event=None):
        """Клик по кнопке Сбросить, очистка фильтров."""
        self.parent.set_filter(None, None)
        self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class NewConnectionType(ConnectionType):
    """Класс формы добавления подключения."""
    def __init__(self, parent):  # Конструктор
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ####
        # Окно
        self.title('Добавить подключение')

        # 3 Кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Сохранить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

    def click_btn_ok(self, event=None):
        """Сохранение нового типа подключения."""
        if self.check_empty() and self.check_exists():  # Проверка на пустые поля и дубль
            # Сохраняем
            self.connection_types_db.insert_new_connection_type(self.ent_name.get(),
                                                                self.txt_description.get())
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateConnectionType(ConnectionType):
    """Класс формы обновления типов подключений."""
    def __init__(self, parent, id_connection_type):  # Конструктор
        super().__init__()
        # Атрибуты
        self.parent = parent  # ConnectionTypes
        self.id_connection_type = id_connection_type

        # ####
        # Окно
        self.title('Обновить тип подключение')

        # 3 Добавляем кнопки
        # btn_ok = ttk.Button(self.frm_main, text='Обновить', command=self.click_btn_ok)
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_connection_type_for_update()

    def get_connection_type_for_update(self):
        """Получение и вывода на форму данных типа подключения для обновления."""
        data = self.connection_types_db.get_connection_type_by_id(self.id_connection_type)
        # Выводим значения в поля формы
        self.ent_name.insert(0, data[1])
        self.txt_description.insert(data[2])

    def click_btn_ok(self, event=None):
        """Обновление типа подключения."""
        if self.check_empty():  # Проверка на пустые поля
            self.connection_types_db.update_connection_type_by_id(self.id_connection_type,
                                                                  self.ent_name.get(),
                                                                  self.txt_description.get())
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"





