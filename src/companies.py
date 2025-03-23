from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import Description, MyButton, TopMenuButtons
import _service as srv
import _styles as style
import companies_db as companies_db  # БД для форм компаний


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
# companies_filter_dict = {'name': '', 'description': ''}
companies_filter_dict = {}


class Companies(tk.Frame):
    """Класс для компаний, меню и список компаний."""
    def __init__(self, root, main, is_admin: bool = None) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                                # frm_content_all
        self.main = main                                # Main
        self.is_admin: bool = is_admin                  # Признак "администратор"
        self.companies_db = companies_db.CompaniesDB()  # БД компаний
        self.companies_list = []                        # Список кортежей компаний

        # ----
        # Окно
        # !ВАЖНО для отображения на полное окно
        self.pack(fill=tk.BOTH, expand=True)

        # Свойства
        # self.title('Список компаний')

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
            'id_company': {
                'displaycolumns': False,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'company_name': {
                'displaycolumns': True,
                'column': {'width': 150, 'anchor': tk.W},
                'heading': {'text': 'Наименование'},
            },
            'company_description': {
                'displaycolumns': True,
                'column': {'width': 355, 'anchor': tk.W},
                'heading': {'text': 'Описание'},
            },
        }
        # Настраиваем таблицу по словарю
        self.companies_table = ttk.Treeview(self.frm_treeview, columns=([key for key in self.columns]),
                                            displaycolumns=(
                                                [key for key in self.columns if self.columns[key]['displaycolumns']]),
                                            **self.treeview_options)
        for key, value in self.columns.items():
            self.companies_table.column(key, **value['column'])
            self.companies_table.heading(key, **value['heading'])

        self.companies_table.grid(row=0, column=0, sticky='nwse')

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self.frm_treeview, command=self.companies_table.yview)
        scroll.grid(row=0, column=1, sticky='nwse')
        self.companies_table.configure(yscrollcommand=scroll.set)

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.companies_table, tearoff=0)
        self.context_menu.add_command(
            label='Копировать наименование', command=self.copy_name)
        self.context_menu.add_command(
            label='Копировать описание', command=self.copy_description)
        self.context_menu.add_command(
            label='Копировать все', command=self.copy_all)

        # -------
        # События
        # Привязываем события клавиш на таблицу
        self.companies_table.bind('<Button-2>', self.select_row)           # СКМ, выделить строку
        self.companies_table.bind('<Button-3>', self.show_context_menu)    # ЛКМ, контекстное меню
        self.companies_table.bind('<Double-Button-1>', self.double_click)  # СКМ, выделить строку

        # Выводим данные
        self.show_companies()

    def select_row(self, event=None):
        """Выделение строки в таблице."""
        # Получаем идентификатор строки под курсором
        iid = self.companies_table.identify_row(event.y)
        if iid:
            # Выделяем строку под курсором по ее идентификатору
            self.companies_table.selection_set(iid)
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
        """Копирование названия компании в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.companies_table.set(self.companies_table.selection()[0], '#1'))

    def copy_description(self):
        """Копирование описания компании в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.companies_table.set(self.companies_table.selection()[0], '#2'))

    def copy_all(self):
        """Копирование выделенной строки в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.companies_table.set(self.companies_table.selection()[0], '#1') + '\n' +
                                   self.companies_table.set(self.companies_table.selection()[0], '#2'))

    def color_btn_filter(self):
        """Смены цвета кнопки Фильтр."""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if companies_filter_dict:  # Если есть фильтры
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
        companies_filter_dict.clear()  # Чистим словарь
        # Пересоздаем словарь
        if name:
            companies_filter_dict['name'] = name
        if description:
            companies_filter_dict['description'] = srv.get_text_in_one_line(description)

    def show_companies(self) -> None:
        """Заполнение таблицы компаний согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.companies_table.delete(i) for i in self.companies_table.get_children()]  # Очистка таблицы
        self.companies_list = self.companies_db.get_company_list_by_filter(companies_filter_dict)
        srv.sorted_table(self.companies_list)
        [self.companies_table.insert('', 'end', values=row) for row in self.companies_list]  # Заполняем таблицу

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров для списка компаний."""
        FilterCompany(self)

    def open_new(self, event: Any = None) -> None:
        """Отображение окна для ввода новой компании."""
        NewCompany(self)

    def open_update(self, event: Any = None) -> None:
        """Отображение окна для редактирования выбранной компании."""
        if self.companies_table.focus() != '':
            # Получаем первую выделенную строку
            item = self.companies_table.item(self.companies_table.focus())
            company_id = item["values"][0]
            UpdateCompany(self, company_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите компанию')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных компаний."""
        if self.companies_table.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # если Да = True
                ids = []  # Список id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.companies_table.selection():
                    item = self.companies_table.item(selected_item)
                    ids.append(item["values"][0])
                self.companies_db.delete_companies(ids)
                self.show_companies()  # Обновляем таблицу компаний
        else:
            mb.showwarning('Предупреждение', 'Выберите компанию')


