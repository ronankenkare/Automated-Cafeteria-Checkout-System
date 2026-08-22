# vendor/

Third-party code, kept in-tree so the Raspberry Pi can run the system offline.
Do not edit anything under here -- the project's own code lives in `src/`.

## yolov5

[Ultralytics YOLOv5](https://github.com/ultralytics/yolov5), AGPL-3.0
(`yolov5/LICENSE`). Used for its model definitions and inference utilities:
`src/config.py` puts this directory on `sys.path`, which is what makes
`from models.common import ...` and `from utils.general import ...` resolve.

Two things differ from a fresh upstream checkout:

- `detect.py` is gone. This project's modified copy of it is
  `src/food_detector.py`.
- `data/images/` and `runs/` are empty. The stock sample images and the run
  output that were there have moved to `results/`.

The pretrained `yolov5s.pt` weights live at `models/yolov5s.pt`.
