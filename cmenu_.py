import sys
import keyboard


def app_message(title_type, *args, **kwargs):
    if title_type == 'app':
        title = 'Pass Vault'
    elif title_type == 'db':
        title = 'Pass Vault - Data Base'
    title_marked = title.rjust(79 // 2 + len(title) // 2,
                               '-').ljust(79, '-')
    print(title_marked)
    # args = ['' + str(arg) for arg in args]
    print(*args, **kwargs, end='\n\n')


def enframe(t):
    t = t.split('\n')  # Разбить текст на строки
    t = ['|  ' + row for row in t]
    max_len_no_indent = len(max(t, key=len)) + 2
    t = [row.ljust(max_len_no_indent, ' ') + '|' for row in t]
    t.insert(0, '/' + '-' * (max_len_no_indent - 1) + '\\')
    t.append('\\' + '-' * (max_len_no_indent - 1) + '/')
    return '\n'.join(t)


# answer_checker - функция
# cmenu_.get_answer() => return: '_back_': str / answer: str
def get_answer(text, answer_checker,
               error_text='Введено неверное значение. Повторите ввод.'):
    # Повторять вопрос, пока пользователь не введет 'back' или ответ,
    # удовлетворяющий функции-условию
    while True:
        # 0
        # Вывести приглашение для ввода (вопрос)
        app_message('app', text, 'Возврат - "escape"')

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
            app_message('app', error_text)



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
        text = f'({self.num})  {self.text}'
        return text  # - {func} - потом удалить

    # cmenu_.CMenuItem.launch_func() => self.func(*CMenuItem.args=())
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

    # cmenu_.CMenu.show()
    # => cmenu_.CMenu.ask()
    # => cmenu_.CMenuItem.launch_func()
    # => cmenu_.CMenuItem.func(*CMenuItem.args=())
    def show(self):
        # Добавить элемент выхода из программы!
        if self.exit_item and not tuple(filter(
                  lambda x: x.text == '_exit_', self.items)):
            self.add_exit_item()
        if self.back_item and not tuple(filter(
                  lambda x: x.text == '_back_', self.items)):
            self.add_back_item()
        # Вывод меню через вывод элементов и 'enframe()'
        print(self)
        # Возврат результата Вызова метода запроса ввода пользователя
        # cmenu_.CMenu.ask()
        # => cmenu_.CMenuItem.launch_func()
        # => cmenu_.CMenuItem.func(*CMenuItem.args=())
        return self.ask()

    def __str__(self):
        menu_str = ''
        menu_str += self.title + '\n\n'
        if self.prologue:
            menu_str += self.prologue + '\n'
        items_str = '\n'.join([str(item) for item in self.items])
        menu_str += items_str + '\n\n'
        if self.epilogue:
            menu_str += self.epilogue
        return enframe(menu_str)

    def add_item(self, text, num, func, args=()):
        self.items.append(CMenuItem(self.parent, text, num, func, args))


    def add_back_item(self):
        back_num = len(self.items) + 1
        self.items.append(CMenuItem(self.parent, '_back_', str(back_num)))


    def add_exit_item(self):
        exit_num = len(self.items) + 1
        self.items.append(CMenuItem(self.parent, '_exit_', str(exit_num),
                                    sys.exit))

    # cmenu_.CMenu.ask()
    # => cmenu_.CMenuItem.launch_func()
    # => cmenu_.CMenuItem.func(*CMenuItem.args=())
    def ask(self):
        answer = input('Ввод: ')
        item_selected = list(filter(lambda item: item.num ==
                             answer, self.items))[0]
        if item_selected.text == '_back_':
            return '_back_'
        # cmenu_.CMenuItem.launch_func() => # => cmenu_.CMenuItem.func(*CMenuItem.args=())
        return item_selected.launch_func()  # Например, select_db_path() из open_create_db_module.py

    def set_epilogue(self, epilogue):
        self.epilogue = epilogue