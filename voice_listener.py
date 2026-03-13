# voice_listener.py
import os, asyncio, json, tempfile, time
import sounddevice as sd
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

BASE_WS_URL = "wss://api.smallest.ai/waves/v1/pulse/get_text"
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 100
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)

KEYWORD_ALIASES = {
    "claritin": ["claritin", "clarity", "claritan", "clarita", "clarinet"],
    "dayquil": ["dayquil", "day quil", "daiquiri", "dequil", "dayco"]
}

def _check_keywords(transcript: str):
    t = transcript.lower().strip()
    for keyword, aliases in KEYWORD_ALIASES.items():
        for alias in aliases:
            if alias in t:
                return keyword
    return None

async def _listen_ws() -> str:
    params = {
        "language": "en",
        "encoding": "linear16",
        "sample_rate": str(SAMPLE_RATE),
        "word_timestamps": "false",
    }
    url = f"{BASE_WS_URL}?{urlencode(params)}"
    headers = {"Authorization": f"Bearer {os.getenv('SMALLEST_API_KEY')}"}

    audio_queue = asyncio.Queue()
    result = {"keyword": None}
    stop_event = asyncio.Event()

    def audio_callback(indata, frames, time_info, status):
        if not stop_event.is_set():
            audio_queue.put_nowait(bytes(indata))

    stream = sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SAMPLES,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    )

    async with websockets.connect(url, additional_headers=headers) as ws:
        print("🎤 Speak now...")

        async def send_audio():
            with stream:
                while not stop_event.is_set():
                    try:
                        chunk = await asyncio.wait_for(audio_queue.get(), timeout=1)
                        await ws.send(chunk)
                    except asyncio.TimeoutError:
                        continue

        async def send_finalize():
            while not stop_event.is_set():
                await asyncio.sleep(2)
                await ws.send(json.dumps({"type": "finalize"}))

        async def receive_transcripts():
            async for message in ws:
                data = json.loads(message)
                transcript = data.get("transcript", "")
                is_final = data.get("is_final", False)
                if transcript:
                    print(f"{'[FINAL]' if is_final else '[interim]'} {transcript}")
                if is_final and transcript:
                    keyword = _check_keywords(transcript)
                    if keyword:
                        result["keyword"] = keyword
                        stop_event.set()
                        return
                # timeout after 8 seconds of finals with no keyword
                if is_final and not result["keyword"]:
                    pass  # keep listening

        try:
            await asyncio.wait_for(
                asyncio.gather(send_audio(), receive_transcripts(), send_finalize()),
                timeout=10
            )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

    return result["keyword"]

def listen() -> str:
    import websockets as _ws  # ensure imported
    global websockets
    import websockets
    
    for attempt in range(3):
        print(f"🎤 Listening... (attempt {attempt+1}/3)")
        keyword = asyncio.run(_listen_ws())
        print(f"Heard keyword: {keyword}")
        if keyword:
            return keyword
        if attempt < 2:
            speak("Sorry, I didn't catch that. Please say Claritin or DayQuil.")
    return None

def speak(msg: str):
    print(f"🔊 {msg}")
    try:
        import subprocess
        from smallestai.waves import WavesClient
        client = WavesClient(api_key=os.getenv("SMALLEST_API_KEY"))
        audio_bytes = client.synthesize(msg)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        subprocess.run(["afplay", tmp_path])
        os.unlink(tmp_path)
        time.sleep(1)
    except Exception as e:
        print(f"TTS fallback: {e}")
        time.sleep(1)