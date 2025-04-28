#!/usr/bin/env python3
"""
Sound effects module for the coyote interactive project.
Provides functions to play various sound effects.
"""

import os
import subprocess
import time

def _get_sound_file_path(sound_file):
    """
    Get the absolute path to a sound file.
    
    Args:
        sound_file: The relative path to the sound file from the project root
                   or an absolute path
    
    Returns:
        str: The absolute path to the sound file
    """
    # If it's already an absolute path, return it
    if os.path.isabs(sound_file):
        return sound_file
    
    # If it's a relative path, make it relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, sound_file)

def play_sound_effect(sound_file, block=True):
    """
    Play a sound effect file.
    
    Args:
        sound_file: The path to the sound file to play
        block: Whether to block until the sound finishes playing
    
    Returns:
        bool: True if the sound was played successfully, False otherwise
    """
    sound_file_path = _get_sound_file_path(sound_file)
    
    if not os.path.exists(sound_file_path):
        print(f"Sound file not found: {sound_file_path}")
        return False
    
    print(f"Playing sound: {os.path.basename(sound_file_path)}")
    
    # Determine file extension
    _, ext = os.path.splitext(sound_file_path)
    ext = ext.lower()
    
    # Choose the appropriate player based on file extension
    if ext == '.mp3':
        player = "mpg123"
    elif ext in ['.wav', '.wave']:
        player = "aplay"
    else:
        # Default to mpg123 for other formats
        player = "mpg123"
    
    try:
        # Run the appropriate command with or without blocking
        if block:
            subprocess.run([player, sound_file_path], check=False, 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Start process without waiting for it to complete
            subprocess.Popen([player, sound_file_path], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Failed to play sound: {e}")
        return False

# For testing
if __name__ == "__main__":
    # Test the module by playing all sound files in the sound_effects directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(current_dir):
        if file.endswith(('.mp3', '.wav')):
            print(f"Testing sound: {file}")
            play_sound_effect(os.path.join('sound_effects', file))
            time.sleep(1)  # Wait a bit between sounds