from pathlib import Path
import consolemenu as cmenu
from consolemenu.items import FunctionItem, CommandItem, ExitItem, \
     ExternalItem, SelectionItem, SubmenuItem
import fileinput
import sqlite3
import get_answer_module
import sys


# Получить значение параметра в конфигурационном файле
def get_value_settings(val):
    with open('./settings.cfg', 'rt') as file:
        for line in file:
            if line.startswith(f'{val} = '):
                return line[len(f'{val} = '):].strip('\n')


def set_value_settings(key, val):
    with fileinput.input('./settings.cfg', inplace=True) as file:
        for line in file:
            if f'{key} = ' in line:
                print(f'{key} = {val}')
            else:
                print(line, end='')


# Получение пути к файлу db_aes
def get_db_path(aes=True):
##    print('aes', aes)
    if aes:
        path = get_value_settings('db_aes_path')
    else:
        path = get_value_settings('db_path')
    return path


# Проверка на соответствие пути требованиям ОС
# !! Выбранный путь должен сохраняться в конфигурационный файл
def check_is_path(val):
    path = Path(val)
    if path.parent != Path('.') and path.parent.exists():
        return True
    return False


# Проверка существования пути
def check_path_exists(val):
    path = Path(val)
    if path.parent != Path('.') and path.exists():
        return True
    return False


def check_db_valid(path):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    sql_query = """SELECT name FROM sqlite_master
WHERE type='table';"""
    try:
        cursor.execute(sql_query)
    except sqlite3.DatabaseError as err_text:
        print(err_text)
        return False
    else:
        return True


# Открытие/создание БД
def select_db_path():
    text = 'Введите путь к существующему файлу БД'
    variants = check_path_exists
    answer = get_answer_module.get_answer(text, variants)
    db_aes_path = Path(answer)
    # Открыть файл и проверить, является ли он файлом БД
    if answer == 'back':
        return
    elif check_db_valid(db_aes_path):
        # Записать в конфигурационный файл новый путь к БД
        set_value_settings('db_aes_path', db_aes_path)
    else:
        print('Выбранный файл не является файлом БД')


def insert_new_password(cur):
    


# Создание меню 'Открыть или создать БД?'
class MainMenu(cmenu.ConsoleMenu):
    def __init__(self, cur):
        super().__init__(title='Управление паролями')
        self.cur = cur
        new_db_path = FunctionItem("Ввод нового пароля",
                                   function=insert_new_password, should_exit=True)
        self.append_item(new_db_path)
        

    
##    create_dbase = FunctionItem("Создание файла БД", create_db)
    
##    # A CommandItem runs a console command
##    command_item = CommandItem("Run a console command",  "touch hello.txt")
##
##    # A SelectionMenu constructs a menu from a list of strings
##    selection_menu = SelectionMenu(["item1", "item2", "item3"])
##
##    # A SubmenuItem lets you add a menu (the selection_menu above, for example)
##    # as a submenu of another menu
##    submenu_item = SubmenuItem("Submenu item", selection_menu, menu)

    # Once we're done creating them, we just add the items to the menu
    

