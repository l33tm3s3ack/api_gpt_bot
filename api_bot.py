from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import Bot, ReplyKeyboardMarkup
import os
import openai
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')
openai_key = os.getenv('OPENAI_API_KEY')


def start(update, context):
    chat = update.effective_chat
    text = '''Hi! I can send your messages to AI.
    Which AI do you want to talk to?'''
    buttons = ReplyKeyboardMarkup(
        [['/gpt_turbo', '/code_davinci', '/text_davinci']]
    )
    context.bot.send_message(chat_id=chat.id, text=text, reply_markup=buttons)


def choice_model(update, context):
    chat = update.effective_chat
    text = update.message.text
    model_list = {
        'gpt_turbo': 'gpt-3.5-turbo',
        'code_davinci': 'text-davinci-003',
        'text_davinci': 'code-davinci-002'
    }
    chosen_model = model_list[text[1:]]
    context.user_data['model'] = chosen_model
    openai.api_key = openai_key
    if chosen_model == 'gpt-3.5-turbo':
        response = openai.ChatCompletion.create(
            model=chosen_model,
            messages=[
                {"role": "user", "content": "Say this is a test."}
            ]

        )
        try:
            response_text = response.choices[0].message.content
        except KeyError:
            user_response = '''Looks like something goes wrong.
            But you still can try to send a message.'''
            context.bot.send_message(chat_id=chat.id, text=user_response)
    else:
        response = openai.Completion.create(
            model=chosen_model,
            prompt='Say this is a test.',
            max_tokens=4000,
            temperature=0
        )
        try:
            response_text = response['choices'][0]['text']
        except KeyError:
            user_response = '''Looks like something goes wrong.
            But you still can try to send a message.'''
            context.bot.send_message(chat_id=chat.id, text=user_response)
    if response_text.find('test') == -1:
        user_response = '''AI responds odd,
        but still can try to send a message.'''
    else:
        user_response = 'Looks ok, you can send a message.'
    context.bot.send_message(chat_id=chat.id, text=user_response)


def input_analyzer(update, context):
    chat = update.effective_chat
    text = update.message.text
    try:
        chosen_model = context.user_data['model']
    except KeyError:
        user_response = 'you need to choose model first.'
        context.bot.send_message(chat_id=chat.id, text=user_response)
    openai.api_key = openai_key
    if chosen_model == 'gpt-3.5-turbo':
        response = openai.ChatCompletion.create(
            model=chosen_model,
            messages=[
                {"role": "user", "content": text}
            ]

        )
        try:
            response_text = response.choices[0].message.content
        except KeyError:
            user_response = '''Didn't receive correct response from OpenAI.'''
            context.bot.send_message(chat_id=chat.id, text=user_response)
    else:
        response = openai.Completion.create(
            model=chosen_model,
            prompt=text,
            max_tokens=4000,
            temperature=0
        )
        try:
            response_text = response['choices'][0]['text']
        except KeyError:
            user_response = '''Didn't receive correct response from OpenAI.'''
            context.bot.send_message(chat_id=chat.id, text=user_response)
    context.bot.send_message(chat_id=chat.id, text=response_text)


def main():
    updater = Updater(token=token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler(
        ['gpt_turbo', 'code_davinci', 'text_davinci'], choice_model
    ))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.text, input_analyzer
    ))
    updater.start_webhook(
        listen='0.0.0.0',
        port=8443,
        key='private.key',
        cert='cert.pem',
        webhook_url='https://62.113.113.158:8443'
    )
    updater.idle()


if __name__ == '__main__':
    main()
