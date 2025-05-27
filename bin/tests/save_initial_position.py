import libs.Servo as Servo
import libs.bus_handler as bus_handler


# --- Настройки ---
PORT = 'COM6'
BAUDRATE = 460800
SERVO_ID = 10


try:
    master = bus_handler.Bus(port=PORT, baudrate=BAUDRATE, debug=False, timeout=1.0)
    servo = Servo.Servo(SERVO_ID, master.bus)

    # Получение текущих данных
    data = servo.get_data()
    if not data or 'Position' not in data:
        print('Ошибка: невозможно получить позицию сервопривода.')
        exit(1)

    position = data['Position']
    angle = position / 100  # т.к. DISTANCE_TO_POSITION_SCALE = 100

    # Сохраняем угол в файл
    with open('../app/initial_angle.txt', 'w') as f:
        f.write(str(angle))

    print(f'Текущая позиция сервопривода: {position} -> {angle:.2f}° записана как начальная.')
except Exception as e:
    print(f'Ошибка подключения: {e}')
    exit(1)
