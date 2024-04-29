from pathlib import Path
from openai import OpenAI
client = OpenAI()

with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input="""I see skies of blue and clouds of white
             The bright blessed days, the dark sacred nights
             And I think to myself
             What a wonderful world""",
) as response:
    response.stream_to_file("speech.mp3")