import tkinter as tk


def sidebar_button(master, text, command, y=5, width=215, height=50, font_size=14):
    """
    :param master: родительский элемент (self.navbar)
    :param text: текст кнопки
    :param command: функция при нажатии
    :param y: вертикальная позиция в пикселях
    :param width: ширина кнопки
    :param height: высота кнопки (по умолчанию 50)
    :param font_size: размер шрифта (по умолчанию 14)
    :return: объект кнопки
    """
    btn = tk.Button(
        master,
        text=text,
        command=command,
        bg='#ffffff',
        fg='#000000',
        activebackground='#f0f0f0',
        relief='flat',
        bd=0,
        font=('Arial', font_size),
        anchor='center'
    )
    btn.place(x=5, y=y, width=width, height=height)

    def on_enter(e): btn.configure(bg='#f0f0f0')
    def on_leave(e): btn.configure(bg='#ffffff')

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn

def control_button(text, command, x, y, width=150, height=30, font_size=14):
    """
    :param text: текст кнопки
    :param command: функция при нажатии
    :param x: горизонтальная позиция в пикселях
    :param y: вертикальная позиция в пикселях
    :param width: ширина кнопки
    :param height: высота кнопки (по умолчанию 50)
    :param font_size: размер шрифта (по умолчанию 14)
    :return: объект кнопки
    """
    btn = tk.Button(
        text=text,
        command=command,
        bg='#ccffcc',
        fg='#000000',
        activebackground='#00ff00',
        relief='flat',
        bd=0,
        font=('Arial', font_size),
        anchor='center'
    )
    btn.place(x=x, y=y, width=width, height=height)

    def on_enter(e): btn.configure(bg='#00ff00')
    def on_leave(e): btn.configure(bg='#ccffcc')

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn

def get_control_button(text, command, x, y, width=240, height=30, font_size=14):
    """
    :param text: текст кнопки
    :param command: функция при нажатии
    :param x: горизонтальная позиция в пикселях
    :param y: вертикальная позиция в пикселях
    :param width: ширина кнопки
    :param height: высота кнопки (по умолчанию 50)
    :param font_size: размер шрифта (по умолчанию 14)
    :return: объект кнопки
    """
    btn = tk.Button(
        text=text,
        command=command,
        bg='#faffcc',
        fg='#000000',
        activebackground='#eaff00',
        relief='flat',
        bd=0,
        font=('Arial', font_size),
        anchor='center'
    )
    btn.place(x=x, y=y, width=width, height=height)

    def on_enter(e): btn.configure(bg='#eaff00')
    def on_leave(e): btn.configure(bg='#faffcc')

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn

def start_button(text, command, x, y, width=330, height=115, font_size=36):
    """
    :param text: текст кнопки
    :param command: функция при нажатии
    :param x: горизонтальная позиция в пикселях
    :param y: вертикальная позиция в пикселях
    :param width: ширина кнопки
    :param height: высота кнопки (по умолчанию 50)
    :param font_size: размер шрифта (по умолчанию 14)
    :return: объект кнопки
    """
    btn = tk.Button(
        text=text,
        command=command,
        bg='#ffcccc',
        fg='#000000',
        activebackground='#ff0000',
        relief='flat',
        bd=0,
        font=('Arial', font_size),
        anchor='center'
    )
    btn.place(x=x, y=y, width=width, height=height)

    def on_enter(e): btn.configure(bg='#ff0000')
    def on_leave(e): btn.configure(bg='#ffcccc')

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn

def end_button(text, command, x, y, width=330, height=115, font_size=36):
    """
    :param text: текст кнопки
    :param command: функция при нажатии
    :param x: горизонтальная позиция в пикселях
    :param y: вертикальная позиция в пикселях
    :param width: ширина кнопки
    :param height: высота кнопки (по умолчанию 50)
    :param font_size: размер шрифта (по умолчанию 14)
    :return: объект кнопки
    """
    btn = tk.Button(
        text=text,
        command=command,
        bg='#ffcccc',
        fg='#000000',
        activebackground='#ffcccc',
        relief='flat',
        bd=0,
        font=('Arial', font_size),
        anchor='center'
    )
    btn.place(x=x, y=y, width=width, height=height)

    def on_enter(e): btn.configure(bg='#ffcccc')
    def on_leave(e): btn.configure(bg='#ffcccc')

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn
