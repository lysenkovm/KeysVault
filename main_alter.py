from common import *
import open_create_db_module as ocdb_module
from pathlib import Path
import sqlite3
from cmenu_ import *
##import main_menu_class


class Application:
    def __init__(self):
        # Созание общего объекта настроек
        '''app.settings.config_file_path
        app.settings.db_aes_path_key
        app.settings.password = None'''
        self.settings = Settings(self)
        # Созание общего объекта упр-я БД, в котором ничего пока нет
        self.db = DataBase(self)
        self.fill_db_aes_path()
        '''Расшифровать фБД_зашифр в фБД_расшифр, подключиться к фБД_расшифр
        self.connection - соединение с БД,
        self.cursor - курсор'''
        self.db_decrypt_open_connect()
        # Следующие действия


    # Инициализировать атрибуты объекта Settings: db_aes_path, db_decr_path
    def fill_db_aes_path(self):
        # Вызов метода файла настроек для получения пути к фБД_зашифр
        self.settings.get_db_aes_path()


    '''Расшифровать фБД_зашифр в фБД_расшифр, подключиться к фБД_расшифр
    connection - соединение с БД,
    cursor - курсор'''
    def db_decrypt_open_connect(self):
        self.db.decrypt_file()
        self.db.open_db_decr_file()


    # Вызов меню 'Открыть/выбрать файл БД'
    # USES
    def open_create_db(self):
        # Вызвать меню создания/открытия файла БД
        title = 'Открыть/выбрать файл БД'
        prologue = 'Внимание! Файл зашифрованной БД не найден!'
        menu_open_create_db = CMenu(self, title, prologue)
        menu_open_create_db.add_item('Открыть существующий файл БД', 1,
                                     self.settings.select_db_path)
        menu_open_create_db.add_item('Создать новый файл БД', 2,
                                     self.db.create_db)
        while (db_aes_path := menu_open_create_db.show()) == '_back_':
            continue


# Открытие фБД через исключения
def main():
    # Application-object with Settings- and DataBase-objects
    app = Application()
    return app


if __name__ == '__main__':
    app = main()
