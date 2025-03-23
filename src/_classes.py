from tkinter import ttk
import tkinter as tk

# Импортируем свои модули
import _service as srv  # Общие процедуры
import _styles as style


class StylizedFrame(ttk.Frame):
    """
    Класс для установки стилей ttk.
    Наследуемся от него один раз при создании главной рамки формы для установки стилей.
    """

    def __init__(self, root=None, **kwargs):
        super().__init__(root, **kwargs)

        # ---------------
        # Тема оформления
        self.style = ttk.Style(root)
        self.style.theme_use(style.STYLE_THEME_USE)

        # -------------------------------
        # Фон по умолчанию для всех Frame
        self.style.configure(
            'TFrame',
            background=style.FRAME_BG
        )

        # --------------------
        # Кнопка главного меню
        self.style.configure(  # Статические параметры
            style.BUTTON_MAIN_MENU,
            width=20,            # Ширина кнопки по умолчанию
            compound=tk.BOTTOM,  # Текст над картинкой
            # focuscolor='',     # Отключаем пунктирную рамку для focus
        )
        self.style.map(  # Динамические параметры
            style.BUTTON_MAIN_MENU,
            foreground=[('disabled', 'black')],  # ('active', '!disabled', '#A9A9A9')
            font=[('disabled', 'underline')],
            background=[
                ('active', style.BUTTON_BG_ACTIVE),
                ('pressed', style.BUTTON_BG_ACTIVE),
                ('disabled', style.BUTTON_BG_ACTIVE)
            ]
        )

        # --------------------
        # Кнопка управления
        self.style.configure(  # Статические параметры
            style.BUTTON_CONTROL,
            width=12,       # Ширина кнопки по умолчанию
            focuscolor='',  # Отключаем пунктирную рамку для focus
        )
        self.style.map(  # Динамические параметры
            style.BUTTON_CONTROL,
            # background=[
            #     ('active', style.BUTTON_BG_ACTIVE),
            #     ('pressed', style.BUTTON_BG_ACTIVE),
            # ]
        )

        # --------------------
        # Кнопка фильтра при наличии фильтра
        self.style.configure(  # Статические параметры
            style.BUTTON_FILTER,
            background=[style.BUTTON_BG_ACTIVE],
            width=12
        )
        self.style.map(  # Динамические параметры
            style.BUTTON_FILTER,
            background=[
                ('active', style.BUTTON_BG_ACTIVE),
                ('pressed', style.BUTTON_BG_ACTIVE),
            ]
        )

        # -------------------------
        # Метка для текстового поля
        self.style.configure(  # Статические параметры
            style.LABEL_CAPTION,
            background=style.FRAME_BG  # padding=6, relief="flat",
        )
        self.style.map(  # Динамические параметры
            style.LABEL_CAPTION,
            background=[
                ('active', style.FRAME_BG,),
                ('disabled', style.FRAME_BG,)
            ]
        )

        # -------------------
        # Галочка Checkbutton
        self.style.configure(  # Статические параметры
            style.CHECKBUTTON_STYLE,
            background=style.FRAME_BG  # padding=6, relief="flat",
        )
        self.style.map(  # Динамические параметры
            style.CHECKBUTTON_STYLE,
            background=[
                ('active', style.FRAME_BG,),
                ('disabled', style.FRAME_BG,)
            ]
        )

        # --------------------------------------
        # !ВАЖНО для отображения данных на форме
        # Растянуто горизонтально с параметрами fill и expand
        self.pack(fill=tk.BOTH, expand=True)


class MyButton(ttk.Button):
    """
    Класс объекта кнопки.
    Позволяет устанавливать отдельные стили на кнопки,
    а также вешать на кнопку несколько процедур.
    """

    def __init__(
            self,
            parent: ttk.Frame,
            index: int = None,
            style_name: str = None,
            image_path: str = None,
            callbacks: list = None,
            **kwargs
    ) -> None:
        """
        :param parent: Frame, на который выводим кнопку
        :param index: Индекс кнопки в списке
        :param style_name: Наименование стиля
        :param image_path: Путь до картинки для кнопки
        :param callbacks: Список функций обратного вызова
        :param button_option: Словарь с настройками кнопки
        """

        self.index: int = index
        self.style_name: str = style_name
        self.image_path: str = image_path
        self.callbacks: list = callbacks

        # Создаем картинку для кнопки
        self.image = None
        if self.image_path:
            self.image = tk.PhotoImage(file=self.image_path)
        # Создаем кнопку
        super().__init__(
            parent, style=self.style_name, image=self.image,  command=self.button_click, **kwargs
        )

    def button_click(self) -> None:
        """
        Последовательный вызов функций обратного вызова по списку,
        с передачей в нее объекта нажатой кнопки (в callback функциях
        обязательно должен приниматься параметр event=None,
        в который будет возвращаться объект нажатой кнопки).
        :return: ttk.Button (объект нажатой кнопки)
        """
        for func in self.callbacks:
            func(self)


