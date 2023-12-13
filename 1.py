from openai import OpenAI
import pygame
import time

pygame.mixer.init()
client = OpenAI(api_key="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")

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are Q-bot. "},
    {"role": "user", "content": "Tell me a story. "}
  ]
)
print(completion.choices[0].message.content)

response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=completion.choices[0].message.content,
)

response.stream_to_file("temp/output.mp3")
time.sleep(2)
pygame.mixer.music.load("temp/output.mp3")
pygame.mixer.music.play()
