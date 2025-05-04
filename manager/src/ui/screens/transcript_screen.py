import os
import select
import sys
from ...utils.terminal import clear_screen

def show_television_transcript():
    """Display television transcript with auto-refresh functionality."""
    transcript_path = "/home/robot/coyote_interactive/audio_to_text/transcription.txt"
    last_lines = []
    lines_to_show = 3
    refresh_rate = 1
    
    while True:
        clear_screen()
        print("=" * 13 + " Television Transcript " + "=" * 13)
        print("=" * 49)
        
        try:
            # Check if file exists
            if not os.path.exists(transcript_path):
                print("Transcript file not found!")
                print(f"Expected at: {transcript_path}")
                print("\nOptions:")
                print("r: Refresh")
                print("b: Back to Main Menu")
                
                choice = input("\nEnter your choice: ")
                if choice.lower() == 'b':
                    return
                continue
            
            # Read the latest content from the file
            with open(transcript_path, "r") as file:
                all_lines = file.readlines()
                if not all_lines:
                    print("Transcript file is empty.")
                else:
                    last_lines = all_lines[-lines_to_show:]
                    # Add simple ASCII character at the start of each line
                    for line in last_lines:
                        print(f"* {line.strip()}")
            
            # Show current status and options
            print("_" * 49)
            print(f"Showing last {len(last_lines)} of {len(all_lines)} lines")
            print("m: More lines (+3) / f: Fewer lines (-3)")
            print("a: Auto-refresh on/off")
            print("b: Back to Main Menu")
            
            # Wait for a keystroke with a timeout
            print(f"Enter a choice (auto-refresh in {refresh_rate}s)...")
            
            # Use standard input instead of input_with_timeout to show typed characters
            if refresh_rate <= 0:
                # If timeout is disabled, just use regular input
                choice = input("Enter your choice: ")
            else:
                # Set up a timeout for input
                ready, _, _ = select.select([sys.stdin], [], [], refresh_rate)
                if ready:
                    # Input is available, read it
                    choice = input("Enter your choice: ")
                else:
                    # Timeout occurred, refresh automatically
                    choice = "_TIMEOUT_"
            
            if choice == '_TIMEOUT_':
                # Timeout occurred, refresh automatically
                continue
            elif choice.lower() == 'r':
                # Manual refresh requested
                continue
            elif choice.lower() == 'm':
                # Show more lines (+3)
                lines_to_show = min(lines_to_show + 3, 50)
                continue
            elif choice.lower() == 'f':
                # Show fewer lines (-3)
                lines_to_show = max(lines_to_show - 3, 3)
                continue
            elif choice.lower() == 'a':
                # Toggle auto-refresh
                if refresh_rate > 0:
                    refresh_rate = 0
                    print("Auto-refresh disabled.")
                else:
                    refresh_rate = 1  # Changed from 3 to 1
                    print("Auto-refresh enabled (1s).")
                input("Press Enter to continue...")
                continue
            elif choice.lower() == 'b':
                # Return to main menu
                return
        
        except Exception as e:
            print(f"Error reading transcript: {e}")
            input("Press Enter to continue...")