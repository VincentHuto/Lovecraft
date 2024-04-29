import pyaudio
import wave

from openai import OpenAI
client = OpenAI()

# OpenAI API Key

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
print("Recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("Finished recording.")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# Saving the recorded data as a wave file
with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

# Function to transcribe audio
def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        response =client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return response

# Transcribing the audio file
transcription = transcribe_audio(WAVE_OUTPUT_FILENAME)
print(transcription)

