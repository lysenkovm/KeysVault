from common import *
from cmenu_ import *
from pathlib import Path
import sqlite3
import sys
import keyboard


RESTRICTED_PATH_SYMBOLS = set("'*+,./:;<=>?[\\]|«")

###################
## NEW FUNCTIONS ##
###################


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


###################
## OLD FUNCTIONS ##
###################

# Проверка на соответствие пути требованиям ОС
# !! Выбранный путь должен сохраняться в конфигурационный файл
def check_is_path(val):
    path = Path(val)
    if path.parent != Path('.') and path.parent.exists():
        return True
    return False
    

def check_name_repeat(path):
    pass


