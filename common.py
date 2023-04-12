from pathlib import Path
import re
import pyAesCrypt
import getpass
import sqlite3
import inspect
import fileinput
import datetime as dt
# import os
from cmenu_ import *
from tabulate import tabulate
import shutil




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

SIMPLE_INPUT_ERROR = 'Введено неверное значение. Повторите ввод.'

RESTRICTED_PATH_SYMBOLS = set("'*+,;<=>?[]|«")
TABLE_STRUCTURE = open(r'./file_format.txt', 'rt').read().strip()
DB_TABLES_COLUMNS_NAMES = {'actual': ['password_id', 'resource',
                                      'login', 'password',
                                      'description', 'create_dt'],
                           'archive': ['password_id', 'resource', 'login',
                                       'password', 'description',
                                       'created_dt', 'archived_dt']}
ATTRIBUTES_NAMES_EN_RU = {'resource':
                              {'rod': 'ресурса',
                               'vin': 'название ресурса'},
                          'login':
                              {'rod': 'логина',
                               'vin': 'логин'},
                          'description':
                              {'rod': 'описания',
                               'vin': 'текст описания'},
                          'password':
                              {'rod': 'пароля',
                               'vin': 'пароль'}}


def info(func):
    def f(*args, **kwargs):
        st = inspect.stack()
        print(f'line {st[2].lineno}')
        print(st[1][4])
        #   print(st)
        print(func.__name__)
        return func(*args, **kwargs)
    return f


def path_checks_carried(*checks):
    def func(path_str):
        return path_checks(path_str, checks)
    return func


