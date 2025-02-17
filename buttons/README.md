# Button Manager

This module provides a class that manages a button using the gpiozero library and threading for event handling.

## Overview

The `ButtonManager` class:
- Initializes a button on a specified GPIO pin.
- Registers and handles callback functions for button press and release events.
- Ensures thread-safe operation with locks.
- Provides a method to check the initial button state.

## Usage

```python
from buttons.button_manager import ButtonManager

# Create a ButtonManager instance for a given GPIO pin
manager = ButtonManager(pin=17)

# Define callback functions
def on_press():
    print("Button pressed!")

def on_release():
    print("Button released!")

# Register callbacks
manager.register_press_callback(on_press)
manager.register_release_callback(on_release)

# Retrieve the initial state of the button
initial_state = manager.get_initial_state()
print("Initial button state:", initial_state)
```

## Dependencies
- gpiozero
- threading

Ensure that the correct GPIO pin is used for your hardware setup.
