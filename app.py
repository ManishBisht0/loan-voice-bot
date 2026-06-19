from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil, uuid, os, asyncio

from questions import QUESTIONS, SUCCESS_MESSAGE, REJECTION_MESSAGE
from services.whisper_service import transcribe_audio
from services.eligibility import classify_answer
from services.tts_service import generate_audio

import os

os.makedirs("uploads", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


sessions = {}

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@app.get("/screening")
async def screening(request: Request):
    return templates.TemplateResponse("screening.html", {"request": request})

@app.get("/question")
async def question(session_id:str):
    idx = sessions.setdefault(session_id, 0)
    q = QUESTIONS[idx]
    audio = await generate_audio(q)
    return {"question": q, "audio": "/" + audio.replace("\\","/")}


@app.post("/answer")
async def answer(session_id:str, audio: UploadFile = File(...)):
    path = f"uploads/{uuid.uuid4()}.webm"

    with open(path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    text = transcribe_audio(path)
    result = classify_answer(text)

    # Rejected
    if result == "no":
        audio_file = await generate_audio(REJECTION_MESSAGE)

        return {
            "status": "reject",
            "message": REJECTION_MESSAGE,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    # Invalid Answer
    if result != "yes":
        retry_msg = "Please answer yes or no"
        audio_file = await generate_audio(retry_msg)

        return {
            "status": "retry",
            "message": retry_msg,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    sessions[session_id] = sessions.get(session_id, 0) + 1

    # Screening Completed Successfully
    if sessions[session_id] >= len(QUESTIONS):
        audio_file = await generate_audio(SUCCESS_MESSAGE)

        return {
            "status": "success",
            "message": SUCCESS_MESSAGE,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    return {"status": "next"}
