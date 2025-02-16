from button_manager import ButtonManager

button_manager_17 = ButtonManager(pin=17)

def script1_button_press():
    print("Script 1: Button 17 was pressed!")

def script1_button_release():
    print("Script 1: Button 17 was released!")

button_manager_17.register_press_callback(script1_button_press)
button_manager_17.register_release_callback(script1_button_release)

# Check the initial state of the button
initial_state = button_manager_17.get_initial_state()
if initial_state:
    print("Script 1: Button 17 is initially pressed.")
else:
    print("Script 1: Button 17 is initially released.")

try:
    print("Script 1: Listening for button 17 events. Press Ctrl+C to exit.")
    while True:
        pass
except KeyboardInterrupt:
    print("Script 1: Exiting...")
    button_manager_17.unregister_press_callback(script1_button_press)
    button_manager_17.unregister_release_callback(script1_button_release)