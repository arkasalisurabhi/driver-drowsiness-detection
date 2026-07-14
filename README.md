# Driver Drowsiness Detection System

A real-time driver drowsiness detection system that uses facial landmark
detection to monitor eye state via a webcam, and alerts the driver with a
buzzer and LCD message through an Arduino when signs of drowsiness or
sleep are detected.

## How it works

1. A webcam feed is processed on a PC/laptop using **OpenCV** and **dlib**.
2. **dlib's 68-point facial landmark predictor** locates the eyes in each frame.
3. The Eye Aspect Ratio (EAR) is computed for both eyes to classify the
   driver's state as `ACTIVE`, `DROWSY`, or `SLEEPING`.
4. The state is sent over **serial (USB)** to an **Arduino**.
5. The Arduino displays the status on a **16x2 LCD** and triggers a
   **buzzer + LED** alert if the driver is drowsy or asleep.

```
Webcam --> driver.py (OpenCV + dlib, EAR calculation) --> Serial (USB)
                                                              |
                                                              v
                                            Arduino (driver.ino) --> LCD + Buzzer + LED
```

## Repository contents

| File          | Description                                              |
|---------------|-----------------------------------------------------------|
| `driver.py`   | Python script: captures webcam feed, detects drowsiness   |
| `driver.ino`  | Arduino sketch: reads serial signal, drives LCD/buzzer/LED |
| `requirements.txt` | Python dependencies                                   |
| `LICENSE`     | MIT license                                                |

## Hardware required

- Arduino Uno (or compatible)
- 16x2 LCD display (wired per `LiquidCrystal lcd(2, 3, 4, 5, 6, 7)`)
- Buzzer (connected to pin 8)
- LED (connected to pin 9)
- USB webcam
- Jumper wires, breadboard

## Software / library requirements

**Python side** (`requirements.txt`):
- opencv-python
- numpy
- dlib
- imutils
- pyserial

**Arduino side:**
- `LiquidCrystal` library (bundled with the Arduino IDE by default)

**Model file (required, not included in this repo):**
- `shape_predictor_68_face_landmarks.dat` — dlib's pretrained 68-point
  facial landmark model. Download it from:
  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
  then extract it and place it in the same folder as `driver.py`.

## Setup

### 1. Arduino side
1. Open `driver.ino` in the Arduino IDE.
2. Wire the LCD, buzzer, and LED as defined in the sketch (pins 2–7 for
   LCD, pin 8 for buzzer, pin 9 for LED).
3. Upload the sketch to your Arduino.
4. Note the COM port your Arduino is connected to (e.g. `COM5` on Windows,
   `/dev/ttyUSB0` on Linux).

### 2. Python side
```bash
git clone https://github.com/<your-username>/driver-drowsiness-detection.git
cd driver-drowsiness-detection
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
```

> **Note on dlib:** dlib can be tricky to install on Windows. If
> `pip install dlib` fails, install CMake and a C++ build toolchain first,
> or use a prebuilt wheel matching your Python version.

Download `shape_predictor_68_face_landmarks.dat` (see above) and place it
in the project root next to `driver.py`.

Open `driver.py` and update the serial port to match your Arduino:
```python
s = serial.Serial('COM5', 9600)  # change COM5 to your port
```

Also check the webcam index if the default doesn't work:
```python
cap = cv2.VideoCapture(1)  # try 0 if 1 doesn't open your camera
```

### 3. Run
```bash
python driver.py
```
Press **Esc** to quit the video window.

## How the detection logic works

For each eye, an Eye Aspect Ratio (EAR) is computed from 6 landmark points.
The ratio classifies each eye per frame as:
- **Open** (ratio > 0.25)
- **Semi-closed / blinking** (0.21 < ratio ≤ 0.25)
- **Closed** (ratio ≤ 0.21)

Counters (`sleep`, `drowsy`, `active`) accumulate consecutive frames in
each state. Once a counter crosses a threshold (6 consecutive frames):
- `SLEEPING !!` → sends `'a'` over serial → Arduino sounds buzzer + LED,
  shows "Please wake up" on the LCD.
- `DROWSY` → also sends `'a'` (same alert as sleeping).
- `ACTIVE` → sends `'b'` → Arduino shows "All Ok / Drive Safe", buzzer/LED off.

## Possible improvements

- Separate alert levels/sounds for `DROWSY` vs `SLEEPING`.
- Yawn detection using mouth landmarks.
- Head-pose estimation for distraction detection.
- Logging drowsiness events with timestamps for analysis.
- Replace HOG face detector with a faster/more robust CNN-based detector.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
