import os
import select
import sys
import termios
import tty

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def input_with_timeout(timeout):
    """Get input with a timeout."""
    if timeout <= 0:
        # If timeout is disabled, just use regular input
        return input()
    
    # Set stdin to non-blocking mode
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        # Check if input is available within timeout
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        else:
            return "_TIMEOUT_"
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)