from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import shutil
import uuid
import os

from time import perf_counter

from questions import QUESTIONS, SUCCESS_MESSAGE, REJECTION_MESSAGE
from services.whisper_service import transcribe_audio
from services.eligibility import classify_answer
from services.tts_service import generate_audio


os.makedirs("uploads", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Session Structure
# {
#     session_id: {
#         "question_idx": 0,
#         "start_time": xxx
#     }
# }
sessions = {}


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {"request": request}
    )


@app.get("/screening")
async def screening(request: Request):
    return templates.TemplateResponse(
        "screening.html",
        {"request": request}
    )


@app.get("/question")
async def question(session_id: str):

    if session_id not in sessions:
        sessions[session_id] = {
            "question_idx": 0,
            "start_time": perf_counter()
        }

    idx = sessions[session_id]["question_idx"]

    question_text = QUESTIONS[idx]

    tts_start = perf_counter()
    audio_file = await generate_audio(question_text)
    tts_time = perf_counter() - tts_start

    print("\n========================================")
    print(f"QUESTION #{idx + 1}")
    print(f"Question: {question_text}")
    print(f"Question TTS Time: {tts_time:.2f} sec")
    print("========================================\n")

    return {
        "question": question_text,
        "audio": "/" + audio_file.replace("\\", "/")
    }


@app.post("/answer")
async def answer(
    session_id: str,
    audio: UploadFile = File(...)
):

    request_start = perf_counter()

    file_path = f"uploads/{uuid.uuid4()}.webm"

    # -------------------------
    # Save Audio
    # -------------------------
    save_start = perf_counter()

    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    save_time = perf_counter() - save_start

    # -------------------------
    # Whisper
    # -------------------------
    whisper_start = perf_counter()

    transcription = transcribe_audio(file_path)

    whisper_time = perf_counter() - whisper_start

    # -------------------------
    # Classification
    # -------------------------
    classify_start = perf_counter()

    result = classify_answer(transcription)

    classify_time = perf_counter() - classify_start

    current_question = sessions[session_id]["question_idx"] + 1

    print("\n========================================")
    print(f"QUESTION #{current_question}")
    print(f"User Answer      : {transcription}")
    print(f"Save Time        : {save_time:.2f} sec")
    print(f"Whisper Time     : {whisper_time:.2f} sec")
    print(f"Classification   : {classify_time:.4f} sec")

    # ---------------------------------------------------
    # REJECTED
    # ---------------------------------------------------
    if result == "no":

        tts_start = perf_counter()

        audio_file = await generate_audio(REJECTION_MESSAGE)

        tts_time = perf_counter() - tts_start

        total_time = perf_counter() - request_start

        interview_time = (
            perf_counter()
            - sessions[session_id]["start_time"]
        )

        print(f"TTS Time         : {tts_time:.2f} sec")
        print(f"API Time         : {total_time:.2f} sec")
        print("\nINTERVIEW REJECTED")
        print(f"Total Duration   : {interview_time:.2f} sec")
        print("========================================\n")

        return {
            "status": "reject",
            "message": REJECTION_MESSAGE,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    # ---------------------------------------------------
    # INVALID ANSWER
    # ---------------------------------------------------
    if result != "yes":

        retry_message = "Please answer yes or no"

        tts_start = perf_counter()

        audio_file = await generate_audio(retry_message)

        tts_time = perf_counter() - tts_start

        total_time = perf_counter() - request_start

        print(f"TTS Time         : {tts_time:.2f} sec")
        print(f"API Time         : {total_time:.2f} sec")
        print("Status           : Retry")
        print("========================================\n")

        return {
            "status": "retry",
            "message": retry_message,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    # ---------------------------------------------------
    # VALID ANSWER
    # ---------------------------------------------------
    sessions[session_id]["question_idx"] += 1

    # ---------------------------------------------------
    # COMPLETED
    # ---------------------------------------------------
    if sessions[session_id]["question_idx"] >= len(QUESTIONS):

        tts_start = perf_counter()

        audio_file = await generate_audio(SUCCESS_MESSAGE)

        tts_time = perf_counter() - tts_start

        total_time = perf_counter() - request_start

        interview_time = (
            perf_counter()
            - sessions[session_id]["start_time"]
        )

        print(f"TTS Time         : {tts_time:.2f} sec")
        print(f"API Time         : {total_time:.2f} sec")

        print("\n########################################")
        print("INTERVIEW COMPLETED")
        print(f"Total Duration   : {interview_time:.2f} sec")
        print("########################################\n")

        return {
            "status": "success",
            "message": SUCCESS_MESSAGE,
            "audio": "/" + audio_file.replace("\\", "/")
        }

    # ---------------------------------------------------
    # NEXT QUESTION
    # ---------------------------------------------------
    total_time = perf_counter() - request_start

    print(f"API Time         : {total_time:.2f} sec")
    print("Status           : Next Question")
    print("========================================\n")

    return {
        "status": "next"
    }