class Company(tk.Toplevel):
    """Базовый класс формы компании."""
    def __init__(self, parent=None):
        super().__init__()
        # Атрибуты
        self.parent = parent                            # Companies
        self.companies_db = companies_db.CompaniesDB()  # БД компаний

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title('Добавить компанию')
        self.geometry('415x200+400+300')
        self.resizable(False, False)

        # Парамеры для единой стилизации меток для текстовых полей
        self.options_lbl = {'width': 10}
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
        self.frm_main.rowconfigure(1, weight=1)

        # 1 Наименование
        lbl_name = ttk.Label(self.frm_main, text='Компания', style=style.LABEL_CAPTION, **self.options_lbl)
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
        self.bind('<Return>', self.click_btn_ok)  # Нажать Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Нажать Esc
        # self.bind('<KeyRelease-Return>', self.click_btn_ok)  # Отпустить Enter
        # self.bind('<KeyRelease-Escape>', self.click_btn_cancel)  # Отпустить Esc

    def click_btn_ok(self, event=None):
        """Клик по кнопке Ok (Применить/Обновить и т.п.)."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        # Заглушка, для создания события, реальная процедура в наследующем классе
        pass

    def click_btn_cancel(self, event=None):
        """Клик по кнопке Отмена."""
        self.parent.show_companies()  # Обновляем таблицу
        self.destroy()

    def check_empty(self):
        """
        Проверка на пустые поля формы.
        :return: True/False
        """
        if len(self.ent_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите компанию')
            return False
        return True

    def check_exists(self):
        """
        Проверка дублей компании по введенным данным.
        :return: True/False
        """
        company_name = self.ent_name.get()
        data = self.companies_db.get_company_name_by_name(company_name)
        if data:
            mb.showwarning('Предупреждение', 'Дубль компании <' + data + '>')
            return False
        return True


class FilterCompany(Company):
    """Класс формы фильтров для отображения списка компаний."""
    def __init__(self, parent):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ----
        # Окно
        self.title('Фильтр компаний')

        # Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Применить', width=12,
        )
        self.btn_ok.grid(row=2, column=2, **self.grid_btn_control)

        self.btn_clear_filter = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.clear_filter],
            text='Сбросить', width=12,
        )
        self.btn_clear_filter.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_filter()

    def get_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        if companies_filter_dict:
            if companies_filter_dict.get('name', ''):
                self.ent_name.insert(0, companies_filter_dict.get('name', ''))
            if companies_filter_dict.get('description', ''):
                self.txt_description.insert(companies_filter_dict.get('description', ''))

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        self.parent.set_filter(self.ent_name.get(),
                               self.txt_description.get())
        self.btn_cancel.invoke()  # Имитация клика по "Отмена"

    def clear_filter(self, event=None):
        """Клик по кнопке Сбросить, очистка фильтров."""
        self.parent.set_filter(None, None)
        self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть


class NewCompany(Company):
    """Класс формы добавления компании."""
    def __init__(self, parent):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main

        # ----
        # Окно
        self.title('Добавить компанию')

        # 3 Кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

    def click_btn_ok(self, event=None):
        """Сохранение новой компании."""
        if self.check_empty() and self.check_exists():  # Проверка на пустые поля и дубль
            self.companies_db.insert_new_company(self.ent_name.get(),
                                                 self.txt_description.get())  # Сохраняем
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateCompany(Company):
    """Класс формы обновления компании."""
    def __init__(self, parent, id_company):
        super().__init__()
        # Атрибуты
        self.parent = parent  # Main
        self.id_company = id_company

        # ----
        # Окно
        self.title('Обновить компанию')

        # 3 Кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_company_for_update()

    def get_company_for_update(self):
        """Получение и вывода на форму данных компании для обновления."""
        data = self.companies_db.get_company_by_id(self.id_company)
        self.ent_name.insert(0, data[1])
        self.txt_description.insert(data[2])

    def click_btn_ok(self, event=None):
        """Обновление компании."""
        if self.check_empty():  # Проверка на пустые поля
            self.companies_db.update_company_by_id(self.id_company,
                                                   self.ent_name.get(),
                                                   self.txt_description.get())  # Обновляем
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"
