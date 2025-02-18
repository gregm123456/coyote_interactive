import subprocess
import time
import re

def speak_text(text):
    # Remove encoded Unicode sequences like "\uXXXX"
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    # Remove unwanted characters: asterisks, double quotes, parentheses, braces, brackets, semicolons, pipes, ampersands, and backticks (but keep dollar signs)
    safe_text = re.sub(r'[*"(){}\[\];|&`]', "", text)
    
    print("Speaking:", safe_text)
    command = (
        f"echo {safe_text} | "
        "piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | "
        "sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 | "
        "aplay -r 22050 -f S16_LE -t raw"
    )
    
    subprocess.run(command, shell=True)
    print("Finished speaking:", safe_text)