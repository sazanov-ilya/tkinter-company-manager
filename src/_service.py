import ctypes
import re
import hashlib


def sorted_table(lst: list) -> None:
    """
    Сортировка полученного через параметр списка кортежей
    по второму элементу из кортежа (по умолчанию должно быть наименование).
    :param lst: Сортируемый список.
    :return: None
    """
    lst.sort(key=lambda x: x[1])


def get_text_in_one_line(text):
    """ Процедура получения текста в одну строку """
    return re.sub('[\n]', ' ', text).strip()


def get_text_without_start_end_enters(text):
    return text.strip('[\n]')


def compute_md5_hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


# Для Copy-Paste в раскладке RU
def is_ru_lang_keyboard():
    """ Проверка текущей раскладки ввода на RU """
    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    return hex(pf(0)) == '0x4190419'


# Для Copy-Paste в раскладке RU
def keys(event):
    """ Определяем метод keys() с учетом раскладки """
    if is_ru_lang_keyboard():
        if event.keycode == 86:
            event.widget.event_generate("<<Paste>>")
        if event.keycode == 67:
            event.widget.event_generate("<<Copy>>")
        if event.keycode == 88:
            event.widget.event_generate("<<Cut>>")
        if event.keycode == 65535:
            event.widget.event_generate("<<Clear>>")
        if event.keycode == 65:
            event.widget.event_generate("<<SelectAll>>")