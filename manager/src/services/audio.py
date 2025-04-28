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