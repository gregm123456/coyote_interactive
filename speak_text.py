import subprocess
import re
import tempfile
import os
import json
import shlex
from config import SPEAKER_DEVICE


def _resolve_piper_model_path():
    """Pick a usable Piper model path from env vars or common defaults."""
    candidates = [
        os.environ.get("PIPER_MODEL_COYOTE", "").strip(),
        os.environ.get("PIPER_MODEL", "").strip(),
        "/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx",
        "/usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return ""


def speak_text(text):
    # First, decode the JSON string if it's enclosed in quotes and has escaped characters
    if text.startswith('"') and text.endswith('"'):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            # If it's not valid JSON, continue with the original text
            pass
    
    # Replace Unicode apostrophes with ASCII apostrophes instead of removing them
    text = re.sub(r'\\u2019', "'", text)  # Unicode RIGHT SINGLE QUOTATION MARK
    text = re.sub(r'\\u2018', "'", text)  # Unicode LEFT SINGLE QUOTATION MARK
    
    # Remove other encoded Unicode sequences
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    
    # Fix common Unicode encoding issues with apostrophes
    text = text.replace('â€™', "'")
    
    # Fix contractions with spaces around apostrophes (e.g., "haven' t" -> "haven't")
    text = re.sub(r"(\w+)'\s+(\w+)", r"\1'\2", text)
    text = re.sub(r"(\w+)\s+'(\w+)", r"\1'\2", text)
    
    # Remove unwanted characters but NOT apostrophes/single quotes
    safe_text = re.sub(r'[*"(){}\[\];|&`]', "", text)
    # replace `\n` with a space
    safe_text = re.sub(r'\\+n', ' ', safe_text)
    
    # Convert dollar amounts to spoken form (e.g., "$3" to "3 dollars", "$3.50" to "3 dollars 50 cents")
    safe_text = re.sub(r'\$(\d+)\.(\d+)', r'\1 dollars \2 cents', safe_text)
    safe_text = re.sub(r'\$(\d+)', r'\1 dollars', safe_text)

    print("Speaking:", safe_text)
    if not safe_text.strip():
        print("Finished speaking:", safe_text)
        return
    
    # Use a temporary file to avoid shell escaping issues with apostrophes
    # Add encoding='utf-8' to handle Unicode characters correctly
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp:
        tmp.write(safe_text)
        tmp_path = tmp.name
    
    try:
        model_path = _resolve_piper_model_path()
        if not model_path:
            print("Piper model not found. Set PIPER_MODEL_COYOTE or install voice models in /usr/share/piper/voices/en_GB/.")
            return

        base_pipeline = (
            f"cat {shlex.quote(tmp_path)} | "
            f"piper --model {shlex.quote(model_path)} -s 71 --length_scale 1.75 --output-raw | "
            "sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98"
        )

        if SPEAKER_DEVICE and SPEAKER_DEVICE.strip():
            command = (
                base_pipeline +
                f" | aplay -D {shlex.quote(SPEAKER_DEVICE)} -r 22050 -f S16_LE -t raw"
            )
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Configured speaker device '{SPEAKER_DEVICE}' failed; retrying default output.")
                fallback_command = base_pipeline + " | aplay -r 22050 -f S16_LE -t raw"
                subprocess.run(fallback_command, shell=True, check=False)
        else:
            command = base_pipeline + " | aplay -r 22050 -f S16_LE -t raw"
            subprocess.run(command, shell=True, check=False)

        print("Finished speaking:", safe_text)
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
