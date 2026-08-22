"""Shared paths for the cafeteria checkout system.

Every path here is anchored to the repository root, so the programs behave the
same no matter which directory they are launched from. Importing this module
also puts the vendored YOLOv5 tree on sys.path, which is what makes
`from models.common import ...` and `from utils.general import ...` resolve --
so import config *before* any YOLOv5 import.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"

# Vendored upstream YOLOv5 (unmodified, see vendor/yolov5/README.md)
YOLOV5_ROOT = REPO_ROOT / "vendor" / "yolov5"
if str(YOLOV5_ROOT) not in sys.path:
    sys.path.insert(0, str(YOLOV5_ROOT))

# Model
WEIGHTS = REPO_ROOT / "models" / "yolov5s.pt"
COCO_DATA = YOLOV5_ROOT / "data" / "coco128.yaml"
YOLOV5_REQUIREMENTS = YOLOV5_ROOT / "requirements.txt"

# Admin records
EMPLOYEE_DATA_CSV = REPO_ROOT / "data" / "admin" / "employee_data.csv"
FOOD_ITEMS_CSV = REPO_ROOT / "data" / "admin" / "food_items.csv"
TRANSACTIONS_CSV = REPO_ROOT / "data" / "admin" / "transactions.csv"

# Runtime working files
CAPTURE_DIR = REPO_ROOT / "data" / "captures"  # tray photos awaiting detection
DETECTED_FOODS_CSV = REPO_ROOT / "data" / "detected_foods.csv"  # detector -> checkout handoff
RUNS_DIR = REPO_ROOT / "results" / "runs"  # annotated detector output

CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
DETECTED_FOODS_CSV.touch(exist_ok=True)
