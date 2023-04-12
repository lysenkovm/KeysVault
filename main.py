from common import *
from pathlib import Path
from cmenu_ import *
import mmenu_module


class Application(mmenu_module.Application):
    
    def __init__(self):
        self.settings = Settings(self)
        # Получить путь из КонфФайла
        # common.Settings.get_vaue_by_key() => (True, Path) / (False, 'Ключ не найден')
        db_aes_path_from_CF_result = self.settings.get_value_by_key(
              self.settings.db_aes_path_key)
        if db_aes_path_from_CF_result[0]:
            db_aes_path = Path(db_aes_path_from_CF_result[1])
            open_db_result = self.open_db(db_aes_path)
        else:
            open_db_result = (False, 'Не найден конфигурационный файл или ключ')
        if not open_db_result[0]:
            # main_alter.Application.open_create_db() => (True, Path)
            # main_alter.Application.open_db() => (False, str)
            # / (False, error)
            # / (False, 'Файл БД имеет не верную структуру')
            # / (True, '')
            while not open_db_result[0]:
                print(open_db_result[1])
                open_db_result = self.open_db(self.open_create_db()[1])
            # При завершении цикла из консоли будет доступ к объекту 'app'
        self.db.backup_db_aes()
        while True:
            # Защита фБД от случайного завершения программы
            try:
                self.main_menu()
            except KeyboardInterrupt as error:
                print('Исключение перехвачено')
                exit_args = ('close', 'encrypt', 'remove')
                self.db.from_close_connection_to_exit(exit_args)
                raise(error)
            except Exception as error:
                print('Исключение перехвачено')
                exit_args = ('close', 'encrypt', 'remove')
                self.db.from_close_connection_to_exit(exit_args)
                raise(error)

    # main_alter.Application.open_db() => (False, str)
    # / (False, error)
    # / (False, 'Файл БД имеет не верную структуру')
    # / (True, '')
    def open_db(self, db_aes_path):  # Path
        # common.path_checks() => (True, '') / (False, str)
        path_checks_result = path_checks(db_aes_path,
                                         ('no_restr_symbols', 'not_empty',
                                          'exists', 'file'))
        if not path_checks_result[0]:
            return path_checks_result
        else:
            db_file = DBFile(db_aes_path, self)  # Созд-е об-та фБД
            # common.DBFile.decrypt_file() => (True, ''), (False, error)
            db_decr_result = db_file.decrypt_file()  # Распаковка файла с получ-ем рез-та (возм.ошибки)
            '''
            ValueError: File is corrupted or not an AES Crypt (or pyAesCrypt) file. - переход в меню В/О фБД
            ValueError: File is corrupted or not an AES Crypt (or pyAesCrypt) file. - переход в меню выбора д-я
            '''
            if not db_decr_result[0]:
                # Позже дополнить Меню выбора действия, если пароль не подошёл
                return db_decr_result  # Возможно с 'return' # Если файл - не зашифрованный
            else:
                # common.DBFile.db_connect() => (True, self.cursor.fetchall()) / (False, error)
                # sqlite3.DatabaseError: file is not a database
                db_connect_result = db_file.db_connect()
                if not db_connect_result[0]:
                    db_file.close_cursor_connection()
                    db_file.db_decr_path.unlink()
                    return db_connect_result
                else:
                    if db_connect_result[1] != TABLE_STRUCTURE:
                        db_file.close_cursor_connection()
                        db_file.db_decr_path.unlink()
                        return False, 'Файл БД имеет не верную структуру'
                    else:
                        self.settings.set_value_by_key(self.settings.db_aes_path_key, str(db_aes_path))
                        self.settings.set_db_aes_path(db_aes_path)  # Уст-ка атрибута db_aes_path
                        self.db = db_file
                        return True, ''

    # Вызов меню 'Открыть/выбрать файл БД'
    # main_alter.Application.open_create_db() => (True, Path)
    def open_create_db(self):
        # Вызвать меню создания/открытия файла БД
        title = 'Открыть/выбрать файл БД'
        prologue = 'Внимание! Файл зашифрованной БД не найден!'
        menu_open_create_db = CMenu(self, title, prologue)
        menu_open_create_db.add_item('Открыть существующий файл БД', 1,
                                     self.select_db_path)
        menu_open_create_db.add_item('Создать новый файл БД', 2,
                                     self.create_db)
        # cmenu_.CMenu.show()
        # => cmenu_.CMenu.ask()
        # => cmenu_.CMenuItem.launch_func()
        # => cmenu_.CMenuItem.func(*CMenuItem.args=())
        # func == main_alter.Application.select_db_path() => '_back_': str / (True, db_aes_path: Path)
        # func == main_alter.Application.create_db() => 'back': str / (True, db_aes_path: Path)
        while (open_create_result := menu_open_create_db.show()) == '_back_':
            continue
        else:
            return open_create_result  # (True, Path)

    # Выбор файла БД для открытия
    # main_alter.Application.select_db_path() => '_back_': str / (True, db_aes_path: Path)
    def select_db_path(self):
        text = 'Введите путь к существующему файлу БД'
        # Функция проверки ответа на существование пути и не '.'
        variants = path_checks_carried('no_restr_symbols', 'not_empty',
                                       'exists', 'file')
        # Запрос ответа
        # cmenu_.get_answer() => return: '_back_': str / answer: str
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
            return True, db_aes_path

    # Создание БД
    # main_alter.Application.create_db => 'back': str / (True, db_aes_path: Path)
    def create_db(self):
        while True:
            # Ввод папки для сохранения БД
            text = 'Введите путь к существующей папке'
            # Функция проверки введенного пути к папке на:
            # - не пустоту,
            # - является папкой (одновременно проверяется, что существует),
            variants = path_checks_carried('no_restr_symbols', 'not_empty',
                                           'exists', 'dir')

            # cmenu_.get_answer() => return: '_back_': str, answer: str
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
            variants = path_checks_carried('no_restr_symbols', 'not_empty')

            # cmenu_.get_answer() => return: '_back_': str, answer: str
            answer = get_answer(text, variants)
            if answer == '_back_':
                return '_back_'
            db_aes_stem_name = Path(answer)

            # Объединение пути к папке и имени файла, добавление расширения 'sqlite'
            db_aes_path = (db_aes_folder_path / db_aes_stem_name).with_suffix('.sqlite')
            # Если файл уже существует, то повторить всю функцию
            # Условие вернет True, если файл существует, False - если нет
            if not path_checks(db_aes_path, ('not_exists', ))[0]:
                app_message('db', 'Файл с таким именем уже существует. Повторите ввод')
                # Перезапуск тела цикла в новой итерации
                continue
            else:
                db = DBFile(db_aes_path, self)
                db.init_db()
                db.from_close_connection_to_exit(('close', 'encrypt', 'remove'))
                return True, db_aes_path

    
# Открытие фБД через исключения
def main():
    # Application-object with Settings- and DataBase-objects
    app = Application()
    return app


if __name__ == '__main__':
    app = main()
