# hud.py
import cv2
import mediapipe as mp

def draw_skeleton(overlay, hand, w, h):
    for connection in mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS:
        start_lm = hand[connection.start]
        end_lm = hand[connection.end]
        cv2.line(
            overlay,
            (int(start_lm.x * w), int(start_lm.y * h)),
            (int(end_lm.x * w), int(end_lm.y * h)),
            (255, 255, 255), 2
        )
    for landmark in hand:
        cv2.circle(
            overlay,
            (int(landmark.x * w), int(landmark.y * h)),
            5, (0, 0, 255), -1
        )

def draw_finger_ids(overlay, hand, w, h):
    finger_tips = [8, 12, 16, 20]
    thumb_tip = hand[4]
    thumb_x = int(thumb_tip.x * w)
    thumb_y = int(thumb_tip.y * h)

    for tip_id in finger_tips:
        tip = hand[tip_id]
        cv2.putText(overlay, f"{tip_id}",
            (int(tip.x * w) + 3, int(tip.y * h) + 3),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 255, 252), 2)

    cv2.putText(overlay, "4",
        (thumb_x + 3, thumb_y + 3),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (250, 255, 252), 2)

def draw_hand_label(overlay, hand_label, label_x, label_y):
    cv2.putText(overlay, hand_label,
        (label_x, label_y),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

def draw_steering_info(overlay, steering):
    cv2.putText(overlay, f"{steering:.1f}",
        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

def draw_throttle_info(overlay, throttle, min_y, max_y):
    cv2.putText(overlay, f"min_y: {min_y:.3f}",    (50, 90),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(overlay, f"max_y: {max_y:.3f}",    (50, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(overlay, f"throttle: {throttle:.2f}", (50, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)