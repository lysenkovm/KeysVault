import sys


def enframe(t):
    t = t.split('\n')
    border_len = len(max(t, key=len)) + 6
    rows_n = len(t)
    t1 = []
    for row_n in range(rows_n):
        row = t[row_n]
        row_len = len(row)

        left_spaces = 2 * ' '
        diff = border_len - 4 - row_len
        right_spaces = diff * ' '
        
        row = left_spaces + row + right_spaces
        if row_n <= rows_n / 2:
            left, right = '\\', '/'
        elif (row_n == rows_n // 2) and row_n % 2:
            left, right = '-', '-'
        else:
            left, right = '/', '\\'
        t1.append(left + row + right)
    
    t2 = '\n'.join(t1)
    op_left = border_len // 2 * '\\'
    op_center = '|' if border_len % 2 else ''
    op_right = border_len // 2 * '/'
    op = op_left + op_center + op_right
    cl_left = border_len // 2 * '/'
    cl_center = '|' if border_len % 2 else ''
    cl_right = border_len // 2 * '\\'
    cl = cl_left + cl_center + cl_right
    return '\n'.join([op, t2, cl])



# Класс Элемента меню
class CMenuItem:
    def __init__(self, text, num, func):
        self.text = text
        self.num = str(num)
        self.func = func

    def __str__(self):
        text = f'({self.num})\t{self.text} - {str(self.func)}'
        return text  # - {func} - потом удалить


# Класс Меню (прародитель)
class CMenu:
    def __init__(self, title, prologue=None, epilogue=None, 
                 exit_item=True, back_item=False, parent=None):
        self.parent = parent
        self.title = title
        self.prologue = prologue
        self.epilogue = epilogue
        self.exit_item = exit_item
        self.items = []

    def show(self):
        # Добавить элемент выхода из программы!
        if tuple(filter(lambda x: x.text == 'exit', self.items)):
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

    def add_item(self, item):
        self.items.append(item)

    def add_exit_item(self):
        exit_num = len(self.items) + 1
        self.items.append(CMenuItem('exit', str(exit_num), 
                                    sys.exit))
        
    def ask(self):
        answer = input('Ввод: ')
        item_selected = list(filter(lambda item: item.num == 
                             answer, self.items))[0]
        print(item_selected.func)
        return item_selected.func()  # Например, select_db_path() из open_create_db_module.py
        # Реализовать: здесь обработка выбранного элемента
        
