import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from pynput.keyboard import Controller
import os
import time
import urllib.request

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
if not os.path.exists(MODEL_PATH):
    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
    print("Downloading hand landmark model...")
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Download complete.")

base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options = mp_vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=mp_vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
landmarker = mp_vision.HandLandmarker.create_from_options(options)

keyboard = Controller()

cp = cv2.VideoCapture(0)
x1, x2, y1, y2 = 0, 0, 0, 0
frame_skip = 1
frame_count = 0
start_time = time.time()

while True:
    ret, image = cp.read()
    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    frame_count += 1

    if frame_count % frame_skip != 0:
        continue

    image_height, image_width, _ = image.shape
    image = cv2.flip(image, 1)
    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
    timestamp_ms = int((time.time() - start_time) * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if result.hand_landmarks:
        one_hand_landmark = result.hand_landmarks[0]

        for id, lm in enumerate(one_hand_landmark):
            x = int(lm.x * image_width)
            y = int(lm.y * image_height)

            if id == 12:
                x1 = x
                y1 = y
            if id == 0:
                x2 = x
                y2 = y

        distX = x1 - x2
        distY = y1 - y2

        if distY > -140 and distY != 0:
            keyboard.release('d')
            keyboard.release('a')
            keyboard.release('w')
            keyboard.press('s')
            print("Pressed Key: S")
        elif distY < -200 and distY != 0:
            keyboard.release('s')
            keyboard.release('d')
            keyboard.release('a')
            keyboard.press('w')
            print("Pressed Key: W")
        elif distX < -100 and distX != 0:
            keyboard.release('s')
            keyboard.release('d')
            keyboard.press('w')
            keyboard.press('a')
            print("Pressed Key: A")
        elif distX > 55 and distX != 0:
            keyboard.release('a')
            keyboard.release('s')
            keyboard.press('w')
            keyboard.press('d')
            print("Pressed Key: D")
    else:
        keyboard.release('d')
        keyboard.release('a')
        keyboard.release('w')
        keyboard.release('s')

    cv2.imshow("Camera Feed", image)

    q = cv2.waitKey(1)
    if q == ord("q"):
        break

landmarker.close()
cv2.destroyAllWindows()
cp.release()
