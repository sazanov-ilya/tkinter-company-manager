from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import Description, PermissionCheckButton, TopMenuButtons, MyButton
import _service as srv
import _styles as style
import users_db as users_db  # БД пользователей


# Словарь фильтров, вынесен из атрибутов класса
# для сохранения фильтров при переходе между окнами
users_filter_dict = {}


class Users(ttk.Frame):
    """Базовый класс формы списка логинов."""
    def __init__(self, root, main, is_admin: bool = None) -> None:
        super().__init__(root)
        # Атрибуты
        self.root = root                    # frm_content_all
        self.main = main                    # Main
        self.is_admin: bool = is_admin      # Признак "администратор"
        self.users_db = users_db.UsersDB()  # БД пользователей
        self.users_list = []                # Список кортежей пользователей

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
                'callbacks': [self.open_role_management],
                'options': {'text': 'Управление ролями', 'width': 20},
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
            'id_user': {
                'displaycolumns': False,
                'column': {'width': 50, 'anchor': tk.CENTER},
                'heading': {'text': 'ID'},
            },
            'user_login': {
                'displaycolumns': True,
                'column': {'width': 100, 'anchor': tk.W},
                'heading': {'text': 'Логин'},
            },
            'user_role': {
                'displaycolumns': True,
                'column': {'width': 70, 'anchor': tk.W},
                'heading': {'text': 'Роль'},
            },
            'user_name': {
                'displaycolumns': True,
                'column': {'width': 150, 'anchor': tk.W},
                'heading': {'text': 'ФИО'},
            },
            'user_description': {
                'displaycolumns': True,
                'column': {'width': 250, 'anchor': tk.W},
                'heading': {'text': 'Описание'},
            },
            'is_deleted': {
                'displaycolumns': True,
                'column': {'width': 40, 'anchor': tk.CENTER},
                'heading': {'text': 'Отк.'},
            },
        }
        # Настраиваем таблицу по словарю
        self.users_table = ttk.Treeview(self.frm_treeview, columns=([key for key in self.columns]),
                                        displaycolumns=(
                                            [key for key in self.columns if self.columns[key]['displaycolumns']]),
                                        **self.treeview_options)
        for key, value in self.columns.items():
            # self.users_table.column("id_user", width=50, anchor=tk.CENTER)
            self.users_table.column(key, **value['column'])
            # self.users_table.heading('id_user', text='ID')
            self.users_table.heading(key, **value['heading'])

        self.users_table.grid(row=0, column=0, sticky='nwse')

        # Полоса прокрутки для таблицы
        scroll = tk.Scrollbar(self.frm_treeview, command=self.users_table.yview)
        scroll.grid(row=0, column=1, sticky='nwse')
        self.users_table.configure(yscrollcommand=scroll.set)

        # Контекстное меню для копирования
        self.context_menu = tk.Menu(self.users_table, tearoff=0)
        self.context_menu.add_command(
            label='Копировать логин', command=self.copy_login)
        self.context_menu.add_command(
            label='Копировать роли', command=self.copy_roles)
        self.context_menu.add_command(
            label='Копировать ФИО', command=self.copy_fio)
        self.context_menu.add_command(
            label='Копировать описание', command=self.copy_description)
        # self.context_menu.add_command(
        #     label='Копировать все', command=self.copy_all)

        # -------------------
        # События для таблицы
        self.users_table.bind('<Double-Button-1>', self.double_click)  # ЛКМ, двойной клик
        self.users_table.bind('<Button-2>', self.select_row)           # СКМ, выделить строку
        self.users_table.bind('<Button-3>', self.show_context_menu)    # ПКМ, контекстное меню

        # Вывод данных
        self.show_users()

    def select_row(self, event=None):
        """Выделение строки в таблице."""
        # Получаем идентификатор строки под курсором
        iid = self.users_table.identify_row(event.y)
        if iid:
            # Выделяем строку под курсором по ее идентификатору
            self.users_table.selection_set(iid)
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
        :return:
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
        """Копирование в буфер обмена логина."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.users_table.set(self.users_table.selection()[0], '#1'))

    def copy_roles(self):
        """Копирование в буфер обмена ролей."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.users_table.set(self.users_table.selection()[0], '#2'))

    def copy_fio(self):
        """Копирование в буфер обмена ФИО."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.users_table.set(self.users_table.selection()[0], '#3'))

    def copy_description(self):
        """Копирование в буфер обмена описания."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.users_table.set(self.users_table.selection()[0], '#4'))

    def copy_all(self):
        """Копирование в буфер обмена строки целиком."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.users_table.set(self.users_table.selection()[0], '#1') + '\n' +
                                   self.users_table.set(self.users_table.selection()[0], '#2') + '\n' +
                                   self.users_table.set(self.users_table.selection()[0], '#3') + '\n' +
                                   self.users_table.set(self.users_table.selection()[0], '#4'))

    def color_btn_filter(self):
        """Смена цвета кнопки Фильтр."""
        # По умолчанию кнопка Фильтр является первым элементом в списке кнопок.
        if users_filter_dict:  # Если есть фильтры
            self.top_menu_buttons[0].configure(style=style.BUTTON_FILTER)
        else:
            self.top_menu_buttons[0].configure(style=style.BUTTON_CONTROL)

    @staticmethod
    def get_filter():
        """Получение текущих значений фильтра."""
        return users_filter_dict

    @staticmethod
    def set_filter(tmp_users_filter_dict):
        """
        Применение фильтра.
        :param tmp_users_filter_dict:
        :return: Нет
        """
        users_filter_dict.clear()  # Чистим словарь
        users_filter_dict.update(tmp_users_filter_dict)

    def show_users(self):
        """Заполнение списка пользователей согласно фильтрам и БД."""
        self.color_btn_filter()  # Цвет кнопки фильтра
        [self.users_table.delete(i) for i in self.users_table.get_children()]  # Чистим таблицу
        self.users_list = self.users_db.get_users_by_filter(users_filter_dict)
        srv.sorted_table(self.users_list)
        [self.users_table.insert('', 'end', values=row) for row in self.users_list]  # Выводим список на форму

    def open_filter(self, event: Any = None) -> None:
        """Отображение окна фильтров."""
        FilterUser(self.main, self)

    def open_new(self, event: Any = None) -> None:
        """Отображение окна для ввода нового пользователя."""
        NewUser(self.main, self)

    def open_update(self, event: Any = None) -> None:
        """Отображение окна обновления выбранного пользователя."""
        if self.users_table.focus() != '':
            # Получаем первую выделенную строку
            item = self.users_table.item(self.users_table.focus())
            user_id = item["values"][0]
            user_login = item["values"][1]
            # Запрет на редактирование базового админа
            if self.users_db.get_user_is_base_admin_by_login(user_login):
                mb.showwarning('Предупреждение', 'Редактирование базового администратора запрещено')
            else:
                UpdateUser(self.main, self, user_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите пользователя в списке')

    def open_delete(self, event: Any = None) -> None:
        """Удаление выбранных пользователей."""
        if self.users_table.focus() != '':
            answer = mb.askyesno(title='Запрос действия',
                                 message="Хотите удалить выбранные элементы?")
            if answer:  # Если Да = True
                ids = []  # Список id выделенных элементов
                # Цикл по всем выделенным элементам
                for selected_item in self.users_table.selection():
                    item = self.users_table.item(selected_item)
                    ids.append(item["values"][0])
                self.users_db.delete_users(ids)  # Удаление данных
                self.show_users()                # Обновляем таблицу
        else:
            mb.showwarning('Предупреждение', 'Выберите пользователя/пользователей')

    def open_role_management(self, event: Any = None) -> None:
        """Отображение окна управление ролями пользователя."""
        if self.users_table.focus() != '':
            # Получаем первую выделенную строку
            item = self.users_table.item(self.users_table.focus())
            user_id = item["values"][0]
            user_login = item["values"][1]
            # Запрет на редактирование базового админа
            if self.users_db.get_user_is_base_admin_by_login(user_login):
                mb.showwarning('Предупреждение', 'Редактирование базового администратора запрещено')
            else:
                UserRoles(self.main, self, user_id)
        else:
            mb.showwarning('Предупреждение', 'Выберите пользователя в списке')


class User(tk.Toplevel):
    """Базовый класс формы пользователя."""
    # TODO: Рассмотреть возможность единого промежуточного класса с формой управления ролями,
    #  для единых настроек параметров виджетов
    def __init__(self, main, parent):
        super().__init__()
        # Атрибуты
        self.main = main                    # Main
        self.parent = parent                # Users
        self.users_db = users_db.UsersDB()  # БД Пользователей
        # Классы-переменные - для связки значений виджетов
        self.is_deleted = tk.BooleanVar()
        self.is_admin = tk.BooleanVar()

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title("Пользователь")
        # self["bg"] = style.FRAME_BG  # Цвет фона формы
        self.geometry('415x320+400+300')
        self.resizable(False, False)

        # Парамеры для единой стилизации меток для текстовых полей
        self.options_lbl = {'width': 10}
        self.grid_lbl = {'sticky': 'nw', 'padx': 10, 'pady': 10}  # lbl_padding
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
        self.frm_main.rowconfigure(5, weight=1)

        # 1 Логин
        self.lbl_login = ttk.Label(self.frm_main, text="Логин", style=style.LABEL_CAPTION, **self.options_lbl)
        self.lbl_login.grid(row=0, column=0, **self.grid_lbl)
        self.ent_login = ttk.Entry(self.frm_main)
        self.ent_login.grid(row=0, column=1, columnspan=4, **self.grid_ent)
        self.ent_login.focus()
        self.ent_login.bind("<Control-KeyPress>", srv.keys)

        # 2 Пароль
        self.lbl_password = ttk.Label(self.frm_main, text="Пароль", style=style.LABEL_CAPTION, **self.options_lbl)
        self.lbl_password.grid(row=1, column=0, **self.grid_lbl)
        self.ent_password = ttk.Entry(self.frm_main)
        self.ent_password.grid(row=1, column=1, columnspan=4, **self.grid_ent)
        self.ent_password.bind("<Control-KeyPress>", srv.keys)

        # 3 Подтверждение пароля (не активно, только для grid)
        self.ent_password2 = ttk.Entry(self.frm_main)

        # 5 Имя
        lbl_name = ttk.Label(self.frm_main, text="Имя", style=style.LABEL_CAPTION, **self.options_lbl)
        lbl_name.grid(row=4, column=0, **self.grid_lbl)
        self.ent_name = ttk.Entry(self.frm_main)
        self.ent_name.grid(row=4, column=1, columnspan=4, **self.grid_ent)
        self.ent_name.bind("<Control-KeyPress>", srv.keys)

        # 6 Описание
        lbl_description = ttk.Label(self.frm_main, text="Описание", style=style.LABEL_CAPTION, **self.options_lbl)
        lbl_description.grid(row=5, column=0, **self.grid_lbl)
        self.txt_description = Description(self.frm_main)
        self.txt_description.grid(row=5, column=1, columnspan=4, **self.grid_txt)

        # 7 Пользователь является администратором, связываем с переменной BooleanVar
        self.check_is_admin = ttk.Checkbutton(self.frm_main,
                                              text='Пользователь является администратором',
                                              style=style.CHECKBUTTON_STYLE,
                                              variable=self.is_admin)
        self.check_is_admin.grid(row=6, column=1, columnspan=4, **self.grid_txt)

        # 8 Признак "Удален", связываем с переменной BooleanVar
        self.check_is_deleted = ttk.Checkbutton(self.frm_main,
                                                text='Признак "удален"',
                                                style=style.CHECKBUTTON_STYLE,
                                                variable=self.is_deleted)
        self.check_is_deleted.grid(row=7, column=1, columnspan=4, **self.grid_txt)

        # 9 Кнопки
        self.btn_cancel = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_cancel],
            text='Отмена', width=12,
        )
        self.btn_cancel.grid(row=8, column=4, **self.grid_btn_control)

        # -------
        # События
        # Виртуальное событие "Сохранить и закрыть окно"
        # Нужно для вызова из текстового поля для перехвата события KeyPress-Return
        self.event_generate('<<GlobalExit>>')  # Не запускает дочернюю привязку события
        self.bind('<<GlobalExit>>', self.click_btn_ok)

        # События клавиш на окно
        self.bind('<Return>', self.click_btn_ok)      # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

    def click_btn_ok(self, event=None):
        """Клик по кнопке Ok (Применить/Обновить и т.п.)."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        # Заглушка, для создания события, реальная процедура в наследующем классе
        pass

    def click_btn_cancel(self, event=None):
        """Клик по кнопке Отмена."""
        self.parent.show_users()  # Обновляем таблицу-список
        self.destroy()

    def check_empty(self):
        """
        Проверка на пустые поля формы.
        :return: True/False
        """
        if len(self.ent_login.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите логин')
            return False
        elif len(self.ent_password.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите пароль')
            return False
        elif len(self.ent_name.get()) == 0:
            mb.showwarning('Предупреждение', 'Введите имя')
            return False
        return True

    def check_exists(self):
        """
        Проверка на дубль логина.
        :return: True/False
        """
        data = self.users_db.get_user_login_for_check_exists(self.ent_login.get())
        if data:
            mb.showwarning('Предупреждение', 'Логин <' + data + '> уже используется')
            return False
        return True


class FilterUser(User):
    """Класс формы добавления нового пользователя."""
    def __init__(self, main, parent):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main  # Main
        self.parent = parent  # Users

        # ----
        # Окно
        self.title("Фильтр списка пользователей")

        # Блокируем ненужные виджеты
        self.lbl_password.configure(state="disabled")  # normal, readonly и disabled
        self.ent_password.configure(state="disabled")  # normal, readonly и disabled
        self.check_is_admin.configure(state="disabled")  # normal, readonly и disabled
        self.check_is_deleted.configure(state="disabled")  # normal, readonly и disabled

        # 7 Кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Применить', width=12,
        )
        self.btn_ok.grid(row=8, column=2, **self.grid_btn_control)

        self.btn_clear = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_clear],
            text='Сбросить', width=12,
        )
        self.btn_clear.grid(row=8, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_filter()
        # TODO: Создать атрибуты класса как StringVar, который связать с виджетами формы

    def get_filter(self):
        """Получение текущих значений фильтров и вывод значений на форму."""
        tmp_users_filter_dict = {}
        tmp_users_filter_dict.update(self.parent.get_filter())

        if tmp_users_filter_dict:
            if tmp_users_filter_dict.get('user_login', ''):
                self.ent_login.insert(0, tmp_users_filter_dict.get('user_login', ''))
            if tmp_users_filter_dict.get('user_name', ''):
                self.ent_name.insert(0, tmp_users_filter_dict.get('user_name', ''))
            if tmp_users_filter_dict.get('user_description', ''):
                self.txt_description.insert(tmp_users_filter_dict.get('user_description', ''))

    def click_btn_ok(self, event=None):
        """Применение фильтров, клик по кнопке Применить."""
        tmp_users_filter_dict = {}
        if len(self.ent_login.get()) > 0:
            tmp_users_filter_dict['user_login'] = self.ent_login.get()
        if len(self.ent_name.get()) > 0:
            tmp_users_filter_dict['user_name'] = self.ent_name.get()
        if len(srv.get_text_in_one_line(self.txt_description.get())) > 0:
            tmp_users_filter_dict['user_description'] = srv.get_text_in_one_line(
                self.txt_description.get())

        self.parent.set_filter(tmp_users_filter_dict)
        self.btn_cancel.invoke()  # Имитация клика по кнопке "Закрыть"

    def click_clear(self, event=None):
        """Очистка фильтров, клик по кнопке Сбросить."""
        self.parent.set_filter({})
        self.btn_cancel.invoke()  # Имитация клика по кнопке "Закрыть"


class NewUser(User):
    """Класс формы добавления нового пользователя."""
    def __init__(self, main, parent):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main      # Main
        self.parent = parent  # Users

        # ----
        # Окно
        self.title("Добавить нового пользователя")

        # Блокируем список ролей и галочку
        self.check_is_deleted.configure(state="disabled")  # normal, readonly и disabled

        # 7 Кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Сохранить', width=12,
        )
        self.btn_ok.grid(row=8, column=3, **self.grid_btn_control)

    def click_btn_ok(self, event=None):
        """Сохранение нового пользователя."""
        if self.check_empty() and self.check_exists():  # Проверка на пустые поля и дубль
            self.users_db.save_new_user(self.ent_login.get(),
                                        self.ent_password.get(),
                                        self.ent_name.get(),
                                        self.txt_description.get(),
                                        self.is_admin.get())
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UpdateUser(User):
    """Класс формы обновления пользователя."""
    def __init__(self, main, parent, id_user):
        super().__init__(main, parent)
        # Атрибуты
        self.main = main        # Main
        self.parent = parent    # Users
        self.id_user = id_user  # Id пользователя

        # ----
        # Окно
        self.title('Обновить пользователя: ' + self.users_db.get_user_login_by_id(id_user))

        # 7 Кнопки
        self.btn_ok = MyButton(
            self.frm_main,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_ok],
            text='Обновить', width=12,
        )
        self.btn_ok.grid(row=8, column=3, **self.grid_btn_control)

        # Выводим данные
        self.get_user_for_update()

    def get_user_for_update(self):
        """Получения и вывода на форму данных пользователя для обновления."""
        user_data = self.users_db.get_user_by_id(self.id_user)  # Получает данные пользователя
        # Выводим значения в поля формы
        self.ent_login.insert(0, user_data[1])
        self.ent_password.insert(0, '*')
        self.ent_name.insert(0, user_data[3])
        self.txt_description.insert(user_data[4])
        self.is_admin.set(user_data[5])    # Галочка is_admin
        self.is_deleted.set(user_data[6])  # Галочка is_deleted

    def click_btn_ok(self, event=None):
        """Обновление пользователя."""
        if self.check_empty():  # Проверка на пустые поля
            self.users_db.update_user_by_id(self.id_user,
                                            self.ent_login.get(),
                                            self.ent_password.get(),
                                            self.ent_name.get(),
                                            self.txt_description.get(),
                                            self.is_admin.get(),   # Галочка is_admin
                                            self.is_deleted.get()  # Галочка is_deleted
                                            )
            self.btn_cancel.invoke()  # Имитация клика по "Отмена"


