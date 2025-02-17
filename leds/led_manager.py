# Import dependencies
from gpiozero import LED, PWMLED
import threading
import time
import random

# Worker function handling LED patterns
def led_worker(gpio, pattern, stop_event):
    # Choose LED type: use PWMLED for breathing, standard LED otherwise
    if pattern == "breathing":
        led = PWMLED(gpio)
    else:
        led = LED(gpio)
    # Process LED behavior until stop event is set
    while not stop_event.is_set():
        if pattern == "flashing":
            # Flashing: LED on then off
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
        elif pattern == "erratic":
            # Erratic: LED on for random short time then off for random time
            led.on()
            time.sleep(random.uniform(0.01, 0.035))
            led.off()
            time.sleep(random.uniform(0.01, 0.35))
        elif pattern == "breathing":
            # Breathing: Increase brightness gradually
            for bri in [0.1 + (x / 100) * 0.9 for x in range(0, 101)]:
                led.value = bri
                time.sleep(0.002)
                if stop_event.is_set():
                    break
            # Breathing: Decrease brightness gradually
            for bri in [1.0 - (x / 100) * 0.9 for x in range(0, 101)]:
                led.value = bri
                time.sleep(0.015)
                if stop_event.is_set():
                    break
        elif pattern == "constant":
            # Constant: LED remains on
            led.on()
            time.sleep(0.1)
        else:
            # Default: pause execution briefly
            time.sleep(0.5)
    # Ensure LED is off after exiting the loop
    led.off()

# Start a thread to run the LED worker
def start_led(gpio, pattern):
    stop_event = threading.Event()
    t = threading.Thread(target=led_worker, args=(gpio, pattern, stop_event))
    t.daemon = True
    t.start()
    return (t, stop_event)

# Stop the LED thread gracefully
def stop_led(led_thread):
    t, stop_event = led_thread
    stop_event.set()
    t.join()
