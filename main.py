import cv2
import mediapipe as mp
import pyautogui
import time
import math

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose()

cooldowns = {
    'jump': 0,
    'forward': 0,
    'left': 0,
    'right': 0,
    'back': 0,
    'scholar': 0,
    'combat': 0,
    'stab_start': None,
    'last_clap_time': 0
}

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

print("🎮 Assassin Controller Activated — Press Q to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    current_time = time.time()
    delta = current_time - last_frame_time
    last_frame_time = current_time

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        nose = lm[mp_pose.PoseLandmark.NOSE]
        left_foot = lm[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
        right_foot = lm[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
        left_hand = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        right_hand = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        hip = left_hip


        if nose.y < hip.y - 0.1 and cooldowns['forward'] <= 0:
            print("⬆️ Forward → W")
            press_keys(['w'])
            cooldowns['forward'] = 1

        if nose.y > hip.y + 0.05 and cooldowns['back'] <= 0:
            print("⬇️ Back → S")
            press_keys(['s'])
            cooldowns['back'] = 1

        if left_shoulder.x < hip.x - 0.05 and cooldowns['left'] <= 0:
            print("⬅️ Left → A")
            press_keys(['a'])
            cooldowns['left'] = 1

        if right_shoulder.x > hip.x + 0.05 and cooldowns['right'] <= 0:
            print("➡️ Right → D")
            press_keys(['d'])
            cooldowns['right'] = 1

        hand_distance = calculate_distance(left_hand, right_hand)
        shoulder_width = calculate_distance(left_shoulder, right_shoulder)

        if hand_distance < 0.05 and cooldowns['scholar'] <= 0:
            print("🕊️ Scholar Mode → W + Space")
            press_keys(['w', 'space'])
            cooldowns['scholar'] = 1.5

        if hand_distance < 0.05:
            if cooldowns['last_clap_time'] == 0:
                cooldowns['last_clap_time'] = current_time
            elif current_time - cooldowns['last_clap_time'] < 1 and cooldowns['combat'] <= 0:
                print("⚔️ Combat Mode Activated → F")
                pyautogui.press('f')
                cooldowns['combat'] = 2
                cooldowns['last_clap_time'] = 0
        else:
            cooldowns['last_clap_time'] = 0

        if nose.y < hip.y - 0.15 and cooldowns['jump'] <= 0:
            print("🏃 Parkour Mode → W + Shift + Space")
            press_keys(['w', 'shift', 'space'])
            cooldowns['jump'] = 1.5

        if cooldowns['stab_start'] is None and right_hand.x < hip.x - 0.1:
            cooldowns['stab_start'] = (right_hand, current_time)

        if cooldowns['stab_start']:
            stab_start_hand, stab_start_time = cooldowns['stab_start']
            if current_time - stab_start_time < 1:
                if right_hand.x > hip.x + 0.05 and right_hand.y < stab_start_hand.y - 0.1:
                    print("🗡️ Assassinate → Left Click")
                    pyautogui.click()
                    cooldowns['stab_start'] = None
            else:
                cooldowns['stab_start'] = None

    for key in cooldowns:
        if isinstance(cooldowns[key], (int, float)) and cooldowns[key] > 0:
            cooldowns[key] -= delta

    cv2.imshow('Assassin IRL Controller', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
