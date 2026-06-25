from config import *
import cv2
import mediapipe as mp
import time
import numpy as np
from hud import draw_skeleton, draw_finger_ids, draw_hand_label, draw_steering_info, draw_throttle_info
from gamepad import steeringControl, throttleControl, press_a, release_a
from steering import calculate_steering
from throttle import calculate_throttle

latest_result = None
last_timestamp_ms = -1
CONTROL_WINDOW = "Throttle Controls"
show_camera = True

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode



def _noop(_value):
    pass


def trackbar_to_float(window_name, trackbar_name):
    return cv2.getTrackbarPos(trackbar_name, window_name) / 1000.0

# debug output
def print_result(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

# options
options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=NUM_HANDS,
    min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_hand_presence_confidence=MIN_PRESENCE_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    result_callback=print_result
)

detector = HandLandmarker.create_from_options(options)

# ================= Opens Webcam ===================
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

cv2.namedWindow(CONTROL_WINDOW)
# Default slider values:
# min_y starts at 0.02
# max_y starts at 0.75
cv2.createTrackbar("min_y", CONTROL_WINDOW, 200, 300, _noop)
cv2.createTrackbar("max_y", CONTROL_WINDOW, 380, 850, _noop)
cv2.createTrackbar("deadzone", CONTROL_WINDOW, 70, 200, _noop)

smoothed_throttle = 0
try:
    # while loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        camera_layer = frame.copy()
        overlay_layer = np.zeros_like(frame)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame
        )

        timestamp_ms = time.monotonic_ns() // 1_000_000
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms

        detector.detect_async(mp_image, timestamp_ms)

        # ========= Draw Skeleton ===================
        if latest_result and latest_result.hand_landmarks:
            h, w, _ = frame.shape

            for hand, handedness in zip(latest_result.hand_landmarks, latest_result.handedness):
                if not handedness:
                    continue

                wrist = hand[0]
                middle_knuckle = hand[9]
                detected_label = handedness[0].category_name

                hand_label = "Left" if detected_label == "Right" else "Right"
                
                label_x = int(wrist.x * w)
                label_y = int(wrist.y * h) - 20

                draw_hand_label(overlay_layer, hand_label, label_x, label_y)

                # Use the swapped label because the webcam feed is mirrored.
                if hand_label == "Left":
                    # ============ LEFT HAND ==============
                    deadzone = trackbar_to_float(CONTROL_WINDOW, "deadzone")
                    steering = calculate_steering(wrist, middle_knuckle, deadzone)

                    draw_steering_info(overlay_layer, steering)

                    steeringControl(steering)

                else:
                    # ============= RIGHT hand ====================
                    wrist = hand[0]
                    index_knuckle = hand[5]
                    pinky_knuckle = hand[17]
                    thumb_tip = hand[4]
                    thumb_knuckle = hand[2]

                    min_y = trackbar_to_float(CONTROL_WINDOW, "min_y") - 0.10
                    max_y = trackbar_to_float(CONTROL_WINDOW, "max_y")

                    if min_y >= max_y:
                        max_y = min(min_y + 0.01, 0.85)

                    throttle = calculate_throttle(wrist, index_knuckle, pinky_knuckle, min_y, max_y)

                    # ======= A button (thumb) ========
                    # when thumb is folded in, it emulated Xbox A button press
                    if thumb_tip.x > thumb_knuckle.x:
                        press_a()
                    else:
                        release_a()
                
                    throttleControl(throttle)
                    draw_throttle_info(overlay_layer, throttle, min_y, max_y)
                    
                   
# ========================= Drawing skeleton =====================================
                draw_skeleton(overlay_layer, hand, w, h)
                draw_finger_ids(overlay_layer, hand, w, h)

        base_layer = camera_layer if show_camera else np.zeros_like(camera_layer)
        display = cv2.add(base_layer, overlay_layer)
        cv2.imshow("Visual Controller", display)

        key = cv2.waitKey(1) & 0xFF 
        if key == ord("q"):
            break
        if key == ord("v"):
            show_camera = not show_camera
finally:
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
