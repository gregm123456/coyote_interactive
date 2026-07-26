import os
from gpiozero import Button
from gpiozero.exc import BadPinFactory
from threading import Lock


def _patch_gpiozero_lgpio_backend():
    """Work around gpiozero lgpio backend missing the os import in some builds."""
    try:
        import gpiozero.pins.lgpio as lgpio_backend
    except Exception:
        return
    if not hasattr(lgpio_backend, "os"):
        lgpio_backend.os = os


class ButtonManager:
    def __init__(self, pin):
        _patch_gpiozero_lgpio_backend()
        self.button = None
        self.press_callbacks = []
        self.release_callbacks = []
        self.lock = Lock()

        try:
            self.button = Button(pin, pull_up=False, bounce_time=0.05)
            # Register the internal handlers for button press and release
            self.button.when_pressed = self._handle_button_press
            self.button.when_released = self._handle_button_release
        except (BadPinFactory, Exception) as exc:
            # Keep running without GPIO so audio/transcription paths still work.
            print(f"Warning: GPIO unavailable for pin {pin}: {exc}")

    def _handle_button_press(self):
        with self.lock:
            for callback in self.press_callbacks:
                callback()

    def _handle_button_release(self):
        with self.lock:
            for callback in self.release_callbacks:
                callback()

    def register_press_callback(self, callback):
        with self.lock:
            if callback not in self.press_callbacks:
                self.press_callbacks.append(callback)

    def unregister_press_callback(self, callback):
        with self.lock:
            if callback in self.press_callbacks:
                self.press_callbacks.remove(callback)

    def register_release_callback(self, callback):
        with self.lock:
            if callback not in self.release_callbacks:
                self.release_callbacks.append(callback)

    def unregister_release_callback(self, callback):
        with self.lock:
            if callback in self.release_callbacks:
                self.release_callbacks.remove(callback)

    def get_initial_state(self):
        if self.button is None:
            return False
        return self.button.is_pressed
