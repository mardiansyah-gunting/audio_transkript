# Audio Transkript

A Python-based toolkit to transcribe audio files (primarily Bahasa Indonesia) using the Google Web Speech API via the `SpeechRecognition` library. It supports long audio files by splitting them into smaller chunks and saving the results into a Word document (`.docx`).

---

## Overview
- `code/main.py`: The primary script that handles audio loading (using `pydub`), splitting audio into 45-second chunks, transcribing each chunk using Google Web Speech API, and saving the final concatenated text into a `.docx` file using `python-docx`.
- Supports various audio formats (e.g., `.m4a`, `.mp3`, `.wav`) through `pydub` and `ffmpeg`.

Typical use cases:
- Transcribing long recordings (e.g., interviews, meetings) in Bahasa Indonesia.
- Automatically generating Word documents from audio transcriptions.

---

## Stack
- Language: Python 3.9+
- Libraries:
  - `SpeechRecognition` (Google Web Speech API)
  - `pydub` (Audio processing and chunking)
  - `python-docx` (Word document generation)
- Package manager: `pip`

---

## Requirements
- Python 3.9+
- `ffmpeg` (Required by `pydub` for audio loading and conversion)
- Internet connection (Required for Google Web Speech API)
- Python packages:
  - `SpeechRecognition`
  - `pydub`
  - `python-docx`

### Install ffmpeg:
- **macOS (Homebrew):** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install -y ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

---

## Setup
1. Create and activate a virtual environment (recommended):
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     python -m pip install --upgrade pip
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     python -m pip install --upgrade pip
     ```
2. Install dependencies:
   ```bash
   pip install SpeechRecognition pydub python-docx
   ```
3. Ensure `ffmpeg` is installed and available in your system's PATH.

---

## How to Run
The script `code/main.py` is currently configured to process a specific file. To use it:

1. Open `code/main.py`.
2. Update the `nama_file` and `nama_file_word` variables with your input audio path and desired output Word document path:
   ```python
   nama_file = 'path/to/your/audio.m4a'
   nama_file_word = 'path/to/output/document.docx'
   ```
3. Run the script:
   ```bash
   python code/main.py
   ```

---

## Scripts and Entry Points
- `code/main.py`
  - `transkrip_audio_panjang(path_audio) -> str`: Splits audio into 45s chunks and transcribes them.
  - `simpan_ke_word(teks, path_simpan)`: Saves the transcription text to a `.docx` file.

---

## Environment Variables
- No environment variables are currently required.
- Google Web Speech API used by `SpeechRecognition` does not require an API key for default usage but does require internet access.

---

## Tests
- No automated tests are included yet.

TODO:
- Add unit tests for audio chunking and transcription functions.
- Add a sample audio file for integration testing.

---

## Project Structure
```
.
├── README.md
├── audio_input/         # Directory for input audio files (ignored by git)
│   ├── katamso/
│   └── tumbang-manyoi/
├── code/
│   └── main.py          # Main transcription script
└── docx/                # Directory for output Word documents (ignored by git)
    ├── katamso/
    └── tumbang-manyoi/
```

---

## Known Limitations & Notes
- Requires a stable internet connection for the Google Web Speech API.
- Large audio files are processed in 45-second chunks to avoid API limits.
- The script uses hardcoded paths; consider updating it to accept command-line arguments.

---

## License
No license file is present.

TODO:
- Choose and add a license (e.g., MIT, Apache-2.0) as `LICENSE` in the repository.

---

## Acknowledgements
- [SpeechRecognition Library](https://pypi.org/project/SpeechRecognition/)
- [Pydub](https://github.com/jiaaro/pydub)
- [python-docx](https://python-docx.readthedocs.io/)
