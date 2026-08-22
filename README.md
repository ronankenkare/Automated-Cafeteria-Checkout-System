# Automated Cafeteria Checkout System

CS 437 (IoT) final project. A Raspberry Pi replaces the cashier in a corporate
cafeteria: an employee scans their RFID badge, a camera photographs their tray,
YOLOv5 identifies the food on it, and the total is charged to their account
without anyone standing in line.

The background and the original work plan are in
[docs/project-proposal.md](docs/project-proposal.md).

## How it works

`src/cafeteria_checkout.py` is the system. It loops over one transaction at a
time:

1. **Identify** — listens on TCP `192.168.88.191:12345` for the RFID reader to
   send a badge ID, then looks the employee up in
   `data/admin/employee_data.csv`.
2. **Capture** — counts down, takes a photo of the tray with the Pi camera, and
   writes it to `data/captures/`.
3. **Detect** — shells out to `src/food_detector.py` with that one photo as its
   source, and it appends every food it recognizes to `data/detected_foods.csv`.
   An annotated copy of the photo lands in `results/runs/`.
4. **Charge** — prices those items against `data/admin/food_items.csv` and appends
   the sale to `data/admin/transactions.csv`.
5. **Reset** — clears the detection list, deletes the tray photo and the run
   output, and waits for the next employee.

Food recognition uses stock YOLOv5s against the COCO classes; the ten COCO labels
treated as cafeteria items are listed in `FOOD_ITEMS` at the top of
`src/food_detector.py`.

## Layout

```
src/
  cafeteria_checkout.py            main program -- start here
  food_detector.py                 YOLOv5 detect.py, forked to log foods to CSV
  config.py                        every filesystem path, anchored to the repo root
  prototypes/
    webcam_food_detection.py       archived first attempt, not wired in
data/
  admin/                           employee, menu, and transaction records
  captures/                        tray photos awaiting detection (runtime)
  detected_foods.csv               detector -> checkout handoff (runtime)
models/yolov5s.pt                  pretrained weights
results/
  captures/                        raw tray photos from the December demo
  detections/                      annotated output of those runs (exp3-exp5)
  early_tests/                     first detector runs, before the tray pipeline
docs/                              proposal write-up and PDF
vendor/yolov5/                     upstream YOLOv5, unmodified -- see vendor/README.md
```

Nothing depends on the working directory anymore. `src/config.py` resolves every
path from the repo root and puts `vendor/yolov5` on `sys.path`, so the programs
can be launched from anywhere.

## Running it

Hardware: Raspberry Pi with the camera module, plus an RFID reader on the same
network that connects to port 12345 and sends the badge ID as UTF-8 text.

```bash
pip install -r requirements.txt
```

```bash
python3 src/cafeteria_checkout.py
```

To test detection alone, off the Pi, point the detector at the saved demo photos:

```bash
python3 src/food_detector.py --source results/captures
```

## Known issues

- **The RFID reader's client code is not in this repo** — only the Pi-side server
  that receives the scan.
- The reader's IP is hardcoded as a default argument in `start_server`.
