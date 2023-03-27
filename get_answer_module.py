import keyboard, sys


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
                            keyboard.press('enter'), args=(cue))
        
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
