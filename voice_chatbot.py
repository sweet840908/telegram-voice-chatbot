from telegram.ext import Updater, MessageHandler, Filters
import telegram, openai, os
from moviepy.editor import AudioFileClip

openai.api_key = "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"
TELEGRAM_API_TOKEN = "6417957762:AAH3VzLAzLcaD5PaLWWk0un0Iw2riCOUVYI"
chat_id = '6386409618'
bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
messages = [{"role": "system", "content": "You are Q-bot, a helpful AI assistant. "}]


def tts(text):
    output_file = "temp/output.ogg"
    response = openai.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(output_file)
    voice_file = os.path.abspath(output_file)
    bot.send_voice(chat_id=chat_id, voice=open(voice_file, 'rb'))


def voice_message(update, context):
    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file.download("temp/voice_message.ogg")
    audio_clip = AudioFileClip("temp/voice_message.ogg")
    audio_clip.write_audiofile("temp/voice_message.mp3")
    audio_file = open("temp/voice_message.mp3", "rb")
    transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    update.message.reply_text(text=f"*[You]:* _{transcript}_", parse_mode=telegram.ParseMode.MARKDOWN)
    messages.append({"role": "user", "content": transcript})
    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages, max_tokens=100)
    ChatGPT_reply = response.choices[0].message.content
    tts(ChatGPT_reply)
    update.message.reply_text(text=f"*[Q-bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
    if ChatGPT_reply:
        messages.append({"role": "assistant", "content": ChatGPT_reply})


def main():
    bot.send_message(chat_id=chat_id, text="Hello! I am Q-bot, your helpful AI assistant")
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
