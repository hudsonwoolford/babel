import whisper

model = whisper.load_model("base")
result = model.transcribe("input/IA_ClientInterview_1.m4a")

with open("output/Transcription.txt", mode='w', encoding='utf-8') as f:
    f.write(result["text"])