class MainMenuButtons:
    """
    Класс списка кнопок главного меню.
    Хранит список объектов кнопок главного меню для общих настроек и
    действий над всеми кнопками меню одновременно:

    - при клике на кнопку блокирует ее и снимает блокировку со всех остальных кнопок меню.
    """

    def __init__(self, parent: ttk.Frame, is_admin: bool, options: list) -> None:
        """
        :param parent: Frame, на котором создаются кнопки
        :param is_admin: Признак "администратор"
        :param options: Словарь с настройками для кнопки
        """

        self.parent: ttk.Frame = parent
        self.is_admin: bool = is_admin
        self.options: list = options

        self.checks = []  # Массив кнопок меню
        for index in range(len(self.options)):
            if self.is_admin or not self.options[index]['is_admin']:

                # Добавляем callback класса MainMenuButtons на кнопку
                self.options[index]['callbacks'].insert(0, self.button_click)

                # Добавляем общие настройки
                self.options[index]['options']['takefocus'] = False  # Отключаем фокус

                # Создаем кнопку
                menu_button = MyButton(
                    self.parent,
                    index=index,
                    style_name=style.BUTTON_MAIN_MENU,
                    image_path=self.options[index]['image_path'],
                    callbacks=self.options[index]['callbacks'],
                    **self.options[index]['options'],
                )
                menu_button.grid(row=0, column=index)
                # Добавляем кнопку в массив
                self.checks.append(menu_button)

    def button_click(self, button: ttk.Button = None) -> None:
        """
        Процедура обратного вызова, передаваемая в параметр command кнопки.
        :param button: Нажатая кнопка из массива.
        :return: Нет.
        """
        # Снимаем блокировку со всех кнопок
        for btn in self.checks:
            btn.configure(state="normal")  # normal, readonly и disabled
        # И блокируем нажатую кнопку
        button.configure(state="disabled")


class TopMenuButtons:
    """
    Класс списка кнопок верхнего меню.
    Хранит список объектов кнопок верхнего меню для общих настроек и
    действий над всеми кнопками меню одновременно.
    """

    def __init__(self, parent: ttk.Frame, is_admin: bool, options: list) -> None:
        """
        :param parent: Frame, на котором создаются кнопки
        :param is_admin: Признак "администратор"
        :param options: Словарь с настройками для кнопки
        """

        self.parent: ttk.Frame = parent
        self.is_admin: bool = is_admin
        self.options: list = options

        self.buttons = []  # Массив кнопок
        for index in range(len(self.options)):
            if self.is_admin or not self.options[index]['is_admin']:
                # # Резиновая ячейка,
                # # кнопки динамически растягиваются на весь экран
                # parent.columnconfigure(index, weight=1)

                # Добавляем общие настройки
                self.options[index]['options']['takefocus'] = False  # Отключаем фокус

                # Парамеры для единой стилизации кнопок управления
                self.grid_btn = {'sticky': 'we', 'pady': 10, 'padx': 7}

                # Создаем кнопку
                menu_button = MyButton(
                    self.parent,
                    index=index,
                    style_name=style.BUTTON_CONTROL,
                    callbacks=self.options[index]['callbacks'],
                    **self.options[index]['options'],
                )
                menu_button.grid(row=0, column=index, **self.grid_btn)
                # Добавляем кнопку в массив
                self.buttons.append(menu_button)

    def __getitem__(self, item: int) -> ttk.Button:
        """
        Возвращает объект кнопки из списка по ее индексу.
        :param item: Индекс кнопки в списке.
        :return: Объект кнопки ttk.Button.
        """
        if not isinstance(item, int):
            raise TypeError("Индекс должен быть целым числом")

        if 0 <= item < len(self.buttons):
            return self.buttons[item]
        else:
            raise IndexError("Неверный индекс")


