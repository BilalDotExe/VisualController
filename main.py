import cv2
import mediapipe as mp
import time
import math
import vgamepad as vg 

latest_result = None
last_timestamp_ms = -1
CONTROL_WINDOW = "Throttle Controls"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
gamepad = vg.VX360Gamepad()


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
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=2,
    min_hand_detection_confidence=0.45,
    min_hand_presence_confidence=0.40,
    min_tracking_confidence=0.40,
    result_callback=print_result
)

detector = HandLandmarker.create_from_options(options)

# ================= Opens Webcam ===================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

cv2.namedWindow(CONTROL_WINDOW)
# Default slider values:
# min_y starts at 0.02
# max_y starts at 0.75
cv2.createTrackbar("min_y", CONTROL_WINDOW, 200, 300, _noop)
cv2.createTrackbar("max_y", CONTROL_WINDOW, 380, 850, _noop)

smoothed_throttle = 0
try:
    # while loop
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
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

                cv2.putText(
                    frame,
                    hand_label,
                    (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

                # Use the swapped label because the webcam feed is mirrored.
                if hand_label == "Left":
                    # ============ LEFT HAND ==============
                    angle = math.degrees(
                        math.atan2(
                            middle_knuckle.y - wrist.y,
                            middle_knuckle.x - wrist.x
                        )
                    )

                    # ========== steering settings =============
                    max_deviation = 22
                    center_angle = -90
                    offset = 2
                    steering = ((angle - offset) - center_angle) / max_deviation
                    steering = max(-1.0, min(1.0, steering))

                    cv2.putText(
                        frame,
                        f"{steering:.1f}",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )

                    gamepad.left_joystick(
                        x_value=int(steering * 32767),
                        y_value=0
                    )
                    gamepad.update()
                    time.sleep(0.01)

                else:
                    # ============= RIGHT hand ====================
                    wrist = hand[0]
                    index_knuckle = hand[5]
                    pinky_knuckle = hand[17]
                    thumb_tip = hand[4]
                    thumb_knuckle = hand[2]


                    # building vectors for palm
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

                    # cross prod
                    normal_x = v1[1] * v2[2] - v1[2] * v2[1]
                    normal_y = v1[2] * v2[0] - v1[0] * v2[2]
                    normal_z = v1[0] * v2[1] - v1[1] * v2[0]

                    magnitude = math.sqrt(
                        normal_x**2 +
                        normal_y**2 +
                        normal_z**2
                    )
                    normal_y /= magnitude

                    # ==== smoothing (low pass filter) =====
                    # higher smoothed_throttle and lower normal_y value = smoother throttle response but laggier throttle
                    smoothed_throttle = (
                    smoothed_throttle * 0.5 + normal_y * 0.5
                )
                    throttle_input = -smoothed_throttle
                    print(f"raw: {smoothed_throttle:.4f} mapped: {throttle_input:.4f}")
                    min_y = trackbar_to_float(CONTROL_WINDOW, "min_y") - 0.10
                    max_y = trackbar_to_float(CONTROL_WINDOW, "max_y")

                    if min_y >= max_y:
                        max_y = min(min_y + 0.01, 0.85)

                    # ======= A button (thumb) ========
                    # when thumb is folded in, it emulated Xbox A button press
                    if thumb_tip.x > thumb_knuckle.x:
                        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                        gamepad.update()
                    else:
                        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                        gamepad.update()
                    

                    cv2.putText(
                        frame,
                        f"min_y: {min_y:.3f}",
                        (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )
                    cv2.putText(
                        frame,
                        f"max_y: {max_y:.3f}",
                        (50, 125),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )
                    cv2.putText(
                        frame,
                        f"raw_y: {throttle_input:.3f}",
                        (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )
                    
                    # clamping value between 0 and 1
                    throttle = (throttle_input - min_y) / (max_y - min_y)
                    throttle = max(0.0, min(1.0, throttle))

                    gamepad.right_trigger(
                        value=int(throttle * 255)
                    )
                    gamepad.update()
                    
                    cv2.putText(
                        frame,
                        f"throttle: {throttle:.2f}",
                        (50, 195),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2
                    )

# ========================= Drawing skeleton ======================================

                for connection in mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS:
                    start_lm = hand[connection.start]
                    end_lm = hand[connection.end]

                    start_x = int(start_lm.x * w)
                    start_y = int(start_lm.y * h)
                    end_x = int(end_lm.x * w)
                    end_y = int(end_lm.y * h)

                    cv2.line(
                        frame,
                        (start_x, start_y),
                        (end_x, end_y),
                        (255, 255, 255),
                        2
                    )

                for landmark in hand:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 0, 255),
                        -1
                    )

                # ========= Fingers IDs ===============
                finger_tips = [8, 12, 16, 20]
                thumb_tip = hand[4]
                thumb_x = int(thumb_tip.x * w)
                thumb_y = int(thumb_tip.y * h)

                for tip_id in finger_tips:
                    tip = hand[tip_id]
                    tip_x = int(tip.x * w)
                    tip_y = int(tip.y * h)

                    cv2.putText(
                        frame,
                        f"{tip_id}",
                        (tip_x + 3, tip_y + 3),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (250, 255, 252),
                        2
                    )

                    # Thumb ID
                    cv2.putText(
                        frame,
                        "4",
                        (thumb_x + 3, thumb_y + 3),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (250, 255, 252),
                        2
                    )

        cv2.imshow("Visual Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
