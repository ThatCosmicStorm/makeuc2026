# Copyright 2026 Vision Ventures
"""*Main script for microcontroller*."""

import time

from machine import ADC, I2C, Pin
from vl53l0x import VL53L0X

try:
    from micropython import const
except ImportError:
    const = lambda x: x  # noqa: E731


CLEAR_TERMINAL = const("\033[2J\033[H")

PIN_PRESSURE = const(1)
PIN_LDR_1 = const(4)
PIN_LDR_2 = const(5)
PIN_UV_LED = const(6)
PIN_DIST_DATA = const(9)
PIN_DIST_CLOCK = const(18)

PROGRAM_RUNNING = const(1)

DISTANCE_ERROR_MESSAGE: str = (
    f"Check PINs: VIN, GND, SCL - {PIN_DIST_CLOCK}, SDA - {PIN_DIST_DATA}"
)


def toggle(pin: Pin) -> None:
    """*Toggle a pin*.

    If off, turn it on.
    If on, turn it off.

    Args:
        pin (Pin): **

    """
    pin.value(not pin.value())


def clear_terminal() -> None:
    """*Clear the entire terminal screen*."""
    print(CLEAR_TERMINAL, end="")


def main() -> None:
    """*Run the program*."""
    clear_terminal()

    error_messages: list[str] = []

    is_distance_working: bool = True
    try:
        distance: VL53L0X = VL53L0X(
            I2C(
                0,
                scl=Pin(PIN_DIST_CLOCK),
                sda=Pin(PIN_DIST_DATA),
                freq=100_000,
            ),
        )
    except OSError:
        error_messages.extend(
            ("Distance sensor not wired correctly.", DISTANCE_ERROR_MESSAGE),
        )
        is_distance_working: bool = False

    uv_led: Pin = Pin(PIN_UV_LED, mode=Pin.OUT)
    uv_led.off()

    ldr_1: ADC = ADC(Pin(PIN_LDR_1))
    ldr_2: ADC = ADC(Pin(PIN_LDR_2))
    pressure: ADC = ADC(Pin(PIN_PRESSURE))
    for sensor in (ldr_1, ldr_2, pressure):
        sensor.atten(ADC.ATTN_11DB)

    try:
        while PROGRAM_RUNNING:
            print("\033[H", end="")
            print(
                f"""Distance: {
                    distance.read_range_single_millimeters()
                    if is_distance_working
                    else "N/A":<4} mm""",
                f"LDR 1: {ldr_1.read():<4} ohms",
                f"LDR 2: {ldr_2.read():<4} ohms",
                f"Pressure: {pressure.read():<4} ohms",
                f"LED Indicator: {uv_led.value():<1}",
                sep="\n",
            )
            toggle(uv_led)
            time.sleep_ms(100)
    except KeyboardInterrupt:
        pass
    except OSError:
        error_messages.extend(
            ("Distance sensor disconnected.", DISTANCE_ERROR_MESSAGE),
        )
    finally:
        clear_terminal()
        print("\n".join(error_messages))


if __name__ == "__main__":
    main()
