from pathlib import Path
import re


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

DB_LOAD_STAGES_MESSAGES = [CF_EXISTS_ERROR, CF_DB_AES_PATH_KEY_ERROR,
                           CF_DB_AES_PATH_VAL_ERROR, DB_AES_PASSWORD_ERROR,
                           DB_SQLITE3_ERROR]
                           
                           
class Settings:
    def __init__(self):
        self.config_file_path = Path('./settings.cfg')
        self.db_aes_path_key = 'db_aes_path'
        '''initialize:
        - self.db_aes_path - фа
        - self.db_decr_path
        '''
        self.get_db_aes_path()


    def get_value_by_key(self, key):
        with open(self.config_file_path, 'rt') as config_file:
            # (2, 3, 4) Получить путь фБД из конф.файла
            # in: <config_file>
            key_re = re.compile(rf'\A\s*{key}\s*=\s*')
            for line in config_file.read().split('\n'):
                if re_str := key_re.match(line):
                    return line[re_str.end():].strip()

    def get_db_aes_path(self):
        self.db_aes_path = self.get_value_by_key(self.db_aes_path_key)
        self.db_decr_path = self.db_aes_path.with_stem(
                self.db_aes_path.stem + '_decr')





