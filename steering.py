from config import MAX_DEVIATION, CENTER_ANGLE, STEERING_OFFSET
import math


def calculate_steering(wrist, middle_knuckle, deadzone) -> float:
    angle = math.degrees(
        math.atan2(
            middle_knuckle.y - wrist.y,
            middle_knuckle.x - wrist.x
        )
    )
    steering = ((angle - STEERING_OFFSET) - CENTER_ANGLE) / MAX_DEVIATION
    
    steering = max(-1.0, min(1.0, steering))    #clamping the value between -1.0 to 1.0
    if abs(steering) < deadzone:
        steering = 0.0
    else:
        steering = math.copysign(
            (abs(steering) - deadzone) / (1 - deadzone),
            steering
        )

        # Smoothstep smoothing
        t = abs(steering)
        t =t*t*(3-2*t)
        steering = math.copysign(t, steering)
    return steering