# Увеличен номер версии до 3.1

# TODO: При вводе неверного пароля добавить очистку полей и фокус в поле ввода логина

# TODO: Событие GlobalExit переименовать в SaveAndClosed

# TODO: добавить на ESC переход назад с формы списка логинов и остальных, если есть,
#  а также выход из приложения, но с запросом "Вы действительно хотите выйти"
#  ранее не сработало, предполагаю нужен общий класс Main и наследование от него с переопределением метода

# TODO: Добавить запрет удаления, если пользователь не является администратором
#  оставить право на удаление только у админа или создателя сущности

from typing import Any
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb

# Импортируем свои модули
from _classes import StylizedFrame, MainMenuButtons, MyButton
import _service as srv
import _styles as style
import users as users  # Формы пользователей
import roles as roles  # Формы ролей
import users_db as users_db
import companies as companies
import connection_types as connection_types
import connections as connections

# Словарь данных пользователя
# companies_filter_dict = {'user_login': '', 'user_name': ''}
user_auth = {}

# # закрываем на крестик
# def on_closing():
#    if mb.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
#        root.destroy()

title_for_authorization = 'Авторизуйтесь'
title_for_main = 'База подключений'


def authorization(*w, **kw):
    """Процедура отображения окна авторизации."""
    root = tk.Tk()
    root.title(title_for_authorization)
    root.geometry('270x135+400+300')
    root.resizable(False, False)

    app = Authorization(root)
    app.pack()

    root.mainloop()


def main(id_user, user_login, is_admin, role_id, *w, **kw):
    """Процедура отображения окна приложения (после авторизации)."""
    root = tk.Tk()
    root.title(title_for_main + '  ' + user_login)
    root.geometry("700x450+300+200")  # "'ширина' x 'высота'+300+200"
    # root.resizable(False, False)

    app = Main(root, id_user, user_login, is_admin,  role_id)
    app.pack()

    root.mainloop()


class Authorization(StylizedFrame):
    """Класс окна авторизации."""
    def __init__(self, root=None, parent=None):
        super().__init__()
        # Атрибуты
        self.root = root                    # Класс Main
        self.parent = parent                # Класс Logins
        self.roles_db = users_db.RolesDB()  # БД ролей
        self.users_db = users_db.UsersDB()  # БД пользователей

        # ----
        # Окно
        # !ВАЖНО для фона на всю форму
        self.pack(fill=tk.BOTH, expand=True)

        # Функции модального, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # Парамеры для единой стилизации меток для текстовых полей
        self.options_lbl = {'width': 7}
        self.grid_lbl = {'sticky': 'nw', 'padx': 10, 'pady': 10}
        # Парамеры для единой стилизации однострочных текстовых полей
        self.grid_ent = {'sticky': 'we', 'padx': 10}
        # Парамеры для единой стилизации кнопок управления
        self.grid_btn_control = {'sticky': 'we', 'pady': 10, 'padx': 10}

        # Таблица на 3 колонки и 3 строки
        # 1 и 2 строки - метки для подписи в первой колонке, текстовой поле на 2 колонки
        # 3 строка - пусто в первой колонке, кнопки Войти и Отмена во 2 и 3 колонках соответственно

        # 1 Логин
        lbl_login = ttk.Label(
            self, text="Логин", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_login.grid(row=0, column=0, **self.grid_lbl)
        self.ent_login = ttk.Entry(self)
        self.ent_login.grid(row=0, column=1, columnspan=2, **self.grid_ent)
        self.ent_login.focus()
        self.ent_login.bind("<Control-KeyPress>", srv.keys)

        # 2 Пароль
        lbl_password = ttk.Label(
            self, text="Пароль", style=style.LABEL_CAPTION, **self.options_lbl
        )
        lbl_password.grid(row=1, column=0, **self.grid_lbl)
        self.ent_password = ttk.Entry(self, show='*')
        self.ent_password.grid(row=1, column=1, columnspan=2, **self.grid_ent)
        self.ent_password.bind("<Control-KeyPress>", srv.keys)

        # 3 Кнопки
        self.btn_ok = MyButton(
            self,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.login],
            text='Войти', width=10,
        )
        self.btn_ok.grid(row=2, column=1, **self.grid_btn_control)

        self.btn_cancel = MyButton(
            self,
            style_name=style.BUTTON_CONTROL,
            callbacks=[self.exit_without_request],
            text='Отмена', width=10,
        )
        self.btn_cancel.grid(row=2, column=2, **self.grid_btn_control)

        # -------
        # События
        # Привязываем события клавиш на окно
        self.root.bind('<Return>', self.login)                 # Enter
        self.root.bind('<Escape>', self.exit_without_request)  # Esc
        # self.root.bind("<Escape>", lambda event: root.destroy())

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
        return True

    def check_exists(self):
        """
        Проверка существования логина.
        :return: True/False
        """
        data = self.users_db.get_user_login_for_check_auth(self.ent_login.get())
        if data is None:
            mb.showwarning('Предупреждение', 'Логин не найден')
            return False
        return True

    def check_pass(self):
        """
        Проверка пароля.
        :return: True/False
        """
        data = self.users_db.get_password_by_login(self.ent_login.get())
        if srv.compute_md5_hash(self.ent_password.get()) != data:
            mb.showwarning('Предупреждение', 'Пароль не верный')
            return False
        return True

    def login(self, event=None):
        """Попытка авторизации пользователя."""
        # event - это скрытый аргумент, передаваемый в функцию при клике на кнопку.
        # Если не указать его во входном аргументе функции возникает исключение TypeError
        if self.check_empty() and self.check_exists() and self.check_pass():  # Проверки
            user_login = self.ent_login.get()
            id_user = self.users_db.get_user_id_by_login(self.ent_login.get())
            is_admin = self.users_db.get_user_is_admin_by_user_id(id_user)
            id_role = self.roles_db.get_role_id_by_name(self.ent_login.get(), id_user)

            self.btn_cancel.invoke()  # Имитация клика по "Отмена"
            main(id_user, user_login, is_admin, id_role)  # Открываем главное окно

    def exit_without_request(self, event=None):
        """Выхода из приложения без запроса."""
        self.root.destroy()


