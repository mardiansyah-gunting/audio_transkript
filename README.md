# Audio Transcript

A small Python utility that transcribes audio files using the `SpeechRecognition` library and its default cloud speech backend. Long recordings are split into 45-second segments, then the combined text is written to a Word document (`.docx`).

## Features

- Chunked processing for long files
- Multiple formats supported via **pydub** (requires **ffmpeg** on your system)
- Output as `.docx` via **python-docx**
- Default recognition language: Indonesian (`id-ID`); override with `--language`

## Requirements

- Python 3.9+
- **ffmpeg** installed and on your `PATH` (required by pydub for many formats)
- Network access while transcribing (the default recognizer uses an online service)

### System: ffmpeg

- **macOS (Homebrew):** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install -y ffmpeg`
- **Windows:** Install ffmpeg from the official distribution and add its `bin` folder to your `PATH`

## Setup

1. Create and activate a virtual environment (recommended):

   **macOS / Linux**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   ```

   **Windows (PowerShell)**

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Confirm `ffmpeg` is available:

   ```bash
   ffmpeg -version
   ```

## Usage

```bash
python code/main.py path/to/audio.m4a path/to/output.docx
```

Optional language (BCP-47 tag), for example US English:

```bash
python code/main.py interview.wav transcript.docx --language en-US
```

Create output directories yourself, or the script will create the parent folder of the output path if needed.

## Project layout

```
.
├── README.md
├── requirements.txt
├── TODO.md
├── code/
│   └── main.py
├── audio_input/    # optional local folder for inputs (gitignored)
└── docx/           # optional local folder for outputs (gitignored)
```

## Limitations

- Needs a stable network connection for the default cloud-based recognition.
- Very large files are processed in fixed 45-second chunks; quality depends on audio clarity and the recognition service.

## License

No license file is included yet. Add one (for example MIT) when you are ready.

## Maintenance

See `TODO.md` for a checklist of repository updates and optional next steps.
