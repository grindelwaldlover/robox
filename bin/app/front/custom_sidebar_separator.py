import tkinter as tk


def sidebar_separator(master, y, width, color='#000000', height=1):
    """
    :param master: родительский фрейм (self.navbar)
    :param y: вертикальная позиция
    :param width: ширина разделителя
    :param color: цвет линии (по умолчанию чёрный)
    :param height: толщина линии (в пикселях)
    :return: объект Frame (разделитель)
    """
    line = tk.Frame(master, bg=color, width=width, height=height)
    line.place(x=0, y=y)
    return line
