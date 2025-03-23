# TODO: Поставить запрет удаления ролей если роль есть у пользователя или,
#  если у роли есть права на логины

from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули*
from _classes import MyButton, TopMenuButtons
import _service as srv
import _styles as style
import users_db as users_db       # БД для форм пользователей
from _classes import Description  # Импорт класса для поля "Комментарий"


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
# roles_filter_dict = {'role_name': '', 'role_description': ''}
roles_filter_dict = {}


class Roles(tk.Frame):
    """Класс формы списка ролей."""
    def __init__(self, root, main, is_admin: bool) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                    # frm_content_all
        self.main = main                    # Main
        self.is_admin: bool = is_admin      # Признак "администратор"
        self.roles_db = users_db.RolesDB()  # БД ролей
        self.roles_list = []                # Список кортежей ролей

        # ----
        # Окно
        # !ВАЖНО для отображения данных на форме
        self.pack(fill=tk.BOTH, expand=True)

        # Свойства
        # self.title('Список ролей пользователей')

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

        # --------------------------
        # Рамка для treeview
        self.frm_treeview = ttk.Frame(self, relief=tk.RAISED, borderwidth=0)
        self.frm_treeview.grid(row=1, column=0, sticky='nwse')

        # Резиновая ячейка с таблицей
        self.frm_treeview.columnconfigure(0, weight=1)
        self.frm_treeview.rowconfigure(0, weight=1)

        # ----------------
        # Таблица Treeview
        self.treeview_options = {'height': 10, 'show': 'headings'}  # , 'selectmode': 'browse'}
        self.columns = {
            'id_role': {
                'displaycolumns': False,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'role_name': {
                'displaycolumns': True,
                'column': {'width': 150, 'anchor': tk.W},
                'heading': {'text': 'Наименование'},
            },
            'role_description': {
                'displaycolumns': True,
                'column': {'width': 355, 'anchor': tk.W},
                'heading': {'text': 'Описание'},
            },
        }
        # Настраиваем таблицу по словарю
        self.roles_table = ttk.Treeview(self.frm_treeview, columns=([key for key in self.columns]),
                                        displaycolumns=(
                                            [key for key in self.columns if self.columns[key]['displaycolumns']]),
                                        **self.treeview_options)
        for key, value in self.columns.items():
            self.roles_table.column(key, **value['column'])
            self.roles_table.heading(key, **value['heading'])

        self.roles_table.grid(row=0, column=0, sticky='nwse')

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self.frm_treeview, command=self.roles_table.yview)
        # scroll.pack(side=tk.RIGHT, fill=tk.Y)
        scroll.grid(row=0, column=1, sticky='nwse')
        self.roles_table.configure(yscrollcommand=scroll.set)

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.roles_table, tearoff=0)
        self.context_menu.add_command(
            label='Копировать наименование', command=self.copy_name)
        self.context_menu.add_command(
            label='Копировать описание', command=self.copy_description)
        # self.context_menu.add_command(
        #     label='Копировать все', command=self.copy_all)

        # -------
        # События
        # Привязываем события клавиш на таблицу
        self.roles_table.bind('<Button-2>', self.select_row)  # СКМ, выделить строку
        self.roles_table.bind('<Button-3>', self.show_context_menu)  # ЛКМ, контекстное меню
        self.roles_table.bind('<Double-Button-1>', self.double_click)  # СКМ, выделить строку

        # Показываем окно
        self.show_roles()

    def select_row(self, event=None):
        """Выделение строки в таблице."""
        # Получаем идентификатор строки под курсором
        iid = self.roles_table.identify_row(event.y)
        if iid:
            # Выделяем строку под курсором по ее идентификатору
            self.roles_table.selection_set(iid)
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
        self.root.clipboard_append(self.roles_table.set(self.roles_table.selection()[0], '#1'))

    def copy_description(self):
        """Копирование описания в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.roles_table.set(self.roles_table.selection()[0], '#2'))

    def copy_all(self):
        """Копирование наименования и описания в буфер обмена."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.roles_table.set(self.roles_table.selection()[0], '#1') + '\n' +
                                   self.roles_table.set(self.roles_table.selection()[0], '#2'))

    def color_btn_filter(self) -> None:
        """Смена цвета кнопки Фильтр"""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if roles_filter_dict:  # Если есть фильтры
            self.top_menu_buttons[0].configure(style=style.BUTTON_FILTER)
        else:
            self.top_menu_buttons[0].configure(style=style.BUTTON_CONTROL)

    def set_filter(self, role_name, role_description):
        """Сохранения и применения фильтра.
        :param role_name:
        :param role_description:
        :return: Нет
        """
        roles_filter_dict.clear()  # Чистим словарь
        # Пересоздаем словарь
        if role_name:
            roles_filter_dict['role_name'] = role_name
        if role_description:
            roles_filter_dict['role_description'] = role_description

    def show_roles(self):
        """Заполнение таблицы ролей согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.roles_table.delete(i) for i in self.roles_table.get_children()]  # Чистим таблицу
        self.roles_list = self.roles_db.get_roles_by_filter(roles_filter_dict.get('role_name', ''),
                                                            roles_filter_dict.get('role_description', ''))
        srv.sorted_table(self.roles_list)
        [self.roles_table.insert('', 'end', values=row) for row in self.roles_list]  # Выводим список на форму

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров для списка ролей."""
        FilterRole(self.main, self)

    def open_new(self, event: Any = None) -> None:
        """Отображение окна для ввода новой роли."""
        NewRole(self.main, self)

    def open_update(self, event: Any = None) -> None:
        """Отображение окна для редактирования выбранной роли."""
        if self.roles_table.focus() != '':
            # Получаем первую выделенную строку
            item = self.roles_table.item(self.roles_table.focus())
            role_id = item['values'][0]
            role_name = item['values'][1]
            # Запрет на редактирование роли для базового админа
            if self.roles_db.get_role_name_for_admin() != role_name:
                UpdateRole(self.main, self, role_id)
            else:
                mb.showwarning('Предупреждение', 'Редактирование базовой роли для администратора запрещено')
        else:
            mb.showwarning('Предупреждение', 'Выберите роль')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных ролей."""
        if self.roles_table.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message='Хотите удалить выбранные элементы?')
            if answer:  # Если Да = True
                ids = []  # Кортеж id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.roles_table.selection():
                    item = self.roles_table.item(selected_item)
                    ids.append(item['values'][0])
                self.roles_db.delete_roles(ids)
                self.show_roles()  # Обновляем таблицу ролей
        else:
            mb.showwarning('Предупреждение', 'Выберите роль/роли')


class Role(tk.Toplevel):
    """Базовый класс всплывающего окна роли."""
    def __init__(self, main, parent):
        super().__init__()
        # Атрибуты
        self.main = main                    # Main
        self.parent = parent                # Roles
        self.roles_db = users_db.RolesDB()  # Подключаем роли

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title('Роль')
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
        lbl_name = ttk.Label(self.frm_main, text='Роль', style=style.LABEL_CAPTION, **self.options_lbl)
        lbl_name.grid(row=0, column=0, **self.grid_lbl)
        self.ent_name = ttk.Entry(self.frm_main)
        self.ent_name.grid(row=0, column=1, columnspan=4, **self.grid_ent)
        self.ent_name.focus()
        self.ent_name.bind('<Control-KeyPress>', srv.keys)

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
        self.event_generate('<<GlobalExit>>')  # Не запускает дочернюю привязку события
        self.bind('<<GlobalExit>>', self.click_btn_ok)

        # Привязываем события клавиш на окно
        self.bind('<Return>', self.click_btn_ok)      # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        # Заглушка, для создания события, реальная процедура в наследующем классе
        pass

    def click_btn_cancel(self, event=None):
        """Клик по кнопке Отмена."""
        self.parent.show_roles()  # Обновляем таблицу-список
        self.destroy()

    def check_empty(self):
        """Проверка на пустые поля формы.
        :return: True/False
        """
        if len(self.ent_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите роль')
            return False
        return True

    def check_exists(self):
        """Проверки дублей роли по введенным данным.
        :return: True/False
        """
        data = self.roles_db.get_role_for_check_exists(self.ent_name.get())
        if data:
            mb.showwarning('Предупреждение', 'Роль <' + data + '> уже существует')
            return False
        return True


class FilterRole(Role):
    """Класс формы фильтров для списка ролей."""
    def __init__(self, main, parent):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins

        # ----
        # Окно
        # Свойства
        self.title('Фильтр списка ролей')

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
            callbacks=[self.click_btn_clear_filter],
            text='Сбросить', width=12,
        )
        self.btn_clear_filter.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_filter()

    def get_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        if roles_filter_dict:
            if roles_filter_dict.get('role_name', ''):
                self.ent_name.insert(0, roles_filter_dict.get('role_name', ''))
            if roles_filter_dict.get('role_description', ''):
                self.txt_description.insert(roles_filter_dict.get('role_description', ''))

    def click_btn_ok(self, event=None):
        """Клик по кнопке Применить, применение фильтров."""
        self.parent.set_filter(self.ent_name.get(),
                               srv.get_text_in_one_line(self.txt_description.get()))
        self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть

    def click_btn_clear_filter(self, event=None):
        """Клик по кнопке Сбросить, очистка фильтров."""
        self.parent.set_filter(None, None)
        self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть


class NewRole(Role):
    """Класс формы добавления новой роли."""
    def __init__(self, main, parent):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Logins

        # ----
        # Окно
        # Свойства
        self.title("Добавить новую роль")

        # Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

    def click_btn_ok(self, event=None):
        """Сохранение новой роли."""
        if self.check_empty() and self.check_exists():  # Проверка на пустые поля и дубль
            self.roles_db.insert_new_role(self.ent_name.get(),
                                          self.txt_description.get())
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateRole(Role):
    """Класс формы обновления роли."""
    def __init__(self, main, parent, id_role):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main        # Main
        self.parent = parent    # Logins
        self.id_role = id_role  # Id роли для обновления

        # ----
        # Окно
        # Свойства
        self.title('Редактировать роль')

        # Добавляем кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=2, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_role_for_update()

    def get_role_for_update(self):
        """Получение и вывода на форму данных роли для обновления."""
        data = self.roles_db.get_role_by_id(self.id_role)
        self.ent_name.insert(0, data[1])
        self.txt_description.insert(data[2])

    def click_btn_ok(self, event=None):
        """Обновление роли."""
        if self.check_empty():  # Проверка на пустые поля
            self.roles_db.update_role_by_id(self.id_role,
                                            self.ent_name.get(),
                                            self.txt_description.get())
            self.btn_cancel.invoke()  # Имитация клика по кнопке закрыть
