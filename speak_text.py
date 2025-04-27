import subprocess
import re


def speak_text(text):
    # Remove encoded Unicode sequences like "\uXXXX"
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    # Remove unwanted characters: asterisks, double quotes, parentheses, braces, brackets, semicolons, pipes, ampersands, backticks, and double-escaped newlines (but keep dollar signs)
    safe_text = re.sub(r'[*"(){}\[\];|&`]', "", text)
    # replace `\n` with a space
    safe_text = re.sub(r'\\+n', ' ', safe_text)
    
    # Convert dollar amounts to spoken form (e.g., "$3" to "3 dollars", "$3.50" to "3 dollars 50 cents")
    safe_text = re.sub(r'\$(\d+)\.(\d+)', r'\1 dollars \2 cents', safe_text)
    safe_text = re.sub(r'\$(\d+)', r'\1 dollars', safe_text)

    print("Speaking:", safe_text)
    command = (
        f"echo {safe_text} | "
        "piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | "
        "sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | "
        "aplay -r 22050 -f S16_LE -t raw"
    )

    subprocess.run(command, shell=True)
    print("Finished speaking:", safe_text)
