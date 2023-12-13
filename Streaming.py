import time
import os
import pygame
from openai import OpenAI

client = OpenAI(api_key="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")
messages = [{"role": "system", "content": "You are Q-bot"}]


def gpt(content):
    sentence, file_num = "", 1
    message = {"role": "user", "content": content}
    messages.append(message)
    reply = client.chat.completions.create(model="gpt-4-1106-preview", messages=messages, stream=True)

    for chunk in reply:
        if chunk.choices:
            word = chunk.choices[0].delta.content
            if word:  # Ensure word is not empty
                sentence += word
                if ((file_num == 1 and word.endswith((',', '.', '!', '?', '。', '，', '？', '！', '……'))) or
                        word.endswith(('.', '!', '?', '。', '！', '？', '……'))):
                    print(sentence.strip())
                    output_file = "temp/" + str(file_num) + ".mp3"
                    audio_response = client.audio.speech.create(model="tts-1", voice="nova", input=sentence)
                    audio_response.stream_to_file(output_file)
                    voice_file = os.path.abspath(output_file)
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)

                    pygame.mixer.music.load(voice_file)
                    pygame.mixer.music.play()
                    messages.append({"role": "assistant", "content": sentence})
                    file_num += 1
                    sentence = ""


def main():
    pygame.mixer.init()
    while 1:
        contents = input("Please enter your message: ")
        gpt(contents)
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)


if __name__ == '__main__':
    main()
