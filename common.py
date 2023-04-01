from pathlib import Path
import re
import pyAesCrypt
import getpass
import sqlite3
import traceback
import fileinput
import os
from cmenu_ import *


CF_EXISTS_ERROR = ('Конфигурационный файл "settings.cfg" не найден',
                   'Конфигурационный файл "settings.cfg" создан')
CF_DB_AES_PATH_KEY_ERROR = ('Ключ пути к файлу БД не найден',
                        'Пустой ключ пути к файлу БД помещен в' + \
                        ' конфигурационный файл')
CF_DB_AES_PATH_VAL_ERROR = ('Не найден фБД_зашифр или ключ - пустой',
                            'Запущено меню создания / открытия файла БД')
DB_AES_PASSWORD_ERROR = ('Введен неверный пароль от файла БД',
                     'Будет выполнена повторная попытка открытия файла БД')
DB_SQLITE3_ERROR = ('БД не может быть прочитана',
                    'Запущено меню создания / открытия файла БД')

SELECT_DB_AES_PATH_ERRORS = ('Вы ввели пустой путь',
                             'Введенный путь не существует',
                             'Введенный путь не является папкой')

DB_LOAD_STAGES_MESSAGES = [CF_EXISTS_ERROR, CF_DB_AES_PATH_KEY_ERROR,
                           CF_DB_AES_PATH_VAL_ERROR, DB_AES_PASSWORD_ERROR,
                           DB_SQLITE3_ERROR]

RESTRICTED_PATH_SYMBOLS = set("'*+,;<=>?[]|«")


def say_my_name():
    stack = traceback.extract_stack()
    print('Print from {}'.format(stack[-2][2]))


def app_message(title_type, *args, **kwargs):
    if title_type == 'app':
        title = 'Pass Vault'
    elif title_type == 'db':
        title = 'Pass Vault - Data Base'
    title_marked = title.rjust(79 // 2 + len(title) // 2,
                                  '-').ljust(79, '-')
    print(title_marked)
    # args = ['' + str(arg) for arg in args]
    print(*args, **kwargs, end='\n\n')


def path_checks_carried(*checks):
    def func(path_str):
        return path_checks(path_str, checks)
    return func


''' Проверка пути'''
# def check_is_dir_not_empty_str(path_str, checks):
def path_checks(path_str, checks):
    path = Path(path_str)
    # Если путь - пустой, не существует или не является папкой
    # Вернуть False и текст ошибки
    true_result = (True, '')
    checks_dict = {
        'symbols': lambda p: (False, 'Имя файла содержит недопустимые'
                                     ' символы: ' +
                                     f'{RESTRICTED_PATH_SYMBOLS & set(str(p))}')
                   if RESTRICTED_PATH_SYMBOLS & set(str(p)) else true_result,
        'empty': lambda p: (False, 'Вы ввели пустой путь')
              if p == Path('.') else true_result,
        'extention': lambda p: (False, 'Имя файла содержит расширение ' +
                                '(точку)') if path.suffix else true_result,
        'exists': lambda p: (False, 'Введенный путь не существует')
              if not p.exists() else true_result,
        'not_exists': lambda p: (False, 'Введенный путь уже существует')
              if p.exists() else true_result,
        'dir': lambda p: (False, 'Введенный путь не является папкой')
              if not p.is_dir() else true_result,
        'file': lambda p: (False, 'Введенный путь не является файлом')
              if not p.is_file() else true_result,
    }
    check_results = [checks_dict[check](path) for check in checks]
    check_results_errors = list(filter(lambda res: not res[0], check_results))
    if check_results_errors:
        return check_results_errors[0]
    else:
        # Вернуть True и пустой текст ошибки
        return True, ''

                           
