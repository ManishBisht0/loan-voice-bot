import edge_tts, uuid, os, asyncio

VOICE="en-US-JennyNeural"

async def generate_audio(text:str):
    os.makedirs("static/audio", exist_ok=True)
    filename=f"static/audio/{uuid.uuid4()}.mp3"
    await edge_tts.Communicate(text=text, voice=VOICE).save(filename)
    return filename
