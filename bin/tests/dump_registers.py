import libs.bus_handler as bus_handler


bus = bus_handler.Bus(port='COM6', baudrate=460800)
slave_id = 1

print('Чтение регистров устройства...')

for reg in range(0x00, 0x10):
    try:
        result = bus.bus.execute(slave_id, 0x04, reg, 1)
        value = result[0]
        print(f'Регистр 0x{reg:02X}: {value}')
    except Exception as e:
        print(f'Ошибка чтения регистра 0x{reg:02X}: {e}')
