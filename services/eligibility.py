YES_WORDS = ["yes","yeah","yep","sure","correct"]
NO_WORDS = ["no","nope"]

def classify_answer(text:str):
    text = text.lower()
    if any(w in text for w in YES_WORDS):
        return "yes"
    if any(w in text for w in NO_WORDS):
        return "no"
    return "unknown"
