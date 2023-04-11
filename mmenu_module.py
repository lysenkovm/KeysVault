from pathlib import Path
from cmenu_ import *
from common import *
import sqlite3


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
        attributes_names = ['resource', 'login', 'password', 'description']
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
        self.db.make_insert(data_to_insert)



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
        menu.add_item('Выполнить запрос (отобразить )', 4,
                      self.db.make_select, args=(selected,))
        menu.add_item('Завершить работу с программой', 5,
                      self.db.from_close_connection_to_exit,
                      (('close', 'encrypt', 'remove', 'exit'),))
        while (menu_result := menu.show()) != '_back_':
            epilogue = gen_epilogue(selected)
            menu.set_epilogue(epilogue)
            continue

    def select_attribute(self, attribute_name, selected):
        text = f'Введите текст, содержащийся в названии ' + \
               ATTRIBUTES_NAMES_EN_RU[attribute_name]['rod']
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
