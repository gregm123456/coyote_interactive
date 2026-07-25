#!/usr/bin/env python3
"""Simple hardware test: flash GPIO_LED_DYNAMITE repeatedly."""

import argparse
import time

from gpiozero import LED

import config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Flash the LED on config.GPIO_LED_DYNAMITE for wiring/debug checks."
    )
    parser.add_argument(
        "--on-time",
        type=float,
        default=0.2,
        help="Seconds LED stays on each cycle (default: 0.2)",
    )
    parser.add_argument(
        "--off-time",
        type=float,
        default=0.2,
        help="Seconds LED stays off each cycle (default: 0.2)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of flashes; 0 means run forever (default: 0)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    pin = config.GPIO_LED_DYNAMITE
    led = LED(pin)

    print(f"Flashing GPIO_LED_DYNAMITE on BCM pin {pin}")
    print(
        f"on-time={args.on_time:.3f}s off-time={args.off_time:.3f}s count={args.count or 'infinite'}"
    )
    print("Press Ctrl+C to stop.")

    flashes_done = 0
    try:
        while args.count == 0 or flashes_done < args.count:
            led.on()
            time.sleep(args.on_time)
            led.off()
            time.sleep(args.off_time)
            flashes_done += 1
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        led.off()


if __name__ == "__main__":
    main()
