import cv2
import mediapipe as mp
import pyautogui
import time
import math

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose()

# Cooldown timers
cooldowns = {
    'jump': 0,
    'forward': 0,
    'left': 0,
    'right': 0,
    'back': 0
}

# Timing
last_frame_time = time.time()

def press_keys(keys):
    for key in keys:
        pyautogui.keyDown(key)
    time.sleep(0.1)
    for key in reversed(keys):
        pyautogui.keyUp(key)

def calculate_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

cap = cv2.VideoCapture(0)

print("Starting Assassin Controller. Press Q to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # mirror image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    current_time = time.time()
    delta = current_time - last_frame_time
    last_frame_time = current_time

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        # Landmarks
        nose = lm[mp_pose.PoseLandmark.NOSE]
        left_foot = lm[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
        right_foot = lm[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
        left_hand = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        right_hand = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip = lm[mp_pose.PoseLandmark.LEFT_HIP]  # or use average of both hips

        # Distance thresholds (you might need to tweak these)
        hand_distance = calculate_distance(left_hand, right_hand)
        shoulder_width = calculate_distance(left_shoulder, right_shoulder)

        # JUMP: arms stretched out + head moves up
        if hand_distance > shoulder_width * 1.8 and cooldowns['jump'] <= 0:
            print("🔺 JUMP detected → W + Shift + Space")
            press_keys(['w', 'shift', 'space'])
            cooldowns['jump'] = 1.5

        # MOVE FORWARD: nose goes upward fast (lean forward)
        if nose.y < hip.y - 0.1 and cooldowns['forward'] <= 0:
            print("⬆️ MOVE FORWARD → W")
            press_keys(['w'])
            cooldowns['forward'] = 1

        # MOVE LEFT: lean left
        if left_shoulder.x < hip.x - 0.05 and cooldowns['left'] <= 0:
            print("⬅️ LEFT → A")
            press_keys(['a'])
            cooldowns['left'] = 1

        # MOVE RIGHT: lean right
        if right_shoulder.x > hip.x + 0.05 and cooldowns['right'] <= 0:
            print("➡️ RIGHT → D")
            press_keys(['d'])
            cooldowns['right'] = 1

        # MOVE BACK: head moves back/down (like leaning)
        if nose.y > hip.y + 0.05 and cooldowns['back'] <= 0:
            print("⬇️ BACKWARD → S")
            press_keys(['s'])
            cooldowns['back'] = 1

    # Reduce cooldowns
    for k in cooldowns:
        if cooldowns[k] > 0:
            cooldowns[k] -= delta

    # Show preview
    cv2.imshow('AC IRL Controller', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
