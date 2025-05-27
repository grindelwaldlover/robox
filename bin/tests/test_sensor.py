import time
import Ranger
import bus_handler


# --- Параметры подключения ---
PORT = 'COM6'
SENSOR_ID = 1

# --- Инициализация шины и датчика ---
master = bus_handler.Bus(port=PORT, baudrate=460800)
sensor = Ranger.Sensor(SENSOR_ID, master.bus)

# --- Чтение данных ---
while True:
    sensor.trig_sensor()
    time.sleep(0.03)

    try:
        data = sensor.read_sensor()
        print('Сырые данные от датчика:', data)
    except Exception as e:
        print(f'Ошибка при чтении: {e}')

    time.sleep(0.5)
