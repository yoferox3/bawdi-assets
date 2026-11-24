# Make one Hindi voice clip per script line with free Microsoft voices (edge-tts),
# plus word timings for subtitles. Output: audio/NNN_SPEAKER.mp3 and audio/lines.json
import asyncio, json, os, edge_tts

VOICES = {
    "N":              ("hi-IN-MadhurNeural", "-6%",  "-6Hz"),
    "KAKA":           ("hi-IN-MadhurNeural", "-14%", "-14Hz"),
    "ARJUN":          ("hi-IN-MadhurNeural", "+0%",  "+2Hz"),
    "KABIR":          ("hi-IN-MadhurNeural", "+10%", "+16Hz"),
    "KESAR":          ("hi-IN-SwaraNeural",  "-22%", "-8Hz"),
    "KESAR_AS_KABIR": ("hi-IN-MadhurNeural", "+4%",  "+10Hz"),
}

async def one(i, sc, sp, text, out):
    voice, rate, pitch = VOICES[sp]
    name = f"audio/{i:03d}_{sp}.mp3"
    words = []
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    with open(name, "wb") as fh:
        async for ch in com.stream():
            if ch["type"] == "audio":
                fh.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]])
    out.append({"i": i, "scene": sc, "speaker": sp, "text": text, "file": name, "words": words})
    print(i, sp, len(words), "words")

async def main():
    os.makedirs("audio", exist_ok=True)
    d = json.load(open("script.json"))
    out, i = [], 0
    for s in d["scenes"]:
        for sp, text in s["lines"]:
            await one(i, s["id"], sp, text, out)
            i += 1
    json.dump(out, open("audio/lines.json", "w"), ensure_ascii=False, indent=1)
    print("DONE", len(out))

asyncio.run(main())
