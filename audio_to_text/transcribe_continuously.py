import os
import subprocess
import argparse
try:
    from audio_to_text.audio_device import resolve_capture_device
except ModuleNotFoundError:
    from audio_device import resolve_capture_device

# Parse command line arguments
parser = argparse.ArgumentParser(description='Transcribe audio continuously.')
parser.add_argument('--log_file_path', type=str, default='./transcription.txt', help='Path to the log file')
parser.add_argument('--whisper_model', type=str, required=True, help='Path to the whisper model')
parser.add_argument('--threads', type=str, default="2", help='Number of threads for whisper-stream')
parser.add_argument('--mic', type=str, default="0", help='Capture device ID for whisper-stream')
parser.add_argument('--mic_name', type=str, default="", help='Optional mic name substring to match (preferred over --mic)')
parser.add_argument('--mic_match_index', type=int, default=0, help='When mic_name matches multiple devices, choose this zero-based match index')
args = parser.parse_args()

# Assign args to local variables
log_file_path = args.log_file_path
whisper_model = args.whisper_model
threads = args.threads
mic = args.mic
mic_name = args.mic_name
mic_match_index = args.mic_match_index
resolved_mic = resolve_capture_device(mic, mic_name, mic_match_index)
if mic_name:
    print(f"Using capture device {resolved_mic} for mic name match: '{mic_name}' at index {mic_match_index}.")
elif resolved_mic != str(mic):
    print(f"Requested mic {mic} not available; using capture device {resolved_mic} instead.")

# Ensure the heard directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Create the log file if it does not exist
if not os.path.exists(log_file_path):
    open(log_file_path, 'w').close()

# Define the stream command
command = [
    'whisper-stream',
    '-m', whisper_model,
    '--step', '4500',
    '--length', '5000',
    '-c', resolved_mic,
    '-t', threads,
    '-ac', '512',
    '--keep', '85'
]

# Start the stream process
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    # Continuously read the output
    while True:
        line = process.stdout.readline()
        if not line:
            break  # If no output, break the loop

        if "[2K" not in line and "[" not in line and "(" not in line:
            with open(log_file_path, 'a') as log_file:
                log_file.write(line)
                log_file.flush()  # Flush the file to ensure the content is written immediately
            #print(f' {line.strip()}')
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    print('Stopping...')
finally:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)

    # Check if the process exited with an error
    if process.returncode != 0:
        print(f'Error: whisper-stream exited with code {process.returncode}')
        # Optionally, read and print the stderr
        stderr_output = process.stderr.read()
        print(f'Error output: {stderr_output}')
