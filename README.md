# aio-smartshunt

Asyncio-based drivers for **smart shunts / DC meters** over Bluetooth Low Energy.

This package reuses the `aiobmsble` base framework but provides support for **non-BMS devices**,  
starting with the **ATORCH CW20 DC Meter**.

## Features
- Decode CW20 BLE frames (voltage, current, energy, capacity, temperature).
- Provide derived values (power, charging/discharging).
- Compatible with `aiobmsble` patterns.

## Installation
```bash
pip install aio-smartshunt
