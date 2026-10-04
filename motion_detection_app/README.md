# Motion Detection App

Opens the webcam and shows **Body in rest** when nothing moves, or **Motion detected** with the
direction (**Left, Right, Up, Down**) when something does. Built with Python, OpenCV and NumPy.
No machine-learning model is needed.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

| Key | Action |
|-----|--------|
| `q` | Quit |
| `m` | Show or hide the black and white motion mask (useful for tuning) |

Useful options (`python main.py --help` lists all of them):

```bash
python main.py --camera 1            # use a second webcam
python main.py --threshold 1500      # less sensitive
python main.py --min-shift 30        # steadier direction
python main.py --log                 # save state changes to logs/*.csv
```

## Project structure

```
motion_detection_app/
├── main.py                 # command-line entry point
├── requirements.txt        # runtime dependencies
├── requirements-dev.txt    # adds pytest
├── pytest.ini
├── .gitignore
├── motion_app/
│   ├── config.py           # every tunable setting in one place
│   ├── camera.py           # stage 1: webcam capture
│   ├── preprocess.py       # stage 2: grayscale + blur
│   ├── detector.py         # stages 3-4, 6: frame diff, threshold, score, centroid
│   ├── state.py            # stage 5: rest/motion decision with delay
│   ├── direction.py        # stages 7-8: centroid shift to direction
│   ├── pipeline.py         # connects all stages: frame in, result out
│   ├── overlay.py          # status banner and direction arrow
│   ├── event_log.py        # optional CSV log of state changes
│   └── app.py              # run loop and window handling
├── tests/                  # unit tests with synthetic frames (no webcam needed)
└── logs/                   # created automatically when --log is used
```

## How it follows the architecture

1. **Webcam capture** (`camera.py`) reads a mirrored frame.
2. **Preprocess** (`preprocess.py`) converts to grayscale and blurs.
3. **Frame diff** and 4. **Threshold** (`detector.py`) produce the motion mask and score.
5. **Decision** (`state.py`) says motion when the score passes the threshold, and rest only after
   `rest_delay_frames` still frames, which stops the label flickering.
6. **Centroid** (`detector.py`) finds the center of the moving area.
7. **Track shift** and 8. **Direction** (`direction.py`) compare the oldest and newest of the last
   6 centroids; the larger axis wins, and shifts inside the dead zone give no direction.

## Tuning

All defaults are in `motion_app/config.py` and can be overridden from the command line.

| Setting | Default | Effect |
|---------|---------|--------|
| `motion_threshold` | 1000 | Changed pixels needed for motion. Raise it to ignore small movement. |
| `pixel_cutoff` | 25 | Brightness change a pixel needs to count as changed. |
| `blur_kernel` | 21 | Larger values remove more noise but blur small motion. |
| `rest_delay_frames` | 10 | Still frames before switching back to rest. |
| `history_length` | 6 | Frames used to measure direction. |
| `min_shift` | 20 | Dead zone in pixels for direction. |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Limitations

- It detects any movement, not only people. Add a person detector (MediaPipe Pose or YOLO) to react to people only.
- Direction is most reliable for steady, deliberate movement, because the centroid of a frame difference sits between the old and new positions.
- Keep the camera fixed; shaking or auto-exposure changes cause false motion.
