from gpiozero import LED, PWMLED
import threading
import time
import random

def led_worker(gpio, pattern, stop_event):
    # Create LED instance; use PWMLED for breathing pattern.
    if pattern == "breathing":
        led = PWMLED(gpio)
    else:
        led = LED(gpio)
    while not stop_event.is_set():
        if pattern == "flashing":
            led.on()                  # LED ON
            time.sleep(0.5)
            led.off()                 # LED OFF
            time.sleep(0.5)
        elif pattern == "erratic":
            led.on()
            time.sleep(random.uniform(0.1, 0.7))
            led.off()
            time.sleep(random.uniform(0.1, 0.7))
        elif pattern == "breathing":
            # Increase brightness
            for bri in [x/20.0 for x in range(0, 21)]:
                led.value = bri
                time.sleep(0.05)
                if stop_event.is_set():
                    break
            # Decrease brightness
            for bri in [x/20.0 for x in range(20, -1, -1)]:
                led.value = bri
                time.sleep(0.05)
                if stop_event.is_set():
                    break
        else:
            time.sleep(0.5)
    # Ensure LED is turned off when stopping.
    led.off()

def start_led(gpio, pattern):
    stop_event = threading.Event()
    t = threading.Thread(target=led_worker, args=(gpio, pattern, stop_event))
    t.daemon = True
    t.start()
    return (t, stop_event)

def stop_led(led_thread):
    t, stop_event = led_thread
    stop_event.set()
    t.join()
