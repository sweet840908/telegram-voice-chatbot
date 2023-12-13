from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
import telegram, openai, os, time
from moviepy.editor import AudioFileClip
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

openai.api_key = "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"
TELEGRAM_API_TOKEN = "6417957762:AAH3VzLAzLcaD5PaLWWk0un0Iw2riCOUVYI"
chat_id = '6386409618'
difficulty_set, topic_mode = False, False
bot = telegram.Bot(token=TELEGRAM_API_TOKEN)


def difficulty_setting(update, context):
    global y, messages, difficulty_set

    if difficulty_set:
        return

    elif update.message.text in ['Low (1000 words)', 'Intermediate (3000 words)', 'Advanced (8000 words)']:
        if update.message.text == 'Low (1000 words)':
            y = ('now your student is a 5-year-old baby, so use the most common and basic 1000 words in English, '
                 'keep it extremely simple')
            text = "*[Q-bot]:* I will use very simple language! "
        elif update.message.text == 'Intermediate (3000 words)':
            y = 'now your student is a 11-year-old child, so use the basic 3000 words in English'
            text = "*[Q-bot]:* I will use daily language! "
        else:  # Advanced (8000 words)
            y = 'now your student is a 18-year-old adult, so use vocabulary from 8000 words in TOEFL, IELTS and GRE'
            text = "*[Q-bot]:* I will use advanced words and difficult structures! "
        difficulty_set = True
        messages = [{"role": "system",
                    "content": "You are Q-bot, a helpful English teacher. "
                     "The instruction is as follows, follow it but don't let your student know:" + y}]
        update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove(), parse_mode=telegram.ParseMode.MARKDOWN)
        
    else:
        custom_keyboard = [['Low (1000 words)', 'Intermediate (3000 words)', 'Advanced (8000 words)']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(text="*[Q-bot]:* Please select your level", reply_markup=reply_markup,
                                  parse_mode=telegram.ParseMode.MARKDOWN)


def tts(text):
    output_file = "temp/output.ogg"
    response = openai.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(output_file)
    voice_file = os.path.abspath(output_file)
    bot.send_voice(chat_id=chat_id, voice=open(voice_file, 'rb'))


def voice_message(update, context):
    if topic_mode:
        messages.append({"role": "system",
                         "content": "The student's speak of the topic given by you is as follows."
                                    "Please give him/her some remark. Be strict but helpful."
                                    "Evaluate from these aspects: Vocabulary, grammatical range and accuracy."
                                    "Make sure the student made efforts."})

    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file.download("temp/voice_message.ogg")
    audio_clip = AudioFileClip("temp/voice_message.ogg")
    audio_clip.write_audiofile("temp/voice_message.mp3")
    audio_file = open("temp/voice_message.mp3", "rb")
    transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    update.message.reply_text(text=f"*[You]:* _{transcript}_", parse_mode=telegram.ParseMode.MARKDOWN)
    content = transcript+y
    messages.append({"role": "user", "content": content})
    response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages, max_tokens=100)
    ChatGPT_reply = response.choices[0].message.content
    tts(ChatGPT_reply)
    update.message.reply_text(text=f"*[Q-bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
    if ChatGPT_reply:
        messages.append({"role": "assistant", "content": ChatGPT_reply})
    if topic_mode:
        message4 = {"role": "user", "content": "Give me a sample speech on the topic(at most 100 words)"}
        messages.append(message4)
        sample1 = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages, max_tokens=300)
        sample = sample1.choices[0].message.content
        messages.append({"role": "assistant", "content": str(sample)})
        text = "我的小主人，你表现得很棒，请容许我搜索一下我的数据库，为你提供一个关于此话题的参考英语文本可以吗？" + str(sample)
        update.message.reply_text(text)
        tts(text)


def topic(update: Update, context: CallbackContext) -> None:
    global topic_mode
    topic_mode = True
    message1 = {"role": "user", "content": "Give me a topic for oral english(at most 3 words)"}
    messages.append(message1)
    topic1 = openai.chat.completions.create(model="gpt-3.5-turbo", messages=[message1], max_tokens=10)
    topic = topic1.choices[0].message.content
    messages.append({"role": "assistant", "content": str(topic)})
    text = "今天要不要练习一下英语口语，要么我们随便聊，要么我们今天练习"+str(topic)+"的话题好吗？"
    update.message.reply_text(text)
    tts(text)

    time.sleep(10)
    try:
        context.bot.getFile(update.message.voice.file_id)
        print("answered")
    except:
        print("not answered")
        message2 = {"role": "user", "content": "Give me 5 key words on the topic(at most 5 words)"}
        messages.append(message2)
        keywords1 = openai.chat.completions.create(model="gpt-3.5-turbo", messages=messages, max_tokens=50)
        keywords = keywords1.choices[0].message.content
        messages.append({"role": "assistant", "content": str(keywords)})
        text = "我的小主人，要不要我推荐给你一些关键词来帮助你扩充你的思路呢？\n" + str(keywords)
        update.message.reply_text(text)
        tts(text)


def main():
    custom_keyboard = [['Low (1000 words)', 'Intermediate (3000 words)', 'Advanced (8000 words)']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(chat_id=chat_id, text="Hello! I am Q-bot, your English teacher. Please select your level:",
                     reply_markup=reply_markup)

    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), difficulty_setting))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
    dispatcher.add_handler(CommandHandler("topic", topic))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
