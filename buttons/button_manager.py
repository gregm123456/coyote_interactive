from gpiozero import Button
from threading import Lock


class ButtonManager:
    def __init__(self, pin):
        self.button = Button(pin, pull_up=False, bounce_time=0.05)
        self.press_callbacks = []
        self.release_callbacks = []
        self.lock = Lock()

        # Register the internal handlers for button press and release
        self.button.when_pressed = self._handle_button_press
        self.button.when_released = self._handle_button_release

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
        return self.button.is_pressed
