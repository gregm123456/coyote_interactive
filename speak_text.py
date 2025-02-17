import subprocess
import time

def speak_text(text):
    # Implement speech synthesis using piper, sox, and aplay
    command = f"echo '{text}' | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 | aplay -r 22050 -f S16_LE -t raw"
    subprocess.run(command, shell=True)
    
    print("Speaking:", text)
