import os
import torch
import whisper

ffmpeg_bin = r"C:\Users\Manis\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"

os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Device:", DEVICE)

if DEVICE == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))

model = whisper.load_model("medium.en", device=DEVICE)

def transcribe_audio(path: str):
    print("File:", path)
    print("Exists:", os.path.exists(path))
    print("Size:", os.path.getsize(path))

    result = model.transcribe(
        path,
        fp16=False
    )

    print("Transcription:", result["text"])
    return result["text"].strip()