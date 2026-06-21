# VisualController

This project uses a webcam, MediaPipe hand tracking, and a virtual Xbox 360 controller to turn hand motion into game controls.

Right now it does two main things:

- Left hand controls steering with the left joystick
- Right hand controls throttle with the right trigger

The app also shows a live camera window with the tracked hand skeleton and a separate slider window so you can tune throttle calibration on the fly.

## How It Works

- `main.py` opens your webcam with OpenCV
- MediaPipe detects up to two hands in real time
- The mirrored camera feed swaps the detected handedness labels so the controls feel natural on screen
- Left-hand tilt is converted into joystick steering
- Right-hand palm orientation is converted into throttle input
- `vgamepad` sends those values to a virtual Xbox 360 controller

## Requirements

- Windows
- Python 3.12+ recommended
- A webcam
- ViGEm Bus driver support for `vgamepad`

Python packages used by the project:

- `opencv-python`
- `opencv-contrib-python`
- `mediapipe`
- `vgamepad`

## Project Structure

```text
hand Controller/
|-- main.py
|-- models/
|   `-- hand_landmarker.task
`-- venv/
```

## Setup

1. Open a terminal in the project folder.
2. Create a virtual environment if you do not already have one:

```powershell
python -m venv venv
```

3. Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

4. Install the dependencies:

```powershell
pip install opencv-python opencv-contrib-python mediapipe vgamepad
```

5. Make sure the model file exists at `models/hand_landmarker.task`.

6. If `vgamepad` does not work, install the ViGEm Bus driver and then restart your machine if needed.

## How To Run

Start the app with:

```powershell
python main.py
```

Press `q` to quit.

## How To Use

When the app starts, you should see:

- A `Hand Detection` camera window
- A `Throttle Controls` slider window

### Steering

- Show your left hand to the camera
- Tilt your hand left or right
- The app maps that angle to the virtual controller's left joystick

### Throttle

- Show your right hand to the camera
- Rotate or pitch your hand to change the palm orientation
- The app maps that motion to the virtual controller's right trigger

### Live Throttle Tuning

The `Throttle Controls` window contains two sliders:

- `min_y`: adjustable from `-0.10` to `0.10`
- `max_y`: adjustable from `0.65` to `0.85`

Default values:

- `min_y = 0.02`
- `max_y = 0.75`

The camera window also shows:

- `min_y`
- `max_y`
- `raw_y`
- `throttle`

Use `raw_y` to see what your hand is producing, then adjust `min_y` and `max_y` until throttle responds the way you want.

## Notes

- The webcam index is currently set to `2` in `main.py`. If your camera does not open, try changing:

```python
cap = cv2.VideoCapture(2)
```

to:

```python
cap = cv2.VideoCapture(0)
```

or `1` depending on your system.

- The video feed is mirrored on purpose, which is why the code swaps MediaPipe's detected left/right labels before applying controls.

- If the throttle feels backwards, the sign or mapping of the right-hand palm normal may need to be flipped again depending on your camera setup and hand pose.

## Troubleshooting

### No camera feed

- Check the webcam index in `main.py`
- Make sure no other app is using the camera

### Hand tracking is unstable

- Improve lighting
- Keep your hand fully in frame
- Move a bit slower while testing

### No virtual controller input

- Confirm `vgamepad` is installed
- Confirm ViGEm Bus is installed correctly
- Test whether Windows can see the virtual Xbox controller

### Throttle stays at 0

- Watch the `raw_y` value in the camera window
- Adjust `min_y` lower or `max_y` lower if your hand never reaches the expected range
- If needed, inspect the right-hand mapping code in `main.py`

## Main File

The main application logic lives in [main.py](/C:/Users/bilal/Desktop/hand%20Controller/main.py).
