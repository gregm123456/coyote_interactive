import os
import select
import sys
from ...utils.terminal import clear_screen

def show_dialogue():
    """Display conversation dialogue with auto-refresh functionality."""
    # Paths to all four possible dialogue files
    speech_path = "/home/robot/coyote_interactive/conversation_data/last_captured_speech.txt"
    commentary_path = "/home/robot/coyote_interactive/conversation_data/last_coyote_commentary.txt"
    reply_path = "/home/robot/coyote_interactive/conversation_data/last_coyote_reply.txt"
    television_path = "/home/robot/coyote_interactive/conversation_data/last_heard_television.txt"
    refresh_rate = 1
    
    while True:
        clear_screen()
        print("=" * 19 + " Dialogue " + "=" * 20)
        
        try:
            # Check which files exist and get their modification times
            files_info = []
            
            if os.path.exists(speech_path):
                files_info.append({
                    'path': speech_path,
                    'title': "Person's Speech",
                    'time': os.path.getmtime(speech_path),
                    'type': 'speech'
                })
                
            if os.path.exists(commentary_path):
                files_info.append({
                    'path': commentary_path,
                    'title': "Coyote's TV Commentary",
                    'time': os.path.getmtime(commentary_path),
                    'type': 'commentary'
                })
                
            if os.path.exists(reply_path):
                files_info.append({
                    'path': reply_path,
                    'title': "Coyote's Reply",
                    'time': os.path.getmtime(reply_path),
                    'type': 'reply'
                })
            
            if os.path.exists(television_path):
                files_info.append({
                    'path': television_path,
                    'title': "Heard on Television",
                    'time': os.path.getmtime(television_path),
                    'type': 'television'
                })
            
            if not files_info:
                print("No dialogue files found!")
                print("\nOptions:")
                print("r: Refresh")
                print("b: Back to Main Menu")
                
                choice = input("\nEnter your choice: ")
                if choice.lower() == 'b':
                    return
                continue
            
            # Sort files by modification time (newest last)
            files_info.sort(key=lambda x: x['time'])
            
            # Get the two most recent files (or all if fewer than 2)
            if len(files_info) > 2:
                files_to_show = files_info[-2:]
            else:
                files_to_show = files_info
                
            # Display files in chronological order (oldest first)
            for file_info in files_to_show:
                print(f"\n--- {file_info['title']} " + "-" * (28 - len(file_info['title'])))
                with open(file_info['path'], "r") as file:
                    content = file.read().strip()
                    print(content)
            
            # Show minimal options at the bottom
            print("\n" + "_" * 49)
            print("a: Auto-refresh on/off | r: Refresh | b: Back")
            
            # Wait for a keystroke with a timeout
            print(f"Enter choice (auto-refresh in {refresh_rate}s)...")
            
            # Use standard input with timeout for auto-refresh
            if refresh_rate <= 0:
                # If timeout is disabled, just use regular input
                choice = input("> ")
            else:
                # Set up a timeout for input
                ready, _, _ = select.select([sys.stdin], [], [], refresh_rate)
                if ready:
                    # Input is available, read it
                    choice = input("> ")
                else:
                    # Timeout occurred, refresh automatically
                    choice = "_TIMEOUT_"
            
            if choice == '_TIMEOUT_':
                # Timeout occurred, refresh automatically
                continue
            elif choice.lower() == 'r':
                # Manual refresh requested
                continue
            elif choice.lower() == 'a':
                # Toggle auto-refresh
                if refresh_rate > 0:
                    refresh_rate = 0
                    print("Auto-refresh disabled.")
                else:
                    refresh_rate = 1
                    print("Auto-refresh enabled (1s).")
                input("Press Enter to continue...")
                continue
            elif choice.lower() == 'b':
                # Return to main menu
                return
        
        except Exception as e:
            print(f"Error reading dialogue files: {e}")
            input("Press Enter to continue...")