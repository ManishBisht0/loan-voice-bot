# Loan Voice Bot

A voice-based loan application assistant built using:

* FastAPI
* OpenAI Whisper (Speech-to-Text)
* Edge-TTS (Text-to-Speech)
* HTML + JavaScript Frontend
* Session-based Question Flow

The application asks loan-related questions, records user responses through the microphone, converts speech to text using Whisper, processes the conversation flow, and generates spoken responses using Edge-TTS.

---

# Features

* Voice-based conversation
* Speech-to-Text using Whisper
* Text-to-Speech using Edge-TTS
* Dynamic loan questionnaire
* Session management
* GPU support for Whisper (CUDA)
* REST API backend using FastAPI

---

# Project Structure

```text
loan_voice_bot/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── script.js
│
├── services/
│   ├── whisper_service.py
│   ├── tts_service.py
│   └── question_service.py
│
├── uploads/
│
└── generated_audio/
```

---

# Installation

## 1. Clone Project

```bash
git clone <repo-url>
cd loan_voice_bot
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv my_env
my_env\Scripts\activate
```

Linux

```bash
python3 -m venv my_env
source my_env/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Install FFmpeg

Whisper requires FFmpeg.

## Windows

Install using Winget:

```bash
winget install Gyan.FFmpeg
```

Verify installation:

```bash
ffmpeg -version
```

---

## Manual Installation

1. Download FFmpeg.
2. Extract ZIP.
3. Add:

```text
ffmpeg/bin
```

to Windows PATH.

Verify:

```bash
ffmpeg -version
```

---

# CUDA Setup (Optional)

For GPU acceleration install PyTorch with CUDA support.

Check NVIDIA GPU:

```bash
nvidia-smi
```

Install CUDA-enabled PyTorch:

```bash
pip uninstall torch torchvision torchaudio -y
```

CUDA 12.1 Example:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Verify:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

Expected:

```text
True
```

---

# Whisper GPU Configuration

File:

```python
services/whisper_service.py
```

```python
import torch
import whisper

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("base").to(DEVICE)

def transcribe_audio(path):
    result = model.transcribe(path)
    return result["text"]
```

Check device:

```python
print("Using device:", DEVICE)
```

---

# Run Application

Start FastAPI:

```bash
uvicorn app:app --reload
```

Open browser:

```text
http://127.0.0.1:8000
```

---

# API Flow

## Start Interview

```http
POST /start
```

Response:

```json
{
  "question": "What is your full name?"
}
```

---

## Submit Audio

```http
POST /answer
```

Request:

```text
multipart/form-data
audio=<recording.wav>
```

Process:

1. Receive audio
2. Save recording
3. Whisper transcribes speech
4. Store answer
5. Fetch next question
6. Generate audio using Edge-TTS
7. Return next question

Response:

```json

```

---

# Edge-TTS

Generate audio response:


---

# Troubleshooting

## FFmpeg Not Found

Check:

```bash
python -c "import shutil; print(shutil.which('ffmpeg'))"
```

Expected:

```text
C:\...\ffmpeg.exe
```

---

## CUDA Not Detected

Check:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False:

* Install NVIDIA drivers
* Install CUDA toolkit
* Reinstall CUDA-enabled PyTorch

---

## Whisper Slow

Use GPU:

```python
DEVICE = "cuda"
```

instead of:

```python
DEVICE = "cpu"
```

---

## Microphone Not Recording

Verify browser permissions:

* Allow microphone access
* Use HTTPS in production
* Check browser console logs

---

# Production Deployment

Install Gunicorn/Uvicorn:

```bash
pip install gunicorn uvicorn
```

Run:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```


# Requirements

```text
fastapi
uvicorn
python-multipart
jinja2
openai-whisper
torch
edge-tts
aiofiles
```

Install:

```bash
pip install -r requirements.txt
```

---

# Workflow Summary

```text
User Speaks
      │
      ▼
Browser Records Audio
      │
      ▼
FastAPI Receives Audio
      │
      ▼
Whisper Converts Speech → Text
      │
      ▼
Question Flow Engine
      │
      ▼
Generate Next Question
      │
      ▼
Edge-TTS Converts Text → Speech
      │
      ▼
Browser Plays Audio
```

---

# Author

Manish Bisht

Data Scientist


pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128