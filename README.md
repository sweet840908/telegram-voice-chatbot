# telegram-voice-chatbot
The robot will convert the voice you send into text, send it to chatgpt, and then convert the answer returned by chatgpt into voice and send it to you.

# Notice
1. Replace openai.api_key with your own api key. You can get it from here: https://platform.openai.com/api-keys

2. Replace TELEGRAM_API_TOKEN with the api token of your own bot. Send "/mybots" to BotFather and select @<the name of your bot> -> API Token. 

3. Replace chat_id with yours. Open the telegram website and the 10-digit number in the url is your chat id. 

# Requirements
`pip install os openai telegram moviepy`
