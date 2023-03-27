from common import *
import crypta_
from cmenu_ import *
from pathlib import Path
import sqlite3
import get_answer_module
import sys
import keyboard
import fileinput


def main_menu():
    title = 'Основное меню'
    prologue = 'Внесение / изменение / удаление записей о паролях'
    data_modification_menu = CMenu(title, prologue)
    data_modification_menu.add_item(CMenuItem('Выборка записей из БД',
                                           1, select_db_path))
    data_modification_menu.add_item(CMenuItem('Создать новый файл БД',
                                           2, create_db))
    data_modification_menu.show()





###################
## NEW FUNCTIONS ##
###################

# Вызов меню 'Открыть/выбрать файл БД'
# USES
def open_create_db():
    # Вызвать меню создания/открытия файла БД
    title = 'Открыть/выбрать файл БД'
    prologue = 'Внимание! Файл зашифрованной БД не найден!'
    menu_open_create_db = CMenu(title, prologue)
    menu_open_create_db.add_item(CMenuItem('Открыть существующий файл БД',
                                           1, select_db_path))
    menu_open_create_db.add_item(CMenuItem('Создать новый файл БД',
                                           2, create_db))
    menu_open_create_db.show()


# (4) Подключение к фБД_расш
# import: sqlite3
# USES
def db_connect(dbase_path):
    # (4) Открыть файл БД
    # in: <dbase_path>
    connection = sqlite3.connect(dbase_path)
    cursor = connection.cursor()
    # Проверить БД на корректность
    sql_query = """SELECT name FROM sqlite_master
WHERE type='table';"""
    cursor.execute(sql_query)
    # out: <connection>, <cursor>
    return connection, cursor


# (3, 4)
# import: crypta_, sqlite3
# USES
def db_decrypt_and_connect(db_aes_path):
    # (3) Расшифровать фБД
    # in: <db_aes_path>
    db_decrypted_path = db_aes_path.with_stem(db_aes_path.stem +
                                              '_decrypted')
    crypta_.decrypt_file(db_aes_path, db_decrypted_path)
    # out: <db_decrypted_path>

    # (4) Открыть файл БД
    # in: <db_decrypted_path>
    connection, cursor = db_connect(db_decrypted_path)
    # out: <connection>, <cursor>
    return connection, cursor


# (2, 3, 4)
# import: common, crypta_, sqlite3
# USES
def from_get_path_to_open_db(config_file):
    # (2) Получить путь фБД из конф.файла
    # in: <config_file>
    ## Отфильтровать строку с ключом пути фБД
    selection = list(filter(lambda line: line.startswith
                            (CF_DB_AES_PATH_KEY),
                            config_file.read().split('\n')))
    db_aes_path_str = selection[0][len(CF_DB_AES_PATH_KEY)
                                   :].strip(' \n\t=')
    db_aes_path = Path(db_aes_path_str)
    # (3, 4) Расшифровать фБД и открыть его
    # in: <db_aes_path>
    connection, cursor = db_decrypt_and_connect(db_aes_path)
    # out: <connection>, <cursor>
    # Реализовать: Открытие основн.меню
    return connection, cursor


# (1, 2, 3, 4)
# import: common, crypta_, sqlite3
# USES
def open_db_from_read_settings(config_file_path):
    # (1) Открыть конф.файл
    # in: <config_file_path>
        with open(config_file_path, 'r') as config_file:
        # (2, 3, 4) Получить путь фБД из конф.файла
        # in: <config_file>
            connection, cursor = from_get_path_to_open_db(config_file)
        # out: <connection>, <cursor>
        return connection, cursor


# Проверка существования пути
# USES
def check_path_exists(val):
    path = Path(val)
    if path.parent != Path('.') and path.exists():
        return True, ''
    return False, 'Путь не существует или пуст'


# Выбор файла БД для открытия
# USES
def select_db_path():
    text = 'Введите путь к существующему файлу БД'
    # Функция проверки ответа на существование пути и не '.'
    variants = check_path_exists
    # Запрос ответа
    answer = get_answer_module.get_answer(text, variants)
    # Открыть файл и проверить, является ли он файлом БД
    if answer == 'back':
        return
    # Если фБД для открытия выбран
    else:
        db_aes_path = Path(answer)
        try:
            db_decrypt_and_connect(db_aes_path)
        except ValueError as error:
        # (3) Не найден фБД_зашифр
            if error.args[0] in ('Unable to read input file.',
                                 "WindowsPath('.') has an empty name"):
                print(CF_DB_AES_PATH_VAL_ERROR[0])
                # Создать / выбрать фБД
                print(CF_DB_AES_PATH_VAL_ERROR[1])
                open_create_db()
        # (3) Введен неверный пароль
            if error.args[0] == 'Wrong password (or file is corrupted).':
                print(DB_AES_PASSWORD_ERROR[0])
                print(DB_AES_PASSWORD_ERROR[1])
                
        except sqlite3.OperationalError as error:
        # (4) фБД_дешифр не может быть прочитан
            if error.args[0] == 'unable to open database file':
                print(DB_SQLITE3_ERROR[0])
                # Создать / выбрать фБД / ввести пароль повторно
                print(DB_SQLITE3_ERROR[1])
                open_create_db()
        except sqlite3.DatabaseError as error:
        # (4) фБД_дешифр не может быть прочитан
            if error.args[0] == 'file is not a database':
                print(DB_SQLITE3_ERROR[0])
                # Создать / выбрать фБД / ввести пароль повторно
                print(DB_SQLITE3_ERROR[1])
                open_create_db()
        else:
            print('норм.')
            set_value_settings(CF_DB_AES_PATH_KEY, db_aes_path)


# Создание БД
def create_db():
    # Ввод папки для сохранения БД
    text = 'Введите путь к существующей папке'
    variants = check_path_exists
    answer = get_answer_module.get_answer(text, variants)
    db_aes_folder_path = Path(answer)

    # Ввод имени файла для сохранения БД
    text = 'Введите имя файла без расширения'
    # Проверить на не существование файла, проверить на отсутствие расширения и пустоту


    def check_name(name):
        return check_path_name_to_create(db_aes_folder_path, name)


    variants = check_name
    answer = get_answer_module.get_answer(text, variants)
    db_aes_path = (db_aes_folder_path / answer).with_suffix('.sqlite')
    
    # Выход
    if answer == 'back':
        return
    # Проверка соответствия файла БД формату 'sqlite3'
    elif check_name_repeat(db_aes_path):
        # Записать в конфигурационный файл новый путь к БД
        set_value_settings('db_aes_path', db_aes_path)
    else:
        print('Выбранный файл не является файлом БД')



###################
## OLD FUNCTIONS ##
###################


# Получить значение параметра в конфигурационном файле
def get_value_settings(val):
    with open(f'./{CF_DB_AES_PATH_KEY}', 'rt') as file:
        for line in file:
            if line.startswith(f'{val} = '):
                return line[len(f'{val} = '):].strip()


def set_value_settings(key, val):
    with fileinput.input('./settings.cfg', inplace=True) as file:
        for line in file:
            if line.startswith(f'{key} = '):
                print(f'{key} = {val}')
            else:
                print(line, end='')


# Проверка на соответствие пути требованиям ОС
# !! Выбранный путь должен сохраняться в конфигурационный файл
def check_is_path(val):
    path = Path(val)
    if path.parent != Path('.') and path.parent.exists():
        return True
    return False

