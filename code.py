# Copyright 2026 Vision Ventures
"""Complete CircuitPython script for XIAO nRF52840 with Sensors and BLE."""

import time

import adafruit_ble
import adafruit_vl53l0x
import analogio
import board
import busio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# --- Pin & Hardware Definitions ---
PIN_LDR_1 = board.A0
PIN_SDA = board.D4
PIN_SCL = board.D5

# --- Initialize BLE Radio & UART Service ---
ble = adafruit_ble.BLERadio()
ble.name = "XIAO_BLE"
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)


def main() -> None:
    print("Initializing hardware...")

    # Initialize I2C and VL53L0X Distance Sensor
    distance_working = True
    try:
        i2c = busio.I2C(scl=PIN_SCL, sda=PIN_SDA)
        distance_sensor = adafruit_vl53l0x.VL53L0X(i2c)
    except Exception as e:
        print("Warning: Distance sensor not found or wired incorrectly:", e)
        distance_working = False

    # Initialize Analog LDR Sensor
    ldr_1 = analogio.AnalogIn(PIN_LDR_1)

    print("Starting BLE Advertising as 'XIAO_BLE'...")
    ble.start_advertising(advertisement)

    try:
        while True:
            # Handle BLE Connection & Web Communication
            if ble.connected:
                # Check for incoming data written by the web browser
                incoming_data = uart_service.read(32)
                if incoming_data:
                    print("Received from web:", incoming_data)
                    # Echo data back to the browser via UART notification
                    uart_service.write(b"Echo: " + incoming_data)
            elif not ble.advertising:
                # Restart advertising automatically if connection dropped
                ble.start_advertising(advertisement)
                print("Disconnected. Waiting for BLE connection...")

            # Read Sensors
            dist_val = distance_sensor.range if distance_working else "N/A"
            ldr_val = ldr_1.value  # Returns 16-bit value (0 - 65535)

            # Print Readings to Serial Monitor
            print(f"Distance: {dist_val:<4} mm | LDR 1: {ldr_val:<5} raw")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program stopped by user.")


if __name__ == "__main__":
    main()
