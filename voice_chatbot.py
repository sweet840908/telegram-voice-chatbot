from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import telegram, openai

openai.api_key = "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"
TELEGRAM_API_TOKEN = "6753361647:AAF-_FbQxenuszO7VGmSv_TFgp0CvS524Ek"
bot = telegram.Bot(token=TELEGRAM_API_TOKEN)
messages = [{"role": "system", "content": "You are Q-bot, a helpful AI assistant. "}]


def start(update, context):
    update.message.reply_text(text="Hello! I am Q-bot, your helpful AI assistant.", parse_mode=telegram.ParseMode.MARKDOWN)


def tts(text):
    output_file = "temp/output.ogg"
    response = openai.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(output_file)
    return output_file


def voice_message(update, context):
    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file.download("temp/voice_message.ogg")
    audio_file = open("temp/voice_message.ogg", "rb")
    transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    update.message.reply_text(text=f"*[You]:* _{transcript}_", parse_mode=telegram.ParseMode.MARKDOWN)
    messages.append({"role": "user", "content": transcript})
    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages, max_tokens=100)
    ChatGPT_reply = response.choices[0].message.content
    update.message.reply_text(text=f"*[Q-bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
    if ChatGPT_reply:
        messages.append({"role": "assistant", "content": ChatGPT_reply})
    with open(tts(ChatGPT_reply), 'rb') as voice_file:
        update.message.reply_voice(voice=voice_file)


def main():
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