''' Проверка пути'''
# common.path_checks() => (True, '') / (False, str)
def path_checks(path_str, checks):
    path = Path(path_str)
    # Если путь - пустой, не существует или не является папкой
    # Вернуть False и текст ошибки
    true_result = (True, '')
    checks_dict = {
        'no_restr_symbols': lambda p: (False, 'Имя файла содержит недопустимые'
                                     ' символы: ' +
                                     f'{RESTRICTED_PATH_SYMBOLS & set(str(p))}')
                   if RESTRICTED_PATH_SYMBOLS & set(str(p)) else true_result,
        'not_empty': lambda p: (False, 'Вы ввели пустой путь')
              if p == Path('.') else true_result,
        'no_extention': lambda p: (False, 'Имя файла содержит расширение ' +
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
        # self.db_aes_path = self.db_decr_path = None
        self.password = None

    # Создание КонФайла при необходимости и возврат пути к нему
    def get_config_file_path(self, config_file_path):
        if not config_file_path.exists():
            app_message('app', *CF_EXISTS_ERROR, sep='\n')
            open(config_file_path, 'wt').close()
        return config_file_path

    # Получить из конф.файла значение по ключу
    # common.Settings.get_vaue_by_key => (True, Path) / (False, 'Ключ не найден')
    def get_value_by_key(self, key):
        key_re = re.compile(rf'\A\s*{key}\s*=\s*')
        with open(self.config_file_path, 'rt') as config_file:
            # Возм.ошибка - Не найден ключ к фБД_зашифр
            for line in config_file.read().split('\n'):
                if re_str := re.match(key_re, line):
                    return True, Path(line[re_str.end():].strip())
            return False, 'Ключ не найден'

    def set_db_aes_path(self, db_aes_path):
        self.db_aes_path = db_aes_path

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

    def get_password(self):
        if self.password is None:
            self.password = getpass.getpass(prompt='Password: ', stream=None)
        return self.password


class DBFile:
    def __init__(self, db_aes_path, app=None):
        self.db_aes_path = db_aes_path
        self.db_decr_path = self.db_aes_path.with_stem(
              self.db_aes_path.stem + '_decr')
        self.cursor = self.connection = None
        self.app = app

    def backup_db_aes(self):
        app_message('app', 'Создается резервная копия файла БД')
        shutil.copy(self.db_aes_path, self.db_aes_path.
                    with_stem(self.db_aes_path.stem + '_backup'))


    def make_insert(self, table_name, data_to_insert):
        attributes_list = ', '.join(DB_TABLES_COLUMNS_NAMES[table_name][1:])
        values_list = ', '.join(['\"' + data_to_insert[k] + '\"' for k in
                                 DB_TABLES_COLUMNS_NAMES[table_name][1:]])
        request = f'''INSERT INTO {table_name} ({attributes_list})
VALUES ({values_list});'''
        print(request)  # test
        self.cursor.execute(request)
        self.connection.commit()


    def archive_entry(self, entry):
        data_to_insert = dict(zip(DB_TABLES_COLUMNS_NAMES['actual'][1:], entry[1:]))
        data_to_insert['created_dt'] = data_to_insert['create_dt']
        data_to_insert['archived_dt'] = dt.datetime.now().strftime('%Y.%m.%d / %H:%M:%S')
        self.make_insert('archive', data_to_insert)
        self.delete_entry('actual', 'password_id', entry[0])


    def delete_entry(self, table_name, attribute_name, attribute_value):
        request = f'''DELETE FROM '{table_name}' WHERE
{attribute_name} = '{attribute_value}';'''
        self.cursor.execute(request)
        self.connection.commit()


    def make_select(self, selected, table_name):
        request_select_part = f'''SELECT * FROM {table_name}'''
        selected_true = list(filter(lambda item: item[1],
                                         selected.items()))
        if selected_true:
            request_where_part = 'WHERE ' + \
                                 ' AND '.join([f'{k} LIKE "{v}"' for
                                               k, v in selected_true])
        else:
            request_where_part = ''
        request = request_select_part + '\n' + request_where_part + ';'
        self.cursor.execute(request)
        return self.cursor.fetchall()


    # Декодирование фБД
    # common.DBFile.decrypt_file() => (True, ''), (False, error)
    def decrypt_file(self):
        src = self.db_aes_path
        tgt = self.db_decr_path
        app_message('db', 'Выполняется дешифрование файла БД')
        password = getpass.getpass(prompt='Password: ', stream=None)
        try:
            pyAesCrypt.decryptFile(src, tgt, password)
        except ValueError as error:
            return False, error
        else:
            return True, ''

    def encrypt_file(self):
        app_message('db', 'Выполняется шифрование файла БД')
        pyAesCrypt.encryptFile(self.db_decr_path, self.db_aes_path,
                               self.app.settings.get_password())

    # Подключение и проверка (sqlite) к фБД_расш
    # common.DBFile.db_connect() => (True, self.cursor.fetchall()) / (False, error)
    def db_connect(self):
        # Открыть файл БД
        self.connection = sqlite3.connect(self.db_decr_path)
        self.cursor = self.connection.cursor()
        # Проверить БД на корректность
        sql_query = """SELECT * FROM sqlite_master;"""
        try:
            self.cursor.execute(sql_query)
        except sqlite3.DatabaseError as error:
            return False, error
        else:
            return True, str(self.cursor.fetchall())

    def init_db(self):
        # Открыть файл БД
        self.connection = sqlite3.connect(self.db_decr_path)
        self.cursor = self.connection.cursor()
        # Structure-queries
        query_create_actual = '''CREATE TABLE actual (
        password_id INTEGER PRIMARY KEY,
        resource TEXT,
        login TEXT,
        password TEXT,
        description TEXT,
        create_dt TEXT NOT NULL);'''
        self.cursor.execute(query_create_actual)
        app_message('db', self.cursor.fetchall())
        query_create_archive = '''CREATE TABLE archive (
        password_id INTEGER PRIMARY KEY,
        resource TEXT,
        login TEXT,
        password TEXT,
        description TEXT,
        created_dt TEXT NOT NULL,
        archived_dt TEXT NOT NULL);'''
        self.cursor.execute(query_create_archive)
        app_message('db', self.cursor.fetchall())
        self.connection.commit()

    def close_cursor_connection(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    def from_close_connection_to_exit(self, args):
        actions = {'close': self.close_cursor_connection,
                   'encrypt': self.encrypt_file,
                   'remove': self.db_decr_path.unlink,
                   'exit': sys.exit}
        for arg in args:
            actions[arg]()
