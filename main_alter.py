from common import *
import open_create_db_module as ocdb_module
from pathlib import Path
import sqlite3
##import main_menu_class


# Открытие фБД через исключения
def main():
    while True:
        try:
            config_file_path = Path(f'./{CF_NAME}')
            connection, cursor = ocdb_module.open_db_from_read_settings(config_file_path)

        except FileNotFoundError as error:
        # (1) конф.файл отсутствует
            if error.filename == str(config_file_path):
                print(CF_EXISTS_ERROR[0])
                with open(config_file_path, 'wt') as config_file:
                    config_file.write(f'{CF_DB_AES_PATH_KEY} = ' + '\n')
                print(CF_EXISTS_ERROR[1])
                print(CF_DB_AES_PATH_KEY_ERROR[1])
        # (2) Не найден ключ пути к фБД
        except IndexError as error:
            print(CF_DB_AES_PATH_KEY_ERROR[0])
            with open(config_file_path, 'at') as config_file:
                # Записать пустой ключ в конф.файл
                config_file.write(f'{CF_DB_AES_PATH_KEY} = ' + '\n')
            print(CF_DB_AES_PATH_KEY_ERROR[1])
        except ValueError as error:
        # (3) Не найден фБД_зашифр
            if error.args[0] in ('Unable to read input file.',
                                 "WindowsPath('.') has an empty name"):
                print(CF_DB_AES_PATH_VAL_ERROR[0])
                # Создать / выбрать фБД
                print(CF_DB_AES_PATH_VAL_ERROR[1])
                ocdb_module.open_create_db()
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
                ocdb_module.open_create_db()
        except sqlite3.DatabaseError as error:
        # (4) фБД_дешифр не может быть прочитан
            if error.args[0] == 'file is not a database':
                print(DB_SQLITE3_ERROR[0])
                # Создать / выбрать фБД / ввести пароль повторно
                print(DB_SQLITE3_ERROR[1])
                ocdb_module.open_create_db()
        else:
            return  # временно
    # Действие <по завершении> работы приложения - посмотреть в Интернете
##    # Зашифровать файл БД
##    crypta_.encrypt_file(db_path_encrypted, db_aes_path)

if __name__ == '__main__':
    main()
