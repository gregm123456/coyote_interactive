![Coyote Image](coyote.png)

# Coyote Interactive

## Overview
A modular system for interactive coyote behaviors and communications.

## Features
- **LEDs**: Control of LED patterns.
- **Buttons**: Handling of button events.
- **Audio to Text**: Continuous transcription using whisper-stream.
- **Television Comments**: AI-powered commentary on television content.
- **Conversation Data**: Log storage for interactions.
  - **Conversation Archiving**: Automatic timestamped archiving of conversation history.
- **Talk with Person**: Captures intercom speech and manages the conversation flow with AI.
- **Wake/Sleep Modes**: System operates in different modes based on switch position.
  - **BOOM Feature**: Press both buttons simultaneously in sleep mode to archive the current conversation.

## Setup
- Install dependencies (Python, gpiozero, whisper-stream, etc.).
- Configure GPIO pins and other settings in config files.

## Usage
- `python coyote.py`

## Operation
- **Wake Mode**: System actively responds to button presses for TV or person interactions.
  - Conversation directory is checked/created before each interaction to ensure stability.
- **Sleep Mode**: System is idle but monitors for the special "BOOM" button combination.
  - Pressing both TV and person buttons archives the current conversation with a timestamp.
- **Conversation Management**: 
  - Conversations are stored in JSON format
  - Archives are automatically named with timestamps (e.g. `conversation_YYYYMMDD_HHMMSS.json`)

## Demonstration Video

[![Watch on YouTube](https://img.shields.io/badge/Watch%20on-YouTube-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=pncuq-U_tuU)  
[![Video Thumbnail](https://img.youtube.com/vi/pncuq-U_tuU/0.jpg)](https://www.youtube.com/watch?v=pncuq-U_tuU)

