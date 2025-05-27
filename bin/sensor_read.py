import libs.Ranger as Ranger
import libs.bus_handler as bus_handler


PORT = 'COM6'
BAUD = 460800
SENSOR_ID = 1

master = bus_handler.Bus(port=PORT, baudrate=BAUD)
sensor = Ranger.Sensor(SENSOR_ID, master.bus)

def read_distance():
    try:
        sensor.trig_sensor()
        # Небольшая пауза на обработку сигнала
        import time; time.sleep(0.05)
        data = sensor.read_sensor()
        return data['US_distance']  # Возвращает расстояние в см
    except Exception as e:
        print(f'Ошибка чтения с датчика: {e}')
        return float('inf')
