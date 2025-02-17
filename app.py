from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import os

# Initialize Flask app
app = Flask(__name__)

# Replace with your actual bot token
BOT_TOKEN = os.getenv('8184177184:AAH0nl6KHpNixXRuIZwm0ubrQYEDoW-6R94')
CHANNEL_IDS = []  # List to store channel IDs

@app.route('/')
def health_check():
    return "Health check passed", 200

def start(update: Update, context: CallbackContext) -> None:
    channels = CHANNEL_IDS  # Assuming CHANNEL_IDS is pre-populated with channel IDs
    keyboard = [[InlineKeyboardButton(f"Channel {i+1}", callback_data=f'channel_{i}')] for i in range(len(channels))]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select the channel to send posts to:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('channel_'):
        channel_index = int(data.split('_')[1])
        channel_id = CHANNEL_IDS[channel_index]
        query.edit_message_text(text=f"Channel selected: {channel_id}. Now send the post (text, image, video).")
        context.user_data['selected_channel'] = channel_id

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
        if post:
            post.delete()
            query.edit_message_text(text="Message deleted. Please send a new post.")
        else:
            query.edit_message_text(text="No message found to delete.")
    elif query.data == 'add_url':
        query.edit_message_text(text="Send the names and links in the format: `name1 link1 | name2 link2 | ...`")

def add_urls(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    post = user_data.get('post')
    selected_channel = user_data.get('selected_channel')
    urls = update.message.text.split('|')
    buttons = [[InlineKeyboardButton(name, url=link)] for name, link in (url.split() for url in urls)]

    if selected_channel:
        update.message.bot.send_message(chat_id=selected_channel, text=post.text, reply_markup=InlineKeyboardMarkup(buttons))
        update.message.reply_text("Post sent to the channel.")
    else:
        update.message.reply_text("No channel selected.")

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
