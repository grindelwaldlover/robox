import math


def find_target(measurements):
    return min(measurements, key=lambda m: m[1])  # (угол, расстояние)

def pol2cart(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y

MOVE_TO_360 = 180
FROM_TO_360 = 179
CYCLICAL = 360
