from typing import List, Tuple, Dict, Any
import subprocess
import re

class AudioDevice:
    def __init__(self, name: str, index: int, volume: float):
        self.name = name
        self.index = index
        self.volume = volume

    def __repr__(self):
        return f"{self.name} (Index: {self.index}, Volume: {self.volume})"
    
    def to_dict(self):
        return {
            "name": self.name,
            "index": self.index,
            "volume": self.volume
        }

class AudioManager:
    @staticmethod
    def get_usb_microphones() -> List[Dict[str, Any]]:
        devices = []
        try:
            output = subprocess.check_output("pactl list sources", shell=True, text=True)
            current_index = None
            current_name = None
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Source #"):
                    try:
                        current_index = int(line.split('#')[1].strip())
                        current_name = None
                    except (ValueError, IndexError):
                        current_index = None
                        
                elif current_index is not None and line.startswith("Name:"):
                    current_name = line.split(':', 1)[1].strip()
                    
                    if "usb" in current_name.lower():
                        volume = AudioManager.get_volume(current_index, is_sink=False)
                        display_name = current_name.split('.')[-1] if '.' in current_name else current_name
                        devices.append({
                            "name": display_name,
                            "full_name": current_name,
                            "index": current_index,
                            "volume": volume
                        })
                        
                    current_index = None
                    current_name = None
                    
        except subprocess.CalledProcessError as e:
            print(f"Error getting microphones: {e}")
        except Exception as e:
            print(f"Unexpected error in get_usb_microphones: {e}")
            
        return devices

    @staticmethod
    def get_audio_output_devices() -> List[Dict[str, Any]]:
        devices = []
        try:
            output = subprocess.check_output("pactl list sinks", shell=True, text=True)
            current_index = None
            current_name = None
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Sink #"):
                    try:
                        current_index = int(line.split('#')[1].strip())
                        current_name = None
                    except (ValueError, IndexError):
                        current_index = None
                        
                elif current_index is not None and line.startswith("Name:"):
                    current_name = line.split(':', 1)[1].strip()
                    volume = AudioManager.get_volume(current_index, is_sink=True)
                    
                    display_name = current_name.split('.')[-1] if '.' in current_name else current_name
                    devices.append({
                        "name": display_name,
                        "full_name": current_name,
                        "index": current_index,
                        "volume": volume
                    })
                    
                    current_index = None
                    current_name = None
                    
        except subprocess.CalledProcessError as e:
            print(f"Error getting audio devices: {e}")
        except Exception as e:
            print(f"Unexpected error in get_audio_output_devices: {e}")
            
        return devices

    @staticmethod
    def get_volume(index: int, is_sink: bool = False) -> float:
        try:
            output = subprocess.check_output(f"pactl get-sink-volume {index}" if is_sink else f"pactl get-source-volume {index}", shell=True, text=True)
            volume = output.split()[4].replace('%', '')
            return float(volume)
        except subprocess.CalledProcessError:
            return 0.0

    @staticmethod
    def set_volume(index: int, volume: float, is_sink: bool = False) -> None:
        try:
            volume_str = f"{volume}%"
            subprocess.run(f"pactl set-sink-volume {index} {volume_str}" if is_sink else f"pactl set-source-volume {index} {volume_str}", shell=True)
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def mute_device(index: int, is_sink: bool = False) -> None:
        try:
            subprocess.run(f"pactl set-sink-mute {index} 1" if is_sink else f"pactl set-source-mute {index} 1", shell=True)
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def unmute_device(index: int, is_sink: bool = False) -> None:
        try:
            subprocess.run(f"pactl set-sink-mute {index} 0" if is_sink else f"pactl set-source-mute {index} 0", shell=True)
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def play_feedback_tone():
        """Play a short beep to confirm volume change."""
        try:
            # Using 'play' command from sox package for a quick beep
            subprocess.run("play -n synth 0.1 sine 1000", shell=True, 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except Exception:
            # Fallback method if play command fails
            try:
                subprocess.run("speaker-test -t sine -f 1000 -l 1 -p 5000", 
                              shell=True, stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Failed to play feedback tone: {e}")

    @staticmethod
    def set_volume_step(index: int, step: int, is_sink: bool = False) -> float:
        """
        Set volume to a specific step (0-10) representing 0% to 100%
        
        Args:
            index: The device index
            step: Integer from 0-10 (0=0%, 1=10%, 5=50%, 10=100%)
            is_sink: True for output devices, False for input devices
            
        Returns:
            float: The new volume percentage
        """
        # Ensure step is between 0-10
        step = max(0, min(10, step))
        
        # Convert to percentage (0-100)
        volume_percent = step * 10.0
        
        # Set the volume using existing method
        AudioManager.set_volume(index, volume_percent, is_sink=is_sink)
        
        # Play feedback tone if this is an output device and volume > 0
        if is_sink and volume_percent > 0:
            AudioManager.play_feedback_tone()
        
        return volume_percent

    @staticmethod
    def increment_volume(index: int, is_sink: bool = False) -> float:
        """
        Increase volume by 10% (one step)
        
        Returns: New volume level
        """
        current_volume = AudioManager.get_volume(index, is_sink)
        current_step = round(current_volume / 10)
        new_step = min(10, current_step + 1)  # Ensure we don't go above 10 (100%)
        return AudioManager.set_volume_step(index, new_step, is_sink)

    @staticmethod
    def decrement_volume(index: int, is_sink: bool = False) -> float:
        """
        Decrease volume by 10% (one step)
        
        Returns: New volume level
        """
        current_volume = AudioManager.get_volume(index, is_sink)
        current_step = round(current_volume / 10)
        new_step = max(0, current_step - 1)  # Ensure we don't go below 0 (0%)
        return AudioManager.set_volume_step(index, new_step, is_sink)

    @staticmethod
    def get_volume_step(index: int, is_sink: bool = False) -> int:
        """
        Get the current volume step (0-10)
        
        Returns: Integer representing volume step (0=0%, 10=100%)
        """
        current_volume = AudioManager.get_volume(index, is_sink)
        return round(current_volume / 10)