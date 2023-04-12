from common import *
import pyperclip
from tabulate import tabulate


class Application:
    def main_menu(self):
        title = 'Основное меню'
        prologue = 'Управление паролями'
        menu = CMenu(self, title, prologue, exit_item=False)
        menu.add_item('Добавить пароль', 1, self.add_password)
        menu.add_item('Выборка записей', 2, self.selection_menu)
        # menu.add_item('Действия с записью', 2, self.entry_managing)
        menu.add_item('Сменить БД', 3, self.open_create_db)
        menu.add_item('Завершить работу с программой', 4,
                      self.db.from_close_connection_to_exit,
                      (('close', 'encrypt', 'remove', 'exit'),))
        menu_result = menu.show()

    def add_password(self):
        attributes_names = DB_TABLES_COLUMNS_NAMES['actual'][1:-1]
        data_to_insert = {}
        for attribute_name in attributes_names:
            answer = get_answer('Введите ' +
                                ATTRIBUTES_NAMES_EN_RU[attribute_name]
                                ['vin'], lambda x: (True, ''))
            # Если ответ - '_back_', то вернуться в
            if answer == '_back_':
                return '_back_'
            else:
                data_to_insert[attribute_name] = answer
        data_to_insert['create_dt'] = dt.datetime.now().strftime('%Y.%m.%d / %H:%M:%S')
        self.db.make_insert('actual', data_to_insert)


    def selection_menu(self):

        def gen_epilogue(selected):
            return f'Ресурс: {selected["resource"]}\n' + \
                   f'Логин: {selected["login"]}\n' + \
                   f'Описание: {selected["description"]}'

        selected = {'resource': '', 'login': '', 'description': ''}
        title = 'Выборка записей и выполнение операций'
        prologue = 'Вывод списка записей по параметрам'
        epilogue = gen_epilogue(selected)
        menu = CMenu(self, title, prologue, epilogue, exit_item=False, back_item=True)
        menu.add_item('Ресурс (сайт и т.п.)', 1, self.select_attribute,
                      args=('resource', selected))
        menu.add_item('Логин', 2, self.select_attribute,
                      args=('login', selected))
        menu.add_item('Описание', 3, self.select_attribute,
                      args=('description', selected))
        menu.add_item('Выполнение запроса и работа с результатами', 4,
                      self.show_results, args=(selected,))
        # menu.add_item('Выполнить запрос (отобразить )', 4,
        #               self.db.make_select, args=(selected, 'actual'))
        menu.add_item('Завершить работу с программой', 5,
                      self.db.from_close_connection_to_exit,
                      (('close', 'encrypt', 'remove', 'exit'),))
        while (menu_result := menu.show()) != '_back_':
            epilogue = gen_epilogue(selected)
            menu.set_epilogue(epilogue)
            continue

    def select_attribute(self, attribute_name, selected):
        text = f'Введите текст, содержащийся в названии ' + \
               ATTRIBUTES_NAMES_EN_RU[attribute_name]['rod'] + \
            '\n# для поиска включений используйте подстановочные символы:' + \
            '\n# "%" - любой набор символов' + \
            '\n# "_" - любой символ'
        # Функция проверки ответа на существование пути и не '.'
        # Запрос ответа
        # cmenu_.get_answer() => return: '_back_': str / answer: str
        answer = get_answer(text, lambda x: (True, ''))
        # Открыть файл и проверить, является ли он файлом БД
        # Если ответ - '_back_', то вернуться в
        if answer == '_back_':
            return '_back_'
        # Если фБД для открытия выбран
        else:
            selected[attribute_name] = answer
            # Инициализировать имена путей к фБД_зашифр, фБД_расшифр
            # Сохранить путь к фБД_зашифр в конф.файл

    def yes_or_no(self, text):
        answer = get_answer(text, lambda x: (True, '')
                            if x in list('yn') else
                            (False, SIMPLE_INPUT_ERROR))
        if answer == '_back_':
            return '_back_'
        # Если фБД для открытия выбран
        else:
            return answer


    def archive_entry_decide(self, entry):
        text = '''Вы действительно хотите переместить выбранную запись в архив? (y/n)'''
        yes_or_no_answer = self.yes_or_no(text)
        if yes_or_no_answer == '_back_':
            return '_back_'
        elif yes_or_no_answer == 'y':
            self.db.archive_entry(entry)
            return '_archived_'


    def show_results(self, selected):
        # selected = {'resource': '', 'login': '', 'description': ''}
        table_name = 'actual'
        result_data = self.db.make_select(selected, table_name)
        passwords_ids = [entry[0] for entry in result_data]
        app_message('db', tabulate(result_data,
                                   headers=DB_TABLES_COLUMNS_NAMES
                                   [table_name]))
        text = 'Введите password_id записи'
        answer = get_answer(text, lambda x: (True, '')
                            if x.isdecimal() and int(x) in passwords_ids else
                            (False, SIMPLE_INPUT_ERROR))
        if answer == '_back_':
            return '_back_'
        # Если фБД для открытия выбран
        else:
            selected_entry_list = [entry for entry in result_data
                                   if entry[0] == int(answer)]
            title = 'Операции над записью'
            prologue = 'Выберите, что сделать с выбранной записью' + '\n' + \
                tabulate(selected_entry_list,
                         headers=DB_TABLES_COLUMNS_NAMES[table_name])

            menu = CMenu(self, title, prologue, exit_item=False, back_item=True)
            menu.add_item('Скопировать логин в буфер обмена', 1,
                          lambda: pyperclip.copy(selected_entry_list[0]
                                                 [DB_TABLES_COLUMNS_NAMES
                              [table_name].index('login')]))
            menu.add_item('Скопировать пароль в буфер обмена', 2,
                          lambda: pyperclip.copy(selected_entry_list[0]
                                                 [DB_TABLES_COLUMNS_NAMES
                              [table_name].index('password')]))
            menu.add_item('Скопировать всю запись в буфер обмена', 3,
                          lambda: pyperclip.copy(str(selected_entry_list[0])))
            menu.add_item('Переместить запись в архив', 4,
                          self.archive_entry_decide, args=(selected_entry_list[0],))
            # menu.add_item('Удалить запись без архивирования', 5,
            #               self.show_results, args=(selected, answer))
            while (menu_result := menu.show()) not in ('_back_', '_archived_', '_deleted_'):
                continue