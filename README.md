# audio_transkript

A small, script-based toolkit to transcribe audio (primarily Bahasa Indonesia) using either:
- OpenAI Whisper (runs locally), or
- Google Web Speech API via the `SpeechRecognition` Python library.

This repository contains two simple Python scripts demonstrating both approaches. It is not yet a packaged application or CLI; you run or import the scripts directly.

---

## Overview
- `code/whisper.py` uses the Whisper model locally to transcribe many audio formats (mp3, wav, m4a, etc.). It sets `language="id"` and `fp16=False` by default for CPU compatibility.
- `code/gsr.py` uses the Google Web Speech API through `SpeechRecognition`. It requires WAV (PCM) input and an active internet connection.

Typical use cases:
- Fast local transcription with Whisper (works offline after the first model download; higher accuracy and flexibility; supports many formats).
- Quick online transcription with Google Web Speech for simple WAV inputs.

---

## Stack
- Language: Python
- Libraries:
  - `openai-whisper` (Whisper)
  - `SpeechRecognition` (Google Web Speech API)
- Package manager: `pip`

---

## Requirements
- Python 3.9+ (earlier/newer versions may work but are untested here)
- ffmpeg (required by Whisper for audio I/O)
- Internet connection (only for the Google Web Speech path in `gsr.py`)
- Python packages:
  - `openai-whisper`
  - `SpeechRecognition`

Optional/implicit:
- `torch` is pulled in by Whisper as a dependency.
- On some systems, additional audio libs/codecs may be needed.

Install ffmpeg (examples):
- macOS (Homebrew): `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
- Windows (Chocolatey): `choco install ffmpeg`

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
   pip install openai-whisper SpeechRecognition
   ```
3. Ensure `ffmpeg` is installed and on your PATH (see Requirements above).

---

## How to Run
You can run the example scripts directly or import their functions in your own code.

### 1) Whisper (local)
- Edit `nama_file` in `code/whisper.py` to point to your audio file (e.g., a file under `audio_input/`). Whisper supports formats like `.mp3`, `.wav`, `.m4a`, etc.
- Run:
  ```bash
  python code/whisper.py
  ```
- First run may take time while the model downloads. The script prints the transcription to stdout.

Importing the function instead:
```python
from code.whisper import transkrip_audio_whisper
print(transkrip_audio_whisper("audio_input/Tumbang Manyoi.m4a"))
```

### 2) Google Web Speech via SpeechRecognition (online)
- `code/gsr.py` expects a WAV (PCM) file and uses `language='id-ID'`.
- If your audio is not WAV, convert it (example with ffmpeg):
  ```bash
  ffmpeg -i "audio_input/Tumbang Manyoi.m4a" -ac 1 -ar 16000 rekaman_saya.wav
  ```
- Edit `nama_file` in `code/gsr.py` to your WAV file name, then run:
  ```bash
  python code/gsr.py
  ```

Importing the function instead:
```python
from code.gsr import transkrip_audio_google
print(transkrip_audio_google("rekaman_saya.wav"))
```

---

## Scripts and Entry Points
- `code/whisper.py`
  - Function: `transkrip_audio_whisper(path_audio) -> str`
  - Default model: `base` (balance of speed and accuracy)
  - Sets `language="id"`, `fp16=False` for CPU compatibility
  - Can be run directly with `python code/whisper.py`

- `code/gsr.py`
  - Function: `transkrip_audio_google(path_audio) -> str`
  - Uses Google Web Speech via `SpeechRecognition`
  - Expects WAV input and an internet connection
  - Can be run directly with `python code/gsr.py`

There is no packaged CLI or module entry point yet (e.g., no `__main__` or `setup.py/pyproject.toml`).

---

## Environment Variables
- None required at the moment for the included examples.
- Whisper runs locally (no API key needed).
- `SpeechRecognition`'s Google Web Speech backend used here does not require credentials but does require an internet connection.

TODO:
- If you later add cloud services (e.g., OpenAI API, Google Cloud Speech-to-Text), document the required environment variables here.

---

## Tests
- Currently, no automated tests are included.

TODO:
- Add small sample audios and unit tests to validate both transcription paths.
- Provide a lightweight smoke test script to verify environment and model download.

---

## Project Structure
```
.
├── README.md
├── audio_input/
│   ├── Tumbang Manyoi 2.m4a
│   └── Tumbang Manyoi.m4a
├── code/
│   ├── gsr.py
│   └── whisper.py
└── docx/
    ├── Tumbang Manyoi 2.docx
    └── Tumbang Manyoi.docx
```

---

## Known Limitations & Notes
- `code/gsr.py` prints Indonesian messages and returns Indonesian errors; ensure your console encoding supports UTF-8.
- For `code/gsr.py`, use WAV (PCM). Other formats need conversion first.
- Whisper's first run downloads the selected model and may take time.
- By default, Whisper here runs on CPU (`fp16=False`). If you have a supported GPU and PyTorch CUDA installed, you can enable faster inference by omitting `fp16=False` and using a GPU-enabled environment.
- The scripts have hardcoded filenames for simplicity; you may adapt them into a CLI.

---

## License
No license file is present.

TODO:
- Choose and add a license (e.g., MIT, Apache-2.0) as `LICENSE` in the repository, and update this section accordingly.

---

## Acknowledgements
- OpenAI Whisper: https://github.com/openai/whisper
- SpeechRecognition library: https://pypi.org/project/SpeechRecognition/
