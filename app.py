import os
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

# Initialize Flask app
app = Flask(__name__)

# Use the provided bot token
BOT_TOKEN = '8184177184:AAH0nl6KHpNixXRuIZwm0ubrQYEDoW-6R94'

CHANNEL_IDS = []  # List to store channel IDs

@app.route('/')
def health_check():
    return "Health check passed", 200

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Start", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Click the button to start:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'start':
        query.edit_message_text(text="Please select the channel to send posts to and send the last message of the channel.")

def add_channel(update: Update, context: CallbackContext) -> None:
    channel_id = update.message.forward_from_chat.id
    if channel_id not in CHANNEL_IDS:
        CHANNEL_IDS.append(channel_id)
    update.message.reply_text(f"Channel added: {channel_id}. Now send the post (text, image, video).")

def handle_post(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    user_data['post'] = update.message
    keyboard = [
        [InlineKeyboardButton("Delete Msg", callback_data='delete_msg')],
        [InlineKeyboardButton("Add URL", callback_data='add_url')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose an action:', reply_markup=reply_markup)

def handle_buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    post = user_data.get('post')
    if query.data == 'delete_msg':
        post.delete()
        query.edit_message_text(text="Message deleted. Please send a new post.")
    elif query.data == 'add_url':
        query.edit_message_text(text="Send the names and links in the format: `name1 link1 | name2 link2 | ...`")

def add_urls(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    post = user_data.get('post')
    urls = update.message.text.split('|')
    buttons = [[InlineKeyboardButton(name, url=link)] for name, link in (url.split() for url in urls)]

    for channel_id in CHANNEL_IDS:
        context.bot.send_message(chat_id=channel_id, text=post.text, reply_markup=InlineKeyboardMarkup(buttons))

    update.message.reply_text("Post sent to the channel.")

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.forwarded & Filters.chat_type.channel, add_channel))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_post))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CallbackQueryHandler(handle_buttons))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex(r'^name\\d+ link\\d+'), add_urls))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Start the Flask app
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    # Start the Telegram bot
    main()
