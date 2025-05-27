import libs.bus_handler as bus_handler
import time


def scan_rs485_addresses(port='COM6', baudrate=460800):
    print('Сканирование шины RS-485...')
    bus = bus_handler.Bus(port=port, baudrate=baudrate)
    found = []

    for addr in range(1, 50):
        try:
            import libs.Servo as Servo
            device = Servo.Servo(addr, bus.bus)
            position = device.get_position()
            print(f'Устройство найдено по адресу {addr} — позиция серво: {position}')
            found.append(addr)
        except Exception as e:
            pass
        time.sleep(0.1)

    if not found:
        print('Ни одного устройства не найдено.')
    else:
        print(f'Найденные адреса: {found}')

if __name__ == "__main__":
    scan_rs485_addresses()