class Settings:
    def __init__(self, application):
        
        self.application = application
        self.config_file_path = self.get_config_file_path(Path('./settings.cfg'))
        self.db_aes_path_key = 'db_aes_path'
        self.password = None

    # Создание КонФайла при необходимости и возврат пути к нему
    def get_config_file_path(self, config_file_path):
        
        if not config_file_path.exists():
            app_message('app', *CF_EXISTS_ERROR, sep='\n')
            open(config_file_path, 'wt').close()
        return config_file_path

    # Получить из конф.файла значение по ключу
    def get_value_by_key(self, key):
        
        key_re = re.compile(rf'\A\s*{key}\s*=\s*')
        with open(self.config_file_path, 'rt') as config_file:
            # Возм.ошибка - Не найден ключ к фБД_зашифр
            for line in config_file.read().split('\n'):
                if re_str := re.match(key_re, line):
                    return line[re_str.end():].strip()
            return ''

    def set_value_by_key(self, key, val):
        
        key_re = re.compile(rf'\A\s*{key}\s*=\s*')
        # Если в
        with open(self.config_file_path, 'rt') as config_file_read:
            key_in_config_file = key_re.search(config_file_read.read())
        if key_in_config_file:
            with fileinput.FileInput(files=self.config_file_path, inplace=True) as config_file:
                # Возм.ошибка - Не найден ключ к фБД_зашифр
                for line in config_file:
                    if re_str := key_re.match(line):
                        print(f'{key} = {val}')
                    else:
                        print(line, end='')
        else:
            with open(self.config_file_path, 'at') as config_file_append:
                config_file_append.write(f'{key} = {val}')


    '''Инициализировать атрибуты путей к фБД(зашифр., расшифр.):
    self.db_aes_path - фБД_зашифр
    self.db_decr_path - фБД_расшифр
    '''
    def get_db_aes_path(self):
        # Инициализировать переменные путей к фБД_зашифр, фБД_расшифр из КонфФайла
        # (1) Получить значение пути_фБД_зашифр по ключу
        db_aes_path = Path(self.get_value_by_key(self.db_aes_path_key))
        print(db_aes_path)
        '''Проверка и исправления ОШИБОК:
        - не является текущим путем,
        - существует ли путь,
        - является ли путь файлом,
        '''
        # (2) Проверить путь_фБД_зашифр, полученный по ключу
        check_results = path_checks(db_aes_path, ('empty', 'exists', 'file'))
        if not check_results[0]:
            # (2.1) Вызвать меню_Выбора/Создания_фБД_зашифр
            app_message(check_results[1])
            self.application.open_create_db()
        else:
            # (2.2) Инициализировать переменные путей к фБД
            self.db_aes_path = db_aes_path
            self.db_decr_path = self.db_aes_path.with_stem(
                    self.db_aes_path.stem + '_decr')


    def set_db_aes_path(self, db_aes_path):
        # Записать путь к фБД_зашифр в конф.файл
        self.set_value_by_key(self.db_aes_path_key, db_aes_path)
        # Инициализировать переменные путей к фБД_зашифр, фБД_расшифр
        self.get_db_aes_path()


    def get_password(self):
        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)
        return self.password


    # Выбор файла БД для открытия
    # USES
    def select_db_path(self):
        text = 'Введите путь к существующему файлу БД'
        # Функция проверки ответа на существование пути и не '.'
        variants = path_checks_carried('symbols', 'empty', 'exists', 'file')
        # Запрос ответа
        answer = get_answer(text, variants)
        # Открыть файл и проверить, является ли он файлом БД
        # Если ответ - '_back_', то вернуться в
        if answer == '_back_':
            return '_back_'
        # Если фБД для открытия выбран
        else:
            db_aes_path = Path(answer)
            # Инициализировать имена путей к фБД_зашифр, фБД_расшифр
            # Сохранить путь к фБД_зашифр в конф.файл
            self.set_db_aes_path(db_aes_path)


