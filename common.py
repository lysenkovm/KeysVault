CF_NAME = 'settings.cfg'
CF_DB_AES_PATH_KEY = 'db_aes_path'

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
                           
                           
                           