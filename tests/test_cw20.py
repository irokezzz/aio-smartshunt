import sys
import pathlib
import json
import asyncio
from types import SimpleNamespace

# 🔹 Додаємо src у PYTHONPATH
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from aio_smartshunt.cw20 import CW20


def load_frames():
    """Load test frames from JSON file."""
    path = pathlib.Path(__file__).parent / "data" / "cw20_bms.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)["frames"]


def test_cw20_decode_frames():
    """Decode known CW20 frames and compare with expected values."""
    dev = SimpleNamespace(address="00:11:22:33:44:55", name="CW20_BLE")
    bms = CW20(dev)

    for frame in load_frames():
        raw = bytes.fromhex(frame["hex"])
        bms._notification_handler(None, raw)  # simulate BLE notify
        sample = asyncio.run(bms._async_update())

        for key, expected in frame["expected"].items():
            assert key in sample
            assert abs(sample[key] - expected) < 0.01, f"{key}: {sample[key]} != {expected}"