class DataBase:
    def __init__(self, application):
        self.application = application
        self.settings = self.application.settings
        self.connection = None
        self.cursor = None

    def close_cursor_connection(self):
        self.cursor.close()
        self.connection.close()
        self.connection = None
        self.cursor = None

    def encrypt_file(self):
        src = self.settings.db_decr_path
        tgt = self.settings.db_aes_path
        app_message('db', 'Выполняется шифрование файла БД')
        pyAesCrypt.encryptFile(src, tgt, self.settings.get_password())

    # Декодирование ф_БД
    def decrypt_file(self):
        src = self.settings.db_aes_path
        tgt = self.settings.db_decr_path
        app_message('db', 'Выполняется дешифрование файла БД')
        password = getpass.getpass(prompt='Password: ', stream=None)
        pyAesCrypt.decryptFile(src, tgt, password)

    def open_db_decr_file(self):
        self.connection = sqlite3.connect(self.settings.db_decr_path)
        self.cursor = self.connection.cursor()

    #
    # # (4) Подключение к фБД_расш
    # def db_connect(self):
    #     # (4) Открыть файл БД
    #     # in: <dbase_path>
    #     connection = sqlite3.connect(dbase_path)
    #     cursor = connection.cursor()
    #     # Проверить БД на корректность
    #     sql_query = """SELECT name FROM sqlite_master
    # WHERE type='table';"""
    #     cursor.execute(sql_query)
    #     # out: <connection>, <cursor>
    #     return connection, cursor


    def init_db(self):
        '''Structure-queries'''
        query_create_actual = '''CREATE TABLE actual (
        password_id INTEGER PRIMARY KEY,
        resource TEXT,
        login TEXT,
        password TEXT,
        description TEXT,
        create_dt TEXT NOT NULL);'''
        self.cursor.execute(query_create_actual)
        print(self.cursor.fetchall())
        query_create_archive = '''CREATE TABLE archive (
        password_id INTEGER PRIMARY KEY,
        resource TEXT,
        login TEXT,
        password TEXT,
        description TEXT,
        created_dt TEXT NOT NULL,
        archived_dt TEXT NOT NULL);'''
        self.cursor.execute(query_create_archive)
        print(self.cursor.fetchall())
        self.connection.commit()


    # Создание БД
    def create_db(self):
        while True:
            # Ввод папки для сохранения БД
            text = 'Введите путь к существующей папке'
            # Функция проверки введенного пути к папке на:
            # - не пустоту,
            # - является папкой (одновременно проверяется, что существует),
            variants = path_checks_carried('symbols', 'empty', 'exists',
                                           'dir')
            answer = get_answer(text, variants)
            if answer == '_back_':
                return '_back_'
            db_aes_folder_path = Path(answer)

            # Ввод имени файла для сохранения БД
            text = 'Введите имя файла без расширения'
            # Проверить на не существование файла, проверить на отсутствие расширения и пустоту
            # Функция проверки введенного пути к папке на:
            # - не пустоту,
            # - отсутствие расширения
            variants = path_checks_carried('symbols', 'empty')
            answer = get_answer(text, variants)
            if answer == '_back_':
                return '_back_'
            db_aes_stem_name = Path(answer)

            # Объединение пути к папке и имени файла, добавление расширения 'sqlite'
            db_aes_path = (db_aes_folder_path / db_aes_stem_name).with_suffix('.sqlite')
            # Если файл уже существует, то повторить всю функцию
            # Условие вернет True, если файл существует, False - если нет
            if path_checks(db_aes_path, ('exists',))[0]:
                app_message('db', 'Файл с таким именем уже существует. Повторите ввод')
                # Перезапуск тела цикла в новой итерации
                continue
            else:
                print(1)
                # Инициализировать имена путей к фБД_зашифр, фБД_расшифр
                # Сохранить путь к фБД_зашифр в конф.файл
                self.settings.set_db_aes_path(db_aes_path)
                # Создать фБД_расшифр
                print(2)
                self.open_db_decr_file()
                # Инициализировать структуру фБД_расшифр
                print(3)
                self.init_db()
                # Зашифровать фБД_расшифр в фБД_зашифр
                print(4)
                self.encrypt_file()
                # Закрыть соединение с фБД_расшифр
                print(5)
                self.close_cursor_connection()
                # Удалить фБД_расшифр
                print(6)
                self.settings.db_decr_path.unlink()
                return
