import datetime
import os
import subprocess
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Transcribe audio continuously.')
parser.add_argument('--log_file_path', type=str, default='./transcription.txt', help='Path to the log file')
parser.add_argument('--whisper_model', type=str, required=True, help='Path to the whisper model')
args = parser.parse_args()

# Define the log file path
log_file_path = args.log_file_path

# Ensure the heard directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Create the log file if it does not exist
if not os.path.exists(log_file_path):
    open(log_file_path, 'w').close()

# Define the stream command
whisper_model = args.whisper_model  # using command-line parameter instead of environment variable
command = ['whisper-stream', '-m', whisper_model, '--step', '4500', '--length', '5000', '-c', '1', '-t', '2', '-ac', '512', '--keep', '85']

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
            print(f' {line.strip()}')
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully
    print('Stopping...')
finally:
    process.terminate()
