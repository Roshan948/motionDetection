# Motion Detection App

Opens the webcam and shows **Body in rest** when nothing moves, or **Motion detected** with the
direction (**Left, Right, Up, Down**) when something does. Built with Python, OpenCV and NumPy.
No machine-learning model is needed.

## Setup

Supported Python: **3.10 or newer** (tested on 3.12).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

For a reproducible install of the exact tested versions, use `pip install -r requirements.lock` instead.

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
python main.py --threshold 0.6       # less sensitive (percent of the frame that must change)
python main.py --min-shift 30        # steadier direction
python main.py --log                 # save state changes to logs/*.csv
```

Bad values are rejected at start-up with a readable message, for example
`Error: blur_kernel must be between 1 and 99 (got 500)`.

## Privacy and files

- The app only reads the webcam on this computer. It has no network code and **never saves video or images**.
- Your operating system may ask for camera permission the first time.
- With `--log`, a small CSV (`logs/motion_events_<timestamp>.csv`) records only the time, state
  (rest or motion), direction and percent of the frame that changed, and only when the state changes.
  Each run creates a new file, and only the newest 20 are kept (`--max-logs` changes that).

## Project structure

```
motion_detection_app/
├── main.py                 # command-line entry point
├── requirements.txt        # supported version ranges
├── requirements.lock       # exact tested versions
├── requirements-dev.txt    # adds pytest
├── requirements-ci.txt     # used by GitHub Actions
├── pytest.ini
├── .gitignore
├── motion_app/
│   ├── config.py           # every setting, with range checks
│   ├── camera.py           # stage 1: webcam capture, with retry on dropped frames
│   ├── preprocess.py       # stage 2: resize + grayscale + blur
│   ├── detector.py         # stages 3-4, 6: frame diff, threshold, score, centroid
│   ├── state.py            # stage 5: rest/motion decision with delay
│   ├── direction.py        # stages 7-8: centroid shift to direction
│   ├── pipeline.py         # connects all stages: frame in, result out
│   ├── overlay.py          # status banner and direction arrow
│   ├── event_log.py        # optional CSV log of state changes
│   └── app.py              # run loop and window handling
├── tests/                  # unit tests with synthetic frames (no webcam needed)
└── tools/benchmark.py      # per-stage timing on synthetic frames
```

## How it follows the architecture

1. **Webcam capture** (`camera.py`) reads a mirrored frame. A failed read is retried a few times;
   if the camera is really gone you get a clear error instead of a silent exit.
2. **Preprocess** (`preprocess.py`) resizes every frame to the same width (640 by default), then
   converts to grayscale and blurs. Because of the resize, all pixel-based settings behave the same
   on a 480p, 720p or 1080p camera.
3. **Frame diff** and 4. **Threshold** (`detector.py`) produce the motion mask and the share of the
   frame that changed.
5. **Decision** (`state.py`) says motion when that share passes the threshold, and rest only after
   `rest_delay_frames` still frames, which stops the label flickering.
6. **Centroid** (`detector.py`) finds the center of the moving area.
7. **Track shift** and 8. **Direction** (`direction.py`) compare the oldest and newest of the last
   6 centroids; the larger axis wins, and shifts inside the dead zone give no direction. The history
   is cleared after a short pause (`direction_reset_frames`), so a new movement is never compared
   with positions from before it.

## Tuning

All defaults are in `motion_app/config.py` and can be overridden from the command line.

| Setting | Default | Effect |
|---------|---------|--------|
| `motion_threshold_pct` | 0.33 | Percent of the frame that must change to count as motion. Raise it to ignore small movement. |
| `process_width` | 640 | Frames are resized to this width first. Lower is faster, higher keeps more detail. |
| `pixel_cutoff` | 25 | Brightness change a pixel needs to count as changed. |
| `blur_kernel` | 21 | Larger values remove more noise but blur small motion. |
| `rest_delay_frames` | 10 | Still frames before switching back to rest. |
| `history_length` | 6 | Frames used to measure direction. |
| `min_shift` | 20 | Dead zone in pixels (at `process_width`) for direction. |
| `direction_reset_frames` | 3 | Inactive frames in a row that clear the direction history. |
| `camera_read_retries` | 5 | Failed reads tolerated in a row before the app stops with an error. |
| `max_log_files` | 20 | Newest event logs kept. |

## Tests and benchmark

```bash
pip install -r requirements-dev.txt
pytest
python tools/benchmark.py
```

The benchmark times preprocessing, detection and the full pipeline on synthetic frames at 480p,
720p and 1080p. It does not include camera capture or window drawing, which depend on your hardware,
so run it on your own machine before quoting a frame rate.

## Limitations

- It detects any movement, not only people. Add a person detector (MediaPipe Pose or YOLO) to react to people only.
- Direction is most reliable for steady, deliberate movement, because the centroid of a frame difference sits between the old and new positions.
- Keep the camera fixed; shaking or auto-exposure changes cause false motion.
- Designed for one local webcam and one processing loop. Several cameras or remote streams would need capture and processing separated by bounded frame queues, with an explicit policy for dropping stale frames.
