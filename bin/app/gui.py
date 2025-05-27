import ctypes
import ctypes.wintypes
import math
import datetime
import os
import re
import time
import tkinter as tk
import subprocess
import platform
import threading
import pygame
import serial
import serial.tools.list_ports
from tkinter import messagebox
from bin.app.front.custom_buttons import (sidebar_button, control_button,
                                          get_control_button, start_button,
                                          end_button)
from bin.app.front.custom_sidebar_separator import sidebar_separator


class RadarApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.logs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.logs_dir,
                                          f'RoboxLog_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.txt')
        self.log_file = open(self.log_file_path, 'a', encoding='utf-8')

        self.scan_process = None
        self.scan_thread = None
        self.scan_running = False
        self.status_label = None
        self.radar_beam_angle = 0  # текущий угол луча в градусах

        pygame.mixer.init()

        self.cm_to_px = 4  # 1 см = 4 пикселя (можно менять)
        self.max_radius_cm = 75
        self.dot_radius = 15  # Радиус точки (в пикселях)

        self.circle_color = '#4CAF50'  # Зелёный цвет кругов
        self.dot_color = '#FF0000'  # Красный цвет точки

        # ################################ НАСТРОЙКИ ################################
        self.title('Radar Scanner GUI')
        self.resizable(False, False)
        self.configure(bg='white')
        self.update_idletasks()

        work_area = ctypes.wintypes.RECT()
        spi_get_work_area = 48
        ctypes.windll.user32.SystemParametersInfoW(spi_get_work_area, 0, ctypes.byref(work_area), 0)

        work_width = work_area.right - work_area.left
        work_height = work_area.bottom - work_area.top
        window_width = 1280
        window_height = 720

        x = (work_width // 2) - (window_width // 2)
        y = (work_height // 2) - (window_height // 2)
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # ################################ САЙДБАР ################################
        self.navbar_width = 225
        self.window_height = 720
        self.navbar = tk.Frame(self, bg='#ffffff', width=self.navbar_width, height=self.window_height)
        self.navbar.place(x=0, y=0)

        self.navbar_border_x = tk.Frame(self.navbar, bg='#000000', width=1, height=self.window_height)
        self.navbar_border_x.place(x=self.navbar_width - 1, y=0)

        # --- Меню сайдбара ---
        sidebar_button(self.navbar, 'О программе', on_button_info)
        sidebar_button(self.navbar, 'Об авторе', on_button_author, y=60)
        sidebar_separator(self.navbar, y=115, width=self.navbar_width)
        sidebar_button(self.navbar, 'LIVE логирование', self.open_live_log_window, y=120)
        sidebar_button(self.navbar, 'Последние записи', self.open_logs_folder, y=175)
        sidebar_separator(self.navbar, y=230, width=self.navbar_width)

        # ################################ ОСНОВНОЕ ОКНО ################################
        # *************** КООРДИНАТНОЕ ПОЛЕ (X, Y) ***************
        self.canvas_width = 600
        self.canvas_height = 600
        self.canvas_origin_x = 300
        self.canvas_origin_y = 300

        self.coord_canvas = tk.Canvas(
            self,
            bg='#000000',
            width=self.canvas_width,
            height=self.canvas_height,
            highlightthickness=1,
            highlightbackground='#ffffff'
        )
        self.coord_canvas.place(x=675, y=5)

        self.coord_canvas.create_line(
            self.canvas_origin_x, 0,
            self.canvas_origin_x, self.canvas_height,
            fill='white', width=1
        )

        self.coord_canvas.create_line(
            0, self.canvas_origin_y,
            self.canvas_width, self.canvas_origin_y,
            fill='white', width=1
        )

        self.coord_canvas.create_text(self.canvas_origin_x + 5, self.canvas_origin_y + 8, text='0', font=('Arial', 10))
        self.coord_canvas.create_text(self.canvas_origin_x + 280, self.canvas_origin_y - 10, text='X', font=('Arial', 10))
        self.coord_canvas.create_text(self.canvas_origin_x + 10, self.canvas_origin_y - 280, text='Y', font=('Arial', 10))

        self.draw_radar_grid()

        # *************** ОКНО СОСТОЯНИЯ (КОНСОЛЬ / ТЕРМИНАЛ) ***************
        self.log_label = tk.Label(self, text='Отслеживание обнаруженных объектов (лог):', font=('Arial', 12, 'bold'), bg='#ffffff', anchor='w')
        self.log_label.place(x=230, y=580)

        self.log_text = tk.Text(
            self,
            font=('Consolas', 10),
            bg='#f7f7f7',
            fg='#111111',
            width=145,
            height=7,
            bd=1,
            relief='solid',
            wrap='word'
        )
        self.log_text.place(x=230, y=610)

        self.scrollbar = tk.Scrollbar(self, command=self.log_text.yview)
        self.scrollbar.place(x=1255, y=615, height=100)
        self.log_text.config(yscrollcommand=self.scrollbar.set)

        # *************** ОКНО УПРАВЛЕНИЯ ***************
        get_control_button('Обновить статус работы', self.check_connection, x=275, y=5)
        control_button('Очистить лог', self.clear_object_log, x=520, y=5)
        control_button('Очистить карту', self.clear_canvas, x=520, y=40)
        self.start_btn = start_button('Запуск\nсканирования', self.start_scan, x=285, y=175, width=330, height=115)
        self.start_btn.config(state='disabled')
        self.end_btn = end_button('Завершение\nсканирования', self.stop_scan, x=285, y=175, width=330, height=115)
        self.end_btn.place(x=-1000, y=-1000)

        self.log_label = tk.Label(self, text='Статус:', font=('Arial', 12, 'bold'), bg='#ffffff', anchor='w')
        self.log_label.place(x=285, y=300)
        self.status_label = tk.Label(self, text='Требует обновления', font=('Arial', 12, 'bold'), bg='#ffffff', fg='red', anchor='w')
        self.status_label.place(x=350, y=300)

        self.protocol('WM_DELETE_WINDOW', self.on_close)

        # --- Для кластеризации точек ---
        self.cluster = []
        self.cluster_timeout = 0.25  # секунд между точками в группе
        self.last_detection_time = time.time()

    def update_radar_beam(self):
        center_x = self.canvas_origin_x
        center_y = self.canvas_origin_y

        self.coord_canvas.delete('radar_beam')

        length = self.max_radius_cm * self.cm_to_px
        angle_rad = math.radians(self.radar_beam_angle)

        end_x = center_x + length * math.cos(angle_rad)
        end_y = center_y - length * math.sin(angle_rad)

        self.coord_canvas.create_line(center_x, center_y, end_x, end_y, fill='#00FF00', width=3, tag='radar_beam')

    def draw_detected_point(self, x_cm, y_cm):
        scale = 4  # 1 см = 4 пикселя
        radius = 4  # радиус точки

        # --- Преобразуем координаты в пиксели ---
        x_px = self.canvas_origin_x + x_cm * scale
        y_px = self.canvas_origin_y - y_cm * scale

        self.coord_canvas.create_oval(
            x_px - radius,
            y_px - radius,
            x_px + radius,
            y_px + radius,
            fill='#ff0000',  # красный
            outline='#ff0000'
        )

    def draw_radar_grid(self):
        # --- Центр радара ---
        center_x = self.canvas_origin_x
        center_y = self.canvas_origin_y

        for cm in range(10, self.max_radius_cm + 10, 10):
            r = cm * self.cm_to_px
            self.coord_canvas.create_oval(
                center_x - r, center_y - r,
                center_x + r, center_y + r,
                outline=self.circle_color
            )

        # --- Подписи осей ---
        for cm in range(0, self.max_radius_cm + 20, 10):
            offset = cm * self.cm_to_px
            label_color = '#ffffff' if cm <= self.max_radius_cm else '#888888'

            # X ось
            self.coord_canvas.create_text(center_x + offset, center_y + 10, text=str(cm), fill=label_color,
                                          font=('Arial', 8))
            self.coord_canvas.create_text(center_x - offset, center_y + 10, text=str(-cm), fill=label_color,
                                          font=('Arial', 8))

            # Y ось
            self.coord_canvas.create_text(center_x + 15, center_y - offset, text=str(cm), fill=label_color,
                                          font=('Arial', 8))
            self.coord_canvas.create_text(center_x + 15, center_y + offset, text=str(-cm), fill=label_color,
                                          font=('Arial', 8))

    def check_connection(self):
        # --- Целевые значения VID и PID ---
        TARGET_VID = 0x0403  # 1027
        TARGET_PID = 0x6001  # 24577

        target_port = None

        # --- Ищем порт с нужным VID и PID ---
        for port in serial.tools.list_ports.comports():
            if port.vid == TARGET_VID and port.pid == TARGET_PID:
                target_port = port.device
                break

        messagebox.showinfo(
            'Обновление статуса',
            'Проверка подключения завершена.\nСтатус был обновлён.\n\n'
            'Для обновления интерфейса нажмите кнопку "ОК",\nлибо закройте данное окно'
        )

        if not target_port:
            self.update_status('Устройство не найдено\n(нет драйвера или кабеля)', 'red')
            return

        try:
            with serial.Serial(port=target_port, baudrate=460800, timeout=1) as ser:
                if ser.is_open:
                    self.update_status(f'Готов к сканированию', 'green')
                else:
                    self.update_status('Интерфейс найден, но нет питания', 'orange')
        except (serial.SerialException, OSError):
            self.update_status('Интерфейс найден, но нет питания', 'orange')

    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)

        # --- Логика активации кнопки ---
        if text == 'Интерфейс подключён и запитан' or text == 'Готов к сканированию':
            self.start_btn.config(state='normal')
        else:
            self.start_btn.config(state='disabled')

    def play_detection_once(self):
        sound = pygame.mixer.Sound('resources/sounds/detection_signal.MP3')
        sound.play()

    def start_scan(self):
        if self.scan_running:
            return

        # --- Проверка статуса перед запуском ---
        if self.status_label.cget('text') != 'Готов к сканированию':
            messagebox.showwarning('Нет подключения',
                                    'Невозможно начать сканирование: отсутствует подключение к интерфейсу.')
            return

        self.update_status('Сканирование в процессе', "blue")
        self.scan_running = True
        self.end_btn.place(x=-1000, y=-1000)
        self.end_btn.place(x=285, y=175)

        def run_main():
            main_path = os.path.join(os.path.dirname(__file__), 'main.py')
            try:
                self.scan_process = subprocess.Popen(
                    ['python', '-u', main_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    encoding='utf-8'
                )
            except Exception as e:
                self.update_status('Требует обновления', 'red')
                messagebox.showerror('Ошибка запуска', f'Не удалось запустить сканирование.\n\nПричина: {e}')
                self.start_btn.config(state='disabled')
                return

            output_lines = []

            # --- Ожидание первых строк вывода или завершения ---
            for _ in range(10):
                if self.scan_process.poll() is not None:
                    break
                line = self.scan_process.stdout.readline()
                if line:
                    line = line.strip()
                    output_lines.append(line)

                    if 'Обнаружен объект' in line:
                        self.play_detection_once()
                        self.log_message(line, is_detection=True)

                    elif 'Расстояние до объекта' in line or 'Координаты объекта' in line:
                        self.log_message(line, is_detection=True)

                    if 'ERROR! Cant init servo:10' in line:
                        self.update_status('Устройство не запитано', 'red')
                        self.scan_running = False
                        self.scan_process.terminate()
                        self.end_btn.place(x=-1000, y=-1000)
                        self.start_btn.place(x=285, y=175)
                        self.start_btn.config(state='disabled')
                        messagebox.showerror('Ошибка', 'Сервопривод не запитан. Проверьте питание.')
                        return

                    if 'Обнаружен объект' in line:
                        self.play_detection_once()

            # --- Проверка, завершился ли процесс с ошибкой ---
            if self.scan_process.poll() is not None and self.scan_process.returncode != 0:
                self.scan_running = False
                self.end_btn.place(x=-1000, y=-1000)
                self.start_btn.place(x=285, y=175)
                self.start_btn.config(state='disabled')

                # --- Проверка по выводу ошибки ---
                for line in output_lines:
                    if 'ERROR! Cant init servo:10' in line or '[ОШИБКА]' in line:
                        self.update_status('Устройство не запитано', 'red')
                        messagebox.showerror('Ошибка запуска', 'Сервопривод не запитан или не подключен.')
                        return

                self.update_status('Ошибка запуска', 'red')
                messagebox.showerror('Ошибка запуска',
                                     'Ошибка при инициализации устройств.\nПроверьте питание и кабель.')
                return

            # --- Если всё ок, продолжаем читать вывод ---
            for line in self.scan_process.stdout:
                if not self.scan_running:
                    break
                line = line.strip()

                self.log_message(line)
                output_lines.append(line)

                if 'Обнаружен объект' in line:
                    self.play_detection_once()
                    self.log_message(line, is_detection=True)

                elif 'Расстояние до объекта' in line or 'Координаты объекта' in line:
                    self.log_message(line, is_detection=True)

                # --- Обработка критических ошибок во время работы ---
                if 'PermissionError' in line and 'Отказано в доступе' in line:
                    self.scan_running = False
                    self.scan_process.terminate()
                    self.update_status('АВАРИЙНЫЙ. Устройство потеряно.', 'red')
                    self.end_btn.place(x=-1000, y=-1000)
                    self.start_btn.place(x=285, y=175)
                    self.start_btn.config(state='disabled')
                    messagebox.showerror('Отключено',
                                         'Программа потеряла доступ к устройству.'
                                         '\n'
                                         '\nВозможные причины для этого:\n1. Отключение USB кабеля.\n2. Отключение внешнего питания')
                    return

                if 'Response length is invalid 0' in line:
                    self.scan_running = False
                    self.scan_process.terminate()
                    self.update_status('АВАРИЙНЫЙ. Устройство потеряно.', 'red')
                    self.end_btn.place(x=-1000, y=-1000)
                    self.start_btn.place(x=285, y=175)
                    self.start_btn.config(state='disabled')
                    messagebox.showerror('Отключено',
                                         'Программа потеряла доступ к устройству.'
                                         '\n'
                                         '\nВозможные причины для этого:\n1. Отключение USB кабеля.\n2. Отключение внешнего питания')
                    return

                if 'Обнаружен объект' in line:
                    self.play_detection_once()

                # --- Углы на холсте ---
                if 'Угол:' in line:
                    match = re.search(r'Угол:\s*(\d+)', line)
                    if match:
                        gui_angle = int(match.group(1))
                        self.radar_beam_angle = gui_angle % 360
                        self.coord_canvas.after(0, self.update_radar_beam)

                elif 'Координаты объекта' in line:
                    match = re.search(r'x\s*=\s*([-+]?\d+(?:\.\d+)?),\s*y\s*=\s*([-+]?\d+(?:\.\d+)?)', line, re.IGNORECASE)
                    if match:
                        x_cm = float(match.group(1))
                        y_cm = float(match.group(2))
                        print(f'[GUI] Отрисовка объекта: X={x_cm}, Y={y_cm}')
                        self.draw_detected_point(x_cm, y_cm)
                    else:
                        print(f'[GUI] Не удалось распознать координаты в строке: {line}')

            self.scan_process.wait()
            self.scan_running = False
            self.update_status('Сканирование завершено.\nОбновите статус работы.', 'orange')

        self.scan_thread = threading.Thread(target=run_main, daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        if self.scan_process:
            self.scan_running = False
            self.scan_process.terminate()
            self.update_status('Сканирование приостановлено', 'orange')
            self.end_btn.place(x=-1000, y=-1000)
            self.start_btn.place(x=285, y=175)

            # --- Повторная проверка ---
            if self.status_label.cget('text') == 'Готов к сканированию':
                self.start_btn.config(state='normal')
            else:
                self.start_btn.config(state='disabled')

    def on_close(self):
        self.stop_scan()
        self.destroy()

        if hasattr(self, 'log_file'):
            self.log_file.close()

    def clear_canvas(self):
        # --- Полная очистка холста ---
        self.coord_canvas.delete('all')

        # --- Восстановление координатных осей ---
        self.coord_canvas.create_line(
            self.canvas_origin_x, 0,
            self.canvas_origin_x, self.canvas_height,
            fill='white', width=1
        )
        self.coord_canvas.create_line(
            0, self.canvas_origin_y,
            self.canvas_width, self.canvas_origin_y,
            fill='white', width=1
        )
        self.coord_canvas.create_text(self.canvas_origin_x + 5, self.canvas_origin_y + 8, text='0', font=('Arial', 10))
        self.coord_canvas.create_text(self.canvas_origin_x + 280, self.canvas_origin_y - 10, text='X',
                                      font=('Arial', 10))
        self.coord_canvas.create_text(self.canvas_origin_x + 10, self.canvas_origin_y - 280, text='Y',
                                      font=('Arial', 10))

        # --- Перерисовать круговую сетку радара (если она есть) ---
        self.draw_radar_grid()

        # --- Очистка кластера ---
        self.cluster = []

    def log_message(self, text, is_detection=False):
        now = datetime.datetime.now().strftime('[%d.%m.%y]|[%H:%M:%S] ')
        log_line = now + text

        self.log_file.write(log_line + '\n')
        self.log_file.flush()

        if is_detection and hasattr(self, 'log_text'):
            try:
                self.log_text.insert('end', log_line + '\n')
                self.log_text.see('end')
            except tk.TclError:
                pass

        if hasattr(self, 'live_log_textbox'):
            try:
                self.live_log_textbox.insert('end', log_line + '\n')
                self.live_log_textbox.see('end')
            except tk.TclError:
                pass

    def clear_object_log(self):
        if hasattr(self, 'log_text'):
            self.log_text.delete('1.0', 'end')

    def open_live_log_window(self):
        if hasattr(self, 'live_log_window') and self.live_log_window.winfo_exists():
            self.live_log_window.lift()
            return

        self.live_log_window = tk.Toplevel(self)
        self.live_log_window.title('LIVE логирование')
        self.live_log_window.geometry('800x600')

        self.live_log_textbox = tk.Text(self.live_log_window, bg='black', fg='lime', font=('Consolas', 10))
        self.live_log_textbox.pack(expand=True, fill='both')

        def on_close_live_log():
            # --- Безопасное удаление виджетов ---
            if hasattr(self, 'live_log_textbox'):
                self.live_log_textbox.destroy()
                del self.live_log_textbox

            if hasattr(self, 'live_log_window'):
                self.live_log_window.destroy()
                del self.live_log_window

        self.live_log_window.protocol('WM_DELETE_WINDOW', on_close_live_log)

    def open_logs_folder(self):
        path = os.path.abspath(self.logs_dir)
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', path])
        else:
            subprocess.call(['xdg-open', path])


def on_button_info():
    messagebox.showinfo('О программе', 'Программа «Радарное сканирование с визуализацией» предназначена для управления ультразвуковым сканером на сервоприводе, визуализации луча и точек обнаружения объектов в реальном времени, а также отображения координат целей в полярной системе координат.\n\n'
                                       'Функции:\n'
                                       '- Автоматическое определение COM-порта подключённого устройства;\n'
                                       '- Интерактивная визуализация луча и целей на холсте;\n'
                                       '- Поддержка ИК и УЗ сенсоров;\n'
                                       '- Звуковое сопровождение процесса сканирования.\n\n'
                                       'Разработано в рамках выполнения выпускной квалификационной работы.')

def on_button_author():
    messagebox.showinfo('Об авторе', 'Автор: Яковицкий Владислав Анатольевич\n\n'
                                     'Учебное заведение: Гродненский Государственный Университет "имени Янки Купалы"\n\n'
                                     'Факультет: Физико-технический\n'
                                     'Кафедра: Электротехники и электроники')

def on_test():
    print('Тест (заглушка)')

def main():
    app = RadarApp()
    app.mainloop()

if __name__ == "__main__":
    main()
