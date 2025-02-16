# Audio to Text Transcription

This script continuously transcribes audio using the `whisper-stream` tool and logs the transcriptions to a specified file.

## Requirements

- Python 3.x
- `whisper-stream` tool
- WHISPER_MODEL environment variable set to the path of the Whisper model

## Installation

To install `whisper.cpp` and its dependencies on a Raspberry Pi system, run the following commands:

```bash
sudo apt update
sudo apt install -y cmake build-essential libsdl2-dev git wget
sudo git clone https://github.com/ggerganov/whisper.cpp /opt/whisper.cpp
cd /opt/whisper.cpp
sudo mkdir -p /usr/share/whisper/models
sudo sh ./models/download-ggml-model.sh tiny.en
sudo mv models/ggml-tiny.en.bin /usr/share/whisper/models/
sudo cmake -B build -DWHISPER_SDL2=ON
sudo cmake --build build --config Release
sudo cp build/bin/* /usr/local/bin/
sudo chmod +x /usr/local/bin/*
echo "WHISPER_MODEL=/usr/share/whisper/models/ggml-tiny.en.bin" | sudo tee -a /etc/environment
source /etc/environment
```

### Explanation of Commands

1. `sudo apt update`: Updates the package list to ensure you get the latest version and dependencies.
2. `sudo apt install -y cmake build-essential libsdl2-dev git wget`: Installs necessary packages for building and running `whisper.cpp`.
3. `sudo git clone https://github.com/ggerganov/whisper.cpp /opt/whisper.cpp`: Clones the `whisper.cpp` repository into `/opt/whisper.cpp`.
4. `cd /opt/whisper.cpp`: Changes the directory to the cloned repository.
5. `sudo mkdir -p /usr/share/whisper/models`: Creates the directory for storing Whisper models.
6. `sudo sh ./models/download-ggml-model.sh tiny.en`: Downloads the tiny English model.
7. `sudo mv models/ggml-tiny.en.bin /usr/share/whisper/models/`: Moves the downloaded model to the designated directory.
8. `sudo cmake -B build -DWHISPER_SDL2=ON`: Configures the build system.
9. `sudo cmake --build build --config Release`: Builds the project.
10. `sudo cp build/bin/* /usr/local/bin/`: Copies the built binaries to `/usr/local/bin/`.
11. `sudo chmod +x /usr/local/bin/*`: Makes the binaries executable.
12. `echo "WHISPER_MODEL=/usr/share/whisper/models/ggml-tiny.en.bin" | sudo tee -a /etc/environment`: Sets the `WHISPER_MODEL` environment variable.
13. `source /etc/environment`: Loads the new environment variable.

## Usage

To run the script, use the following command:

```bash
python transcribe_continuously.py [--log_file_path LOG_FILE_PATH]
```

### Arguments

- `--log_file_path`: Optional. Path to the log file where transcriptions will be saved. Defaults to `./transcription.txt`.

### Example

```bash
python transcribe_continuously.py --log_file_path ./heard/log.txt
```

This will start the transcription process and save the transcriptions to `./heard/log.txt`.

## Handling Interruptions

To stop the script gracefully, use `Ctrl+C`. The script will terminate the `whisper-stream` process and stop logging.

## Notes

- Ensure the `WHISPER_MODEL` environment variable is set to the correct path of the Whisper model before running the script.
- The script will create the log file and its parent directory if they do not exist.