# Copyright 2026 Vision Ventures
"""*Main script for microcontroller*."""

import time

import bluetooth
from machine import ADC, I2C, Pin
from vl53l0x import VL53L0X

try:
    from micropython import const
except ImportError:
    const = lambda x: x  # noqa: E731


CLEAR_TERMINAL = const("\033[2J\033[H")

PIN_PRESSURE = const(1)
PIN_LDR_1 = const(0)
PIN_LDR_2 = const(5)
PIN_UV_LED = const(6)
PIN_DIST_DATA = const(9)
PIN_DIST_CLOCK = const(10)

IRQ_CENTRAL_CONNECT = const(1)
IRQ_CENTRAL_DISCONNECT = const(2)
IRQ_GATTS_WRITE = const(3)

PROGRAM_RUNNING = const(1)

DISTANCE_ERROR_MESSAGE: str = (
    f"Check PINs: VIN, GND, SCL - {PIN_DIST_CLOCK}, SDA - {PIN_DIST_DATA}"
)

UART_UUID: bluetooth.UUID = bluetooth.UUID(
    "6E400001-B5A3-F393-E0A9-E50E24DCCA9E",
)
TX_UUID: bluetooth.UUID = bluetooth.UUID(
    "6E400003-B5A3-F393-E0A9-E50E24DCCA9E",
)
RX_UUID: bluetooth.UUID = bluetooth.UUID(
    "6E400002-B5A3-F393-E0A9-E50E24DCCA9E",
)


SERVICE_LAYOUT: tuple[
    bluetooth.UUID,
    tuple[tuple[bluetooth.UUID, int], tuple[bluetooth.UUID, int]],
] = (
    UART_UUID,
    (
        (TX_UUID, bluetooth.FLAG_NOTIFY),
        (RX_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE),
    ),
)


def clear_terminal() -> None:
    """*Clear the entire terminal screen*."""
    print(CLEAR_TERMINAL, end="")


def toggle(pin: Pin) -> None:
    """*Toggle a pin*.

    If off, turn it on.
    If on, turn it off.

    Args:
        pin (Pin): *`Pin` object—not just an `int`*

    """
    pin.value(not pin.value())


# class BLEUARTServer:
#     def __init__(self):
#         self.ble: bluetooth.BLE = bluetooth.BLE()
#         self.ble.active(True)  # noqa: FBT003
#         self.ble.irq(self.irq)
#         ((self.tx_handle, self.rx_handle),) = self.ble.gatts_register_services(
#             (SERVICE_LAYOUT,),
#         )
#         self.connections: set = set()
#         self.payload: str = "XIAO_BLE"
#         self.advertise()

#     def irq(self, event: int, data: tuple[memoryview[int], ...]) -> None:
#         if event == IRQ_CENTRAL_CONNECT:
#             conn_handle, _, _ = data
#             print("Connected to central:", conn_handle)
#             self.connections.add(conn_handle)
#         elif event == IRQ_CENTRAL_DISCONNECT:
#             conn_handle, _, _ = data
#             print("Disconnected from central:", conn_handle)
#             self.connections.remove(conn_handle)
#             self.advertise()
#         elif event == IRQ_GATTS_WRITE:
#             conn_handle, value_handle = data
#             if value_handle != self.rx_handle:
#                 return
#             incoming_data = self.ble.gatts_read(self.rx_handle)
#             print("Received from web:", incoming_data)
#             self.send(b"Echo: " + incoming_data)

#     def send(self, data: bytes) -> None:
#         for conn_handle in self.connections:
#             self.ble.gatts_notify(conn_handle, data)

#     def advertise(self) -> None: ...


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

    # uv_led: Pin = Pin(PIN_UV_LED, mode=Pin.OUT)
    # uv_led.off()

    ldr_1: ADC = ADC(Pin(PIN_LDR_1))
    ldr_1.atten(ADC.ATTN_11DB)
    # ldr_2: ADC = ADC(Pin(PIN_LDR_2))
    # pressure: ADC = ADC(Pin(PIN_PRESSURE))
    # for sensor in (ldr_1, ldr_2, pressure):
    #     sensor.atten(ADC.ATTN_11DB)

    try:
        while PROGRAM_RUNNING:
            print("\033[H", end="")
            print(
                f"""Distance: {
                    distance.read_range_single_millimeters()
                    if is_distance_working
                    else "N/A":<4} mm""",
                f"LDR 1: {ldr_1.read():<4} ohms",
                # f"LDR 2: {ldr_2.read():<4} ohms",
                # f"Pressure: {pressure.read():<4} ohms",
                # f"LED Indicator: {uv_led.value():<1}",
                sep="\n",
            )
            # toggle(uv_led)
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
