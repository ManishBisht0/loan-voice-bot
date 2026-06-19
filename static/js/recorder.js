
const sessionId = crypto.randomUUID();

async function playAudio(audioUrl) {
    try {
        const audio = new Audio(audioUrl);

        return new Promise((resolve, reject) => {
            audio.onended = resolve;
            audio.onerror = reject;

            audio.play().catch(reject);
        });
    } catch (err) {
        console.error("Audio playback failed:", err);
    }
}

async function loadQuestion() {
    try {
        const response = await fetch(`/question?session_id=${sessionId}`);
        const data = await response.json();

        document.getElementById("question").innerText = data.question;

        if (data.audio) {
            await playAudio(data.audio);
        }
    } catch (err) {
        console.error("Error loading question:", err);
    }
}

async function recordAnswer() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        const recorder = new MediaRecorder(stream);
        const chunks = [];

        recorder.ondataavailable = (e) => {
            chunks.push(e.data);
        };

        recorder.start();

        document.getElementById("status").innerText = "Listening...";

        setTimeout(() => {
            recorder.stop();
        }, 3000);

        recorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());

            const blob = new Blob(chunks, {
                type: "audio/webm"
            });

            const formData = new FormData();
            formData.append("audio", blob, "answer.webm");

            const response = await fetch(
                `/answer?session_id=${sessionId}`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            document.getElementById("status").innerText = "";

            // Load next question
            if (data.status === "next") {
                await loadQuestion();
                return;
            }

            // Show final/retry message
            document.body.innerHTML = `
                <div style="text-align:center;margin-top:100px;">
                    <h1>${data.message}</h1>
                </div>
            `;

            // Speak message if audio exists
            if (data.audio) {
                await playAudio(data.audio);
            }
        };
    } catch (err) {
        console.error("Recording error:", err);
        document.getElementById("status").innerText =
            "Microphone access denied or recording failed.";
    }
}

window.onload = loadQuestion;