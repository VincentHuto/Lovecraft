from openai import OpenAI
import os
from playsound import playsound # type: ignore
import pyaudio # type: ignore
import wave
import speech_recognition as sr # type: ignore
from gpiozero import LED # type: ignore

# Initialize the OpenAI client once
client = OpenAI(api_key = "")



# Main Loop where it waits and listens for words, mainly the lovecraft wakeup cue
def listen_for_wake_word(wake_word):
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Set up the microphone input
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening for the wake word...")

        # Continuously listen
        while True:
            try:
                audio = recognizer.listen(source, timeout=5)  # Listen for audio
                # Recognize speech using Google's speech recognition
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")

                # Check if the wake word was said
                if wake_word in text:
                    print(f"Wake word '{wake_word}' detected!")
                    prompt = text.replace(wake_word,"")
                    if not prompt or len(prompt) < 4:
                        doRecordAudioLoop("")
                    else:
                        doRecordAudioLoop(prompt)
                    break  # Exit or perform an action

            except sr.WaitTimeoutError:
                print("No speech detected within the timeout period.")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

# Takes in the transcribtion message and sends it to OpenAI
def generate_response_msg(assistant_type, prompt):
    """Generates a response message using the OpenAI chat model."""
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": assistant_type},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating response message: {e}")
        return "Error in generating response."

# Converts Transcribed audio mp3 to speech output and outputs it to a temp output.mp3
def text_to_speech(message, file_name="audio_output.mp3"):
    """Generates speech from text using the OpenAI API and saves it to a file."""
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="echo",
            input=message,
        ) as response:
            print(message)
            response.stream_to_file(file_name)
    except Exception as e:
        print(f"Failed to generate speech: {e}")
    return file_name

# Function to transcribe audio
def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        response =client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return response

#Playes the audio file and deletes it after
def play_and_delete_audio(file_name):
    """Plays an audio file and deletes it afterwards."""
    try:
        playsound(file_name)
    except Exception as e:
        print(f"Error playing the sound: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
            print("File deleted.")
        else:
            print("File does not exist.")
        if os.path.exists("audio_input.wav"):
            os.remove("audio_input.wav")
            print("audio_input.wav deleted.")
        else:
            print("audio_input.wav does not exist.")   

def doRecordAudioLoop(incoming_prompt):
    if not incoming_prompt:
        # Audio recording parameters
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "audio_input.wav"
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
        transcription = transcribe_audio(WAVE_OUTPUT_FILENAME)
        prompt = transcription.text
        print(transcription)
    else:
        prompt = incoming_prompt

    # Example usage
    assistant_type = "You are an old fashioned personal assistant, skilled in explaining complex concepts with creative flair, in a clear and concise manner."
   

    msg = generate_response_msg(assistant_type, prompt)
    audio_file = text_to_speech(msg)
    
    play_and_delete_audio(audio_file)
    listen_for_wake_word("lovecraft")

if __name__ == "__main__":
    #Initial Startup
    listen_for_wake_word("lovecraft")
    #First time it starts the loop
    doRecordAudioLoop()
    
