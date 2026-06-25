import math
from config import THROTTLE_LAG, THROTTLE_RESPONSE

smoothed_throttle = 0.0

def calculate_throttle(wrist, index_knuckle, pinky_knuckle, min_y, max_y) -> float:
    global smoothed_throttle

    v1 = (
        index_knuckle.x - wrist.x,
        index_knuckle.y - wrist.y,
        index_knuckle.z - wrist.z
    )
    v2 = (
        pinky_knuckle.x - wrist.x,
        pinky_knuckle.y - wrist.y,
        pinky_knuckle.z - wrist.z
    )

    normal_x = v1[1]*v2[2] - v1[2]*v2[1]
    normal_y = v1[2]*v2[0] - v1[0]*v2[2]
    normal_z = v1[0]*v2[1] - v1[1]*v2[0]

    magnitude = math.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
    normal_y /= magnitude

    smoothed_throttle = smoothed_throttle * THROTTLE_LAG + normal_y * THROTTLE_RESPONSE
    throttle_input = -smoothed_throttle

    throttle = (throttle_input - min_y) / (max_y - min_y)
    return max(0.0, min(1.0, throttle))