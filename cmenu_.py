import sys
import keyboard


def enframe(t):

    def get_left_center_right(border_len, symb):
        symbols = {'/': '\\', '\\': '/'}
        return (border_len // 2 * symb) + ('|' if border_len % 2 else '') + \
               (border_len // 2 * symbols[symb])

    t = t.split('\n')  # Разбить текст на строки
    # Будущая длина строки вместе с границами
    border_len = len(max(t, key=len)) + 6
    # t1 = []  # список строк текста с границами и пробелами
    for row_n in range(len(t)):  # для каждого индекса строки в списке
        left_spaces = 2 * ' '  # пробелы слева - всегда 2
        # пробелы справа
        right_spaces = (border_len - 4 - len(t[row_n])) * ' '
        row = left_spaces + t[row_n] + right_spaces
        if row_n <= len(t) // 2 - 1:
            left, right = '\\', '/'
        elif (row_n == len(t) // 2) and len(t) % 2:
            left, right = '-', '-'
        else:
            left, right = '/', '\\'
        t[row_n] = left + row + right
    t_bordered = '\n'.join(t)
    return '\n'.join([get_left_center_right(border_len, '\\'), t_bordered,
                      get_left_center_right(border_len, '/')])



# answer_checker - функция
def get_answer(text, answer_checker,
               error_text='Введено неверное значение. Повторите ввод.'):
    # Повторять вопрос, пока пользователь не введет 'back' или ответ,
    # удовлетворяющий функции-условию
    while True:
        # 0
        # Вывести приглашение для ввода (вопрос)
        print(text)
        print('Возврат - "escape"')

        # 1
        # Сигнальная метка выхода из цикла запроса ввода пользователя
        # в виде списка (изменяемого объекта)
        cue = []
        # Добавление горячей клавиши "Escape"
        # Lambda-функция, изменяющая сигн.метку (cue), и выполняющая нажатие "Enter",
        # после которого выполняется проверка сигн.метки
        keyboard.add_hotkey('esc', lambda: cue.append(True) or
                                           keyboard.press('enter'))

        # 2
        # Ввод пользователем ответа 'answer'
        answer = input('Ввод: ')
        keyboard.remove_all_hotkeys()  # очистка всех горячих клавиш

        # 3
        # В случае нажатия 'Esc' вернуть '_back_'
        if cue:
            return '_back_'
        # Проверка ответа функцией 'answer_checker'
        check_status, error_text = answer_checker(answer)
        # Если ответ прошёл проверку функцией
        if check_status:
            # Вернуть ответ
            return answer
        # Если ответ не прошёл проверку функцией
        else:
            # Вывести текст ошибки и повторить запрос
            print(error_text)



# Класс Элемента меню
class CMenuItem:
    def __init__(self, parent, text, num, func=False, args=()):
        self.parent = parent
        self.text = text
        self.num = str(num)
        if not func:
            self.func = self.__str__
        else:
            self.func = func
        self.args = args

    def __str__(self):
        text = f'({self.num})\t{self.text} - {str(self.func)}'
        return text  # - {func} - потом удалить

    def launch_func(self):
        return self.func(*self.args)


# Класс Меню (прародитель)
class CMenu:
    def __init__(self, parent, title, prologue=None, epilogue=None,
                 exit_item=True, back_item=False):
        self.parent = parent
        self.title = title
        self.prologue = prologue
        self.epilogue = epilogue
        self.exit_item = exit_item
        self.back_item = back_item
        self.items = []

    def show(self):
        # Добавить элемент выхода из программы!
        if tuple(filter(lambda x: x.text == '_exit_', self.items)):
            self.add_exit_item()
        # Вывод меню через вывод элементов и 'enframe()'
        print(self)
        # Возврат результата Вызова метода запроса ввода пользователя
        return self.ask()

    def __str__(self):
        menu_str = ''
        menu_str += self.title + '\n\n'
        items_str = '\n'.join([str(item) for item in self.items])
        menu_str += items_str + '\n\n'
        menu_str += self.prologue
        return enframe(menu_str)

    def add_item(self, text, num, func, args=()):
        self.items.append(CMenuItem(self.parent, text, num, func, args))

    def add_exit_item(self):
        exit_num = len(self.items) + 1
        self.items.append(CMenuItem('_exit_', str(exit_num), sys.exit))
        
    def ask(self):
        answer = input('Ввод: ')
        item_selected = list(filter(lambda item: item.num == 
                             answer, self.items))[0]
        return item_selected.launch_func()  # Например, select_db_path() из open_create_db_module.py
        # Реализовать: здесь обработка выбранного элемента
