"""Plugin to support ATORCH CW20 DC Meter (Smart Shunt)."""

import logging
from typing import Final

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.uuids import normalize_uuid_str

from aiobmsble.basebms import BaseBMS, BMSdp, BMSsample, BMSvalue, MatcherPattern

_LOGGER = logging.getLogger(__name__)


class CW20(BaseBMS):
    """ATORCH CW20 Smart Shunt implementation."""

    INFO_LEN: Final[int] = 36  # typical CW20 frame size

    _FIELDS: Final[tuple[BMSdp, ...]] = (
        BMSdp("voltage", 4, 3, False, lambda x: x / 10.0),       # 0.1 V
        BMSdp("current", 7, 3, True, lambda x: x / 1000.0),      # 0.001 A
        BMSdp("capacity", 10, 3, False, lambda x: x / 1000.0),   # 0.001 Ah
        BMSdp("energy", 13, 4, False, lambda x: x / 100.0),      # 0.01 kWh
        BMSdp("temperature", 24, 2, False, lambda x: x),         # °C
    )

    def __init__(self, ble_device: BLEDevice, keep_alive: bool = True) -> None:
        self._data_final: bytearray = bytearray()
        super().__init__(ble_device, keep_alive)

    # --------------------
    # Device identification
    # --------------------
    @staticmethod
    def matcher_dict_list() -> list[MatcherPattern]:
        return [
            MatcherPattern("CW20_BLE", normalize_uuid_str("ffe0"), True),
            MatcherPattern("ATORCH-CW20", normalize_uuid_str("ffe0"), True),
            MatcherPattern("CW20_BLE", normalize_uuid_str("fff0"), True),
            MatcherPattern("ATORCH-CW20", normalize_uuid_str("fff0"), True),
        ]

    @staticmethod
    def device_info() -> dict[str, str]:
        return {"manufacturer": "ATORCH", "model": "CW20 DC Meter"}

    @staticmethod
    def uuid_services() -> list[str]:
        return [normalize_uuid_str("ffe0"), normalize_uuid_str("fff0")]

    @staticmethod
    def uuid_rx() -> str:
        return normalize_uuid_str("ffe1")

    @staticmethod
    def uuid_tx() -> str:
        return ""

    @staticmethod
    def _calc_values() -> frozenset[BMSvalue]:
        return frozenset({"power"})

    # --------------------
    # Data handling
    # --------------------
    def _notification_handler(
        self, _sender: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        if not data.startswith(b"\xFF\x55"):
            return

        if len(data) >= CW20.INFO_LEN:
            self._data_final = data
            _LOGGER.debug("CW20 RX frame: %s", data.hex())
        else:
            _LOGGER.debug("CW20 RX frame too short: %s", data.hex())

    async def _async_update(self) -> BMSsample:
        data: BMSsample = {}

        if not self._data_final:
            return data

        data = CW20._decode_data(CW20._FIELDS, self._data_final)

        if "voltage" in data and "current" in data:
            data["power"] = round(data["voltage"] * data["current"], 2)

        return data