class Main(StylizedFrame):
    """
    Класс главного окна.
    Для подключения стилей ttk наследуемся от промежуточного класса StylizedFrame,
    который устанавливает набор стилей.
    """
    def __init__(self, root, id_user=None, user_login=None, is_admin=None, id_role=None):
        super().__init__(root)
        # Атрибуты
        self.root = root                    # Главный процесс Tk()
        self.id_user = id_user              # id пользователя
        self.user_login = user_login        # Логин пользователя
        self.is_admin = is_admin            # Признак "администратор"
        self.id_role = id_role              # Id связанной роли
        self.users_db = users_db.UsersDB()  # Подключаем пользователей

        # ----
        # Окно
        # !ВАЖНО для отображения данных на форме
        # Растянуто на весь экран по горизонтали и вертикали
        self.pack(fill=tk.BOTH, expand=True)

        # Функции модального окна, перехватываем фокус до закрытия
        self.grab_set()
        self.focus_set()

        # ------------
        # Главное меню
        self.frm_main_menu = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)  # GROOVE
        self.frm_main_menu.pack(fill=tk.X)  # растянуто горизонтально

        # Словарь параметров для настройки кнопок главного меню
        self.main_menu_button_options = [
            {
                'is_admin': True,
                'image_path': 'img/users.gif',
                'callbacks': [self.open_users],
                'options': {'text': 'Пользователи'},
            },
            {
                'is_admin': True,
                'image_path': 'img/roles.gif',
                'callbacks': [self.open_roles],
                'options': {'text': 'Роли'},
            },
            {
                'is_admin': False,
                'image_path': 'img/companies.gif',
                'callbacks': [self.open_companies],
                'options': {'text': 'Компании'},
            },
            {
                'is_admin': False,
                'image_path': 'img/connection_types.gif',
                'callbacks': [self.open_connection_types],
                'options': {'text': 'Типы доступов'},
            },
            {
                'is_admin': False,
                'image_path': 'img/connections.gif',
                'callbacks': [self.open_connections],
                'options': {'text': 'Доступы'},
            },
        ]

        # Создание кнопок главного меню
        self.main_menu_buttons = MainMenuButtons(
            self.frm_main_menu,
            is_admin=self.is_admin,
            options=self.main_menu_button_options
        )

        # ----------------------------
        # Контент (рамка для контента)
        self.frm_content_all = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.frm_content_all.pack(fill=tk.BOTH, anchor=tk.N, expand=True)

        # -------
        # События
        # Привязываем события клавиш на окно
        self.root.bind('<Escape>', self.exit_with_request)  # Esc, выход с запросом

        self.clear_frm_content_all()  # Чистим блок с контентом

    def clear_frm_content_all(self) -> None:
        """Очистка области (рамки) для ввода данных."""
        for widget in self.frm_content_all.winfo_children():
            widget.destroy()

    def open_users(self, event: Any = None) -> None:
        """Вывод списка пользователей (доступно только для админа)."""
        self.clear_frm_content_all()
        users.Users(self.frm_content_all, self, self.is_admin)

    def open_roles(self, event: Any = None) -> None:
        """Вывод списка ролей (доступно только для админа)."""
        self.clear_frm_content_all()
        roles.Roles(self.frm_content_all, self, self.is_admin)

    def open_companies(self, event: Any = None) -> None:
        """Вывод списка компаний."""
        self.clear_frm_content_all()
        companies.Companies(self.frm_content_all, self, self.is_admin)

    def open_connection_types(self, event: Any = None) -> None:
        """Вывод списка типов подключения."""
        self.clear_frm_content_all()
        connection_types.ConnectionTypes(self.frm_content_all, self)

    def open_connections(self, event: Any = None) -> None:
        """Вывод списка подключений."""
        self.clear_frm_content_all()
        connections.Connections(self.frm_content_all, self, self.is_admin)

    def exit_with_request(self, event: Any = None) -> None:
        """Выхода из приложения с запросом."""
        # self.root.destroy()
        if mb.askokcancel("Выход из приложения", "Хотите выйти из приложения?"):
            self.root.destroy()


if __name__ == '__main__':
    authorization()

    # root = tk.Tk()
    #
    # # # закрываем на крестик
    # # root.protocol("WM_DELETE_WINDOW", on_closing)  # клик по крестику
    #
    # db = db.DB()  # Добавляем класс DB
    # app = Main(root)  # добавляем класс Main
    # # app = users.Authorization(root)
    #

    # app.pack()
    # root.title("База подключений")
    # root.geometry("700x450+300+200")
    # # root.resizable(False, False)
    #
    # # отключил 20210807 (не помню для чего)
    # #root.event_add('<<Paste>>', '<Control-igrave>')
    # #root.event_add("<<Copy>>", "<Control-ntilde>")
    #
    # root.mainloop()