class UserRoles(tk.Toplevel):
    """Класс формы управления назначением ролей пользователю."""
    def __init__(self, main, parent, id_user):
        super().__init__()
        # Атрибуты
        self.main = main                            # Main
        self.parent = parent                        # Users
        self.users_db = users_db.UsersDB()          # БД Пользователей
        self.users_roles = users_db.UsersRolesDB()  # БД роли-пользователей
        self.roles_db = users_db.RolesDB()          # БД ролей
        self.id_user = id_user                      # Id пользователя
        self.roles_list = self.roles_db.get_role_list_for_user_roles(self.id_user)  # Кортеж ролей пользователя
        self.checks = []  # Список объектов "Галочка" с ролями пользователей

        # ----
        # Окно
        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Свойства
        self.title('Управление ролями: ' + self.users_db.get_user_login_by_id(id_user))
        self.width = 415
        self.height = 350
        self.posx = 400
        self.posy = 300
        self.geometry("%dx%d+%d+%d" % (self.width, self.height, self.posx, self.posy))
        self.resizable(False, False)

        # TODO: Вынести общие параметры виджетов, по возможности переделать ввод на grid
        # Общая рамка
        self.frm_main = ttk.Frame(self)
        self.frm_main.pack(fill=tk.BOTH, expand=True)

        # Резиновая ячейка для Canvas
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

        # Резиновая ячейка
        frm_canvas.columnconfigure(0, weight=1)
        frm_canvas.rowconfigure(0, weight=1)

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
        self.frm_permission.bind("<Enter>", self._bound_to_mousewheel)
        self.frm_permission.bind("<Leave>", self._unbound_to_mousewheel)
        # Маштабирование при изменении размера
        self.frm_permission.bind('<Configure>', self._on_configure)
        # Изменения размеров вложенного frame
        self.canvas.bind("<Configure>", self._on_resize_canvas)

        # ------------------------------
        # Нижний toolbar (третья строка)
        self.frm_bottom_toolbar = ttk.Frame(self.frm_main, relief=tk.RAISED, borderwidth=0)
        self.frm_bottom_toolbar.grid(row=2, column=0, sticky="nesw")

        self.btn_cancel = MyButton(
            self.frm_bottom_toolbar,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.click_btn_cancel],
            text='Отмена', width=12,
        )
        self.btn_cancel.pack(side=tk.RIGHT, pady=10, padx=10)

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
        self.bind('<Return>', self.click_btn_ok)  # Enter
        self.bind('<Escape>', self.click_btn_cancel)  # Esc

        # Выводим данные
        self.show_permission()

    def _on_resize_canvas(self, event):
        canvas_width, canvas_height = event.width - 5, event.height - 5
        # Ширина внутренней рамки по ширине canvas
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Высота внутренней рамки по высоте canvas, если ролей недостаточно для полной высоты
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
        Обработка события выхода курсора мыши из области canvas.
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
        for iter in range(len(self.roles_list)):
            self.checks.append(PermissionCheckButton(self.frm_permission,
                                                     iter,
                                                     self.roles_list[iter][0],
                                                     self.roles_list[iter][1],
                                                     self.roles_list[iter][2],
                                                     self.roles_list[iter][3]))

    def clear_frm_permission(self):
        """Очистка формы со списком ролей."""
        for widget in self.frm_permission.winfo_children():
            # widget.pack_forget()
            widget.destroy()

    def apply_filter(self, event=None):
        """
        Клик по кнопке Применить фильтр,
        применение фильтрации по введенной строке.
        :return: Нет
        """
        self.clear_frm_permission()  # Чистим форму с ролями
        self.roles_list = []         # и список ролей
        if len(self.ent_filter.get()) == 0:
            self.roles_list = self.roles_db.get_role_list_for_user_roles(self.id_user)
        else:
            self.roles_list = self.roles_db.get_role_list_for_user_roles_by_like_role_name(self.id_user,
                                                                                           self.ent_filter.get())
        self.show_permission()  # Перезаполняем список ролей

    def click_btn_ok(self, event=None):
        """
        Клик по кнопке Сохранить, применение назначенных прав.
        :return: Нет
        """
        for check in self.checks:
            if self.roles_list[check.iter][3] != check.permission.get():  # Если значение изменилось
                if check.permission.get():  # На True
                    # print('Изменен элемент № ' + str(check.iter) + ' Добавлена роль ' + check.role_name)
                    self.add_role_for_user(check.id_role)  # Добавляем права
                else:
                    # print('Изменен элемент № ' + str(check.iter) + ' Удалена роль ' + check.role_name)
                    self.delete_role_for_user([check.id_permission])  # Удаляем права
        self.parent.show_users()  # Обновляем таблицу пользователей
        self.btn_cancel.invoke()  # Имитация клика по "Отмена"

    def click_btn_cancel(self, event=None):
        """Нажатие кнопки Отмена, закрываем окно."""
        self.destroy()

    def add_role_for_user(self, id_role):
        """Добавления прав на новую роль."""
        self.users_roles.save_new_user_role(self.id_user, id_role)

    def delete_role_for_user(self, id_users_roles):
        """Удаление прав с роли."""
        self.users_roles.delete_user_roles(id_users_roles)
