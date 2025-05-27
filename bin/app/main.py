import time
import math
import pygame
import os
import numpy as np
import libs.Servo as Servo
import libs.Ranger as Ranger
import libs.bus_handler as bus_handler
import serial.tools.list_ports
from bin.tracking_logic import FROM_TO_360, MOVE_TO_360, CYCLICAL


# --- Настройки конфигурации ---
def auto_detect_port(target_vid=0x0403, target_pid=0x6001):
    for port in serial.tools.list_ports.comports():
        if port.vid == target_vid and port.pid == target_pid:
            return port.device
    return None

PORT = auto_detect_port()

if PORT is None:
    print('[ОШИБКА]: Устройство не найдено. Проверьте подключение.')
    exit(1)
else:
    pass


BAUDRATE = 460800
SERVO_ID = 10
SENSOR_ID = 1
pygame.mixer.init() # Инициализация звука


# --- Соотношение градусов к позиции сервопривода ---
DISTANCE_TO_POSITION_SCALE = 100
SCAN_STEP = 0.5
DELAY = 0.005


try:
    # --- Инициализация устройств ---
    master = bus_handler.Bus(port=PORT, baudrate=BAUDRATE, debug=False, timeout=1.0)
    servo = Servo.Servo(SERVO_ID, master.bus)
    sensor = Ranger.Sensor(SENSOR_ID, master.bus)
    servo.set_torque(1)
except Exception as e:
    print(f'[ОШИБКА]: Не удалось инициализировать устройства. {e}')
    exit(1)


# --- Установка начальной позиции ---
try:
    with open('initial_angle.txt', 'r') as f:
        INITIAL_ANGLE = float(f.read().strip())

except Exception:
    INITIAL_ANGLE = 0  # значение по умолчанию, если файл не найден

initial_pos = int(INITIAL_ANGLE * DISTANCE_TO_POSITION_SCALE)
servo.set_point(initial_pos)
print(f'Обновление статуса. Установка начального положения: {INITIAL_ANGLE}°')
time.sleep(1.0)
print(f'Статус обновлён. Начальное положение установлено!')
time.sleep(0.5)


# --- Пауза 3 секунды перед стартом сканирования ---
print('Сканирование начнется через 3 секунды...')
time.sleep(3.0)


# --- Сканирование ---
print('Радар активен. Начало сканирования...')

current_angle = INITIAL_ANGLE
direction = 1
SCAN_DIRECTION = -1

def scan_angle(angle, virtual_angle, is_reverse=False):
    pos = int(angle * DISTANCE_TO_POSITION_SCALE)
    servo.set_point(pos)
    time.sleep(DELAY)

    sensor.trig_sensor()
    time.sleep(0.01)
    data = sensor.read_sensor()

    us = data.get('US_distance', 255)
    ir = data.get('IR_distance', 0)

    if 45 <= us <= 75:
        distance = us
        source = 'УЗ'
    elif 0 < ir <= 45:
        distance = ir
        source = 'ИК'
    else:
        distance = float('inf')
        source = 'Отсутствие объектов'

    if is_reverse:
        gui_angle = (360 - virtual_angle * 2) % 360
    else:
        gui_angle = (virtual_angle * 2) % 360

    if math.isfinite(distance):
        theta_rad = math.radians(gui_angle)
        x = distance * math.cos(theta_rad)
        y = distance * math.sin(theta_rad)
        print(f'Обнаружен объект. Угол: {gui_angle:}°,\n'
              f'Расстояние до объекта: {distance:.1f} см ({source}).\n'
              f'Координаты объекта: x = {x:.1f}, y = {y:.1f}\n')
    else:
        print(f'Угол: {gui_angle:}°, объекты не обнаружены.\n')

try:
    # --- Запуск фонового сканирующего звука ---
    sound_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "sounds", "scan_signal.MP3")
    sound_path = os.path.abspath(sound_path)
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play(-1)

    while True:
        # --- Прямой проход ---
        for angle in np.arange(0, MOVE_TO_360, SCAN_STEP):
            virtual_angle = angle
            scan_angle(angle, virtual_angle, is_reverse=False)

        # --- Обратный проход ---
        for angle in np.arange(FROM_TO_360 - SCAN_STEP, 0, -SCAN_STEP):
            virtual_angle = CYCLICAL - angle
            scan_angle(angle, virtual_angle, is_reverse=True)

except KeyboardInterrupt:
    pygame.mixer.music.stop()
    print('Программа завершена пользователем.')
