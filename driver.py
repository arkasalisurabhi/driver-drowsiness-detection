import cv2
import numpy as np
import dlib
from imutils import face_utils
import serial

# ---------------- Serial setup ----------------
try:
    s = serial.Serial('COM5', 9600)  # <-- change to your actual COM port (COM3/COM4/etc.)
except Exception:
    print("Warning: Serial port not found. Continuing without serial...")
    s = None

# ---------------- Camera setup ----------------
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("ERROR: Camera not opening. Try VideoCapture(0) or another index.")
    exit()

# ---------------- Load detectors ----------------
try:
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except Exception:
    print("ERROR: shape_predictor_68_face_landmarks.dat not found!")
    exit()

hog_face_detector = dlib.get_frontal_face_detector()


def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)


def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2  # eye open
    elif 0.21 < ratio <= 0.25:
        return 1  # semi-closed / blinking
    else:
        return 0  # eye closed


sleep = drowsy = active = 0
status = ""
color = (0, 0, 0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Frame not received!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = hog_face_detector(gray)

    for face in faces:
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        left_blink = blinked(landmarks[36], landmarks[37],
                              landmarks[38], landmarks[41],
                              landmarks[40], landmarks[39])

        right_blink = blinked(landmarks[42], landmarks[43],
                               landmarks[44], landmarks[47],
                               landmarks[46], landmarks[45])

        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                if s:
                    s.write(b'a')
                status = "SLEEPING !!"
                color = (0, 0, 255)

        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                if s:
                    s.write(b'a')
                status = "DROWSY"
                color = (0, 0, 255)

        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                if s:
                    s.write(b'b')
                status = "ACTIVE"
                color = (0, 255, 0)

        cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, color, 3)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
