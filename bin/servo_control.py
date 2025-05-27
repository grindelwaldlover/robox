import libs.Servo as Servo
import libs.bus_handler as bus_handler


class ServoController:
    def __init__(self, port='COM6', servo_id=10):
        self.master = bus_handler.Bus(port=port, baudrate=460800)
        self.servo = Servo.Servo(servo_id, self.master.bus)

    def enable(self):
        self.servo.set_torque(1)

    def move_to(self, point):
        self.servo.set_point(point)

    def angle_to_position(self, angle_deg):
        # Пример пересчёта: 1 градус = 45.45 единиц (зависит от серво!)
        return int(angle_deg * 45)
