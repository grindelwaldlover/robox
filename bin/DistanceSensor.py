class DistanceSensor:
    def __init__(self, slave_id, bus):
        self.slave_id = slave_id
        self.bus = bus

    def get_distance(self):
        try:
            # Читаем регистр 0x03 — там находится расстояние
            result = self.bus.execute(self.slave_id, 0x03, 0x00, 1)
            return result[0]  # Значение в сантиметрах
        except Exception as e:
            raise Exception(f'Ошибка при получении расстояния с устройства {self.slave_id}: {e}')
