from common import *
import crypta_
from cmenu_ import *
import open_create_db_module as ocdb_module
from pathlib import Path
##import main_menu_class



def db_connect(dbase_path):
    connection = sqlite3.connect(dbase_path)
    cursor = connection.cursor()
    return connection, cursor


def main():
    # Проверка наличия и при необх-ти создание конф.файла
    config_file_path = Path(f'./{CF_NAME}')
    # (2) Если путь к конфиг.файлу не существует
    if not config_file_path.exists():
        print('# (2) Если путь к конфиг.файлу не существует')
        # Создать конфиг.файл и записать в него параметр пути к фБД
        with open(config_file_path, 'wt') as config_file:
            config_file.write(CF_DB_AES_PATH_KEY + '\n')
    # (1) Если же путь существует, то проверить наличие ключа параметр фБД,
    # и если нет, то добавить ключ
    else:
        print('# (1) Если же путь существует, то проверить наличие ключа параметр фБД,')
        with open(config_file_path, 'r+') as config_file:
            # Отфильтровать строку с ключом пути фБД
            selection = list(filter(lambda line: line.startswith
                                    (CF_DB_AES_PATH_KEY),
                                    config_file.read().split('\n')))
            # (1.2) Если ключ не найден, то вставить его в файл
            if not selection:
                print('# (1.2) Если ключ не найден, то вставить его в файл')
                config_file.write('\n' + CF_DB_AES_PATH_KEY + '\n')
    
    # (1.1) Получить значение пути к фБД по ключу
    with open(config_file_path, 'r+') as config_file:
        # Отфильтровать строку с ключом пути фБД
        selection = list(filter(lambda line: line.startswith
                                (CF_DB_AES_PATH_KEY),
                                config_file.read().split('\n')))
        db_aes_path_str = selection[0][len(CF_DB_AES_PATH_KEY)
                                       :].strip(' \n\t=')
        print('# (1.1) Получить значение пути к фБД по ключу')
        print(db_aes_path_str)

    # (1.1.1.2) Проверить наличие фБД по пути
    # и при отсутствии вызвать меню Откр/Созд фБД:
    # - создать/открыть фБД,
    # - записать в конф.файл путь,
    # - получить путь фБД,
    # - расшифровать фБД,
    # - открыть фБД(расшифр)
    # (1.1.1.2) Проверить наличие фБД по пути
    if not db_aes_path_str or not Path(db_aes_path_str).exists():
        # Вызвать меню создания/открытия файла БД
        title = 'Открыть/выбрать файл БД'
        prologue = 'Внимание! Файл зашифрованной БД не найден!'
        menu_open_create_db = CMenu(title, prologue)
        menu_open_create_db.add_item(CMenuItem('Открыть существующий файл БД',
                                               1, ocdb_module.select_db_path))
        menu_open_create_db.add_item(CMenuItem('Создать новый файл БД',
                                               2, ocdb_module.create_db))
        menu_open_create_db.show()  # Открывает данное меню
        
    #### Не закрывать меню, пока фБД не будет создан или выбран

    # Расшифровать файл БД
    

    


    
    
##    while True:
##        
##        # Если путь из конфиг.файла не существует
##        if not open_create_db_module_class.check_path_exists(db_aes_path):
##            # Вызов меню создания/открытия файла БД
##            prologue_text = 'Внимание! Файл зашифрованной БД не найден!'
##            menu_open_create_db = open_create_db_module_class. \
##                                  menu_open_create_db(prologue_text)
##            menu_open_create_db.show()  # Открывает данное меню
##        # Если путь из конфиг.файла ссылается на не sqlite3-файл
##        elif not open_create_db_module_class.check_db_valid(db_aes_path):
##            # Вызов меню создания/открытия файла БД
##            prologue_text = '''Внимание! Файл БД не является файлом формата 'sqlite3'.
##Необходимо открыть другой файл БД.'''
##            menu_open_create_db = open_create_db_module_class. \
##                                  menu_open_create_db(prologue_text)
##            menu_open_create_db.show()  # Закрывает данное меню
##        else:
##            print('allright')
            
            # Расшифровать файл БД
##            db_path_suffix = Path(db_aes_path).suffix
##            db_path_encrypted = Path(db_aes_path).with_name('db_decrypted'). \
##                                with_suffix(db_path_suffix)
##            crypta_.decrypt_file(db_aes_path, db_path_encrypted)
            # Подключение к БД и получения курсора
##            conn = sqlite3.connect(db_path_encrypted)
##            cur = conn.cursor()
            # Вызов основного меню
##            main_menu = main_menu_class.MainMenu(cur)
            
            
            # Зашифровать файл БД
##            crypta_.encrypt_file(db_path_encrypted, db_aes_path)
##            return

if __name__ == '__main__':
    main()