class PermissionCheckButton:
    """Класс объекта галочка для списка ролей."""
    def __init__(self, parent, iter, id_role, role, id_permission, permission):
        """
        :param parent: Класс родительского виджета
        :param iter: Порядковый номер
        :param id_role: Id роли
        :param role: Наименование роли
        :param id_permission: Id связи
        :param permission: Признак 1/0 (есть или нет галочка)
        """
        self.permission = tk.BooleanVar()
        self.iter = iter
        self.id_role = id_role
        self.role = role
        self.id_permission = id_permission
        self.permission.set(permission)  # Устанавливаем значение
        self.cb = ttk.Checkbutton(
            parent, text=self.role, variable=self.permission, style=style.CHECKBUTTON_STYLE, onvalue=1, offvalue=0
        )
        self.cb.grid(row=self.iter, column=0, sticky='w', pady=3, padx=10)


class Description(tk.Frame):
    """Класс многострочного текстового поля с полосой прокрутки."""
    def __init__(self, master):
        super().__init__(master)

        # Резиновая ячейка для текстового поля
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Текстовое поле
        self.txt_description = tk.Text(self)
        self.txt_description.grid(row=0, column=0, sticky='nwse')
        self.txt_description.bind("<Control-KeyPress>", srv.keys)

        # Полоса прокрутки
        scroll = tk.Scrollbar(self, command=self.txt_description.yview)
        scroll.grid(row=0, column=1, sticky='nwse')
        self.txt_description.configure(yscrollcommand=scroll.set)

        # Привязываем события клавиш на текстовое поле
        # Нажать Enter
        # self.txt_description.bind('<Return>', self.bind_return)
        self.txt_description.bind('<KeyPress-Return>', self.bind_key_press_return)
        # # Отпустить Enter
        # self.txt_description.bind('<KeyRelease-Return>', self.bind_key_release_return)

        # Нажать Shift+Enter
        self.txt_description.bind('<Shift-KeyPress-Return>', self.bind_shift_key_press_return)
        # # Отпустить Shift+Enter
        # self.txt_description.bind('<Shift-KeyRelease-Return>', self.bind_shift_key_release_return)

        # # Отключить событие Return, но тогда оно не проходит и на форму уровня выше
        # self.txt_description.bind('<Return>', lambda e: 'break')

        # self.txt_description.bind('<Control-Return>', lambda event: self.txt_description.insert("end", '\n'))
        # self.txt_description.bind('<Control-Return>', self.bind_control_return)  # Ctrl+Enter

    def get(self):
        """ Процедура получения данных из текстового поля """
        # return self.txt_description.get('1.0', tk.END)
        # Удаляем все лишние символы с обоих концов строки
        return srv.get_text_without_start_end_enters(self.txt_description.get('1.0', tk.END))

    def insert(self, text):
        """ Процедура вывода данных в текстовое поле """
        self.txt_description.insert(1.0, text)

    def disabled(self):
        """ Процедура блокирования текстового поля """
        self.txt_description.configure(state="disabled")  # normal, readonly и disabled

    def bind_key_press_return(self, event=None):
        """ Процедура события KeyPress-Return """
        # Подменяем на глобальное событие для сохранения и закрытия окна
        # Чтобы в текстовом поле прервать событие для перехода на новую строку
        self.event_generate('<<GlobalExit>>')  # triggers the root binding

        # Не работает
        # pass
        # # Не отключает срабатывание
        # self.txt_description.bind('<Return>', lambda e: 'break')
        # # Если полностью отключить, то и на форме не работает
        # return 'break'
        # # Не работает
        # self.txt_description.unbind('<KeyPress-Return>')

    def bind_shift_key_press_return(self, event=None):
        """ Процедура события Shift-KeyPress-Return """
        # # Не понял работает или нет
        # self.txt_description.unbind('<KeyPress-Return>')
        # self.txt_description.unbind('<KeyRelease-Return>')

        # Начальный текст
        text_begin = self.txt_description.get('1.0', self.txt_description.index(tk.INSERT))
        # Окончание текста с удалением начальных и конечных переносов строки
        text_end = srv.get_text_without_start_end_enters(
            self.txt_description.get(self.txt_description.index(tk.INSERT), tk.END)
        )

        self.txt_description.delete('1.0', tk.END)                    # Чистим поле
        self.txt_description.insert(tk.INSERT, text_begin)            # Выводим начало текста
        self.txt_description.insert(tk.INSERT, '\n')                  # Добавляем перенос строки
        list_index = self.txt_description.index('insert').split('.')  # Сохраняем в словарь позицию курсора
        self.txt_description.insert(tk.INSERT, text_end)              # Выводим окончание текста
        self.txt_description.mark_set("insert", "%d.%d" % (int(list_index[0]), int(list_index[1])))  # Смещаем курсор

        # !!! Нужно, чтобы не сработало сохранение и форма не закрылась
        # Сохранение через виртуальное событие GlobalExit основного окна
        return 'break'

