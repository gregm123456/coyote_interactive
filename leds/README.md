# LED Manager

This module controls various LED patterns using GPIO on the robot.

## LED Patterns
- **flashing:** Blinks the LED on and off at a fixed interval (on for 0.5 seconds, off for 0.5 seconds).
- **erratic:** Blinks with random timing (on for a duration between 0.01 and 0.035 seconds, then off for a duration between 0.01 and 0.35 seconds).
- **breathing:** Smoothly increases brightness from 0.1 to 1.0 in 101 steps (0.002 sec each) and then decreases from 1.0 to 0.1 in 101 steps (0.015 sec each).
- **constant:** Keeps the LED steadily on with a 0.1-second loop delay.

## Usage

```python
from leds.led_manager import start_led, stop_led

# Start LED with a pattern, e.g. breathing
led_thread = start_led(gpio=17, pattern="breathing")

# Stop LED when needed
stop_led(led_thread)
```

## Dependencies
- gpiozero
- threading
- time
- random

## Note
Ensure that the appropriate GPIO pin is used for your specific hardware setup.
