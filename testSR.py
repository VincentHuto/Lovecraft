import speech_recognition as sr

def listen_for_wake_word(wake_word="hello"):
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
                    break  # Exit or perform an action

            except sr.WaitTimeoutError:
                print("No speech detected within the timeout period.")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    listen_for_wake_word()
