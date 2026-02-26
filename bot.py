import telebot
import logging

# Replace with your actual bot token from @BotFather
BOT_TOKEN = '8307990040:AAGt9Xfh0gli2Tbb1CA42c_E-mAlLWjkOM4'
bot = telebot.TeleBot(BOT_TOKEN)

# Enable logging to see errors (optional)
logging.basicConfig(level=logging.WARNING)

# A publicly accessible image URL for the start message
WELCOME_IMAGE_URL = "https://tmpfiles.org/dl/26326290/download7.jpg"  # Random placeholder

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Send a welcome message with instructions and an image."""
    chat_id = message.chat.id
    welcome_text = (
        '<tg-emoji emoji-id="6336707083940927246">👋</tg-emoji> <b>Welcome to Custom Emoji ID Bot!</b>\n\n'
        'Send me any message containing a <b>Telegram Premium custom emoji</b> '
        'and I\'ll reply with its unique ID.\n\n'
        '<tg-emoji emoji-id="5325547803936572038">✨</tg-emoji> <b>How to use:</b>\n'
        '• Just type a message with a custom emoji (from a Premium pack)\n'
        '• I\'ll instantly reply with the emoji\'s ID\n'
        '• Works in groups and private chats\n\n'
        '<tg-emoji emoji-id="5319230516929502602">🔍</tg-emoji> <b>Note:</b> '
        'Only custom (Premium) emojis are detected. Standard Unicode emojis are ignored.\n\n'
        'Use /help to see this message again.'
    )

    try:
        # Send photo with caption (the image URL is fetched by Telegram)
        bot.send_photo(
            chat_id,
            photo=WELCOME_IMAGE_URL,
            caption=welcome_text,
            parse_mode="HTML"
        )
    except Exception as e:
        # Fallback if image fails to send
        logging.error(f"Failed to send photo: {e}")
        bot.send_message(chat_id, welcome_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def get_emoji_id(message):
    """Extract custom emoji ID from any incoming message."""
    if message.entities:
        for entity in message.entities:
            if entity.type == 'custom_emoji':
                emoji_id = entity.custom_emoji_id
                # Success response with custom emojis
                response = (
                    f'<tg-emoji emoji-id="6257784371227399216">✅</tg-emoji> '
                    f'<b>Custom Emoji Detected!</b>\n\n'
                    f'<tg-emoji emoji-id="6336581950068757210">🆔</tg-emoji> '
                    f'<b>ID:</b> <code>{emoji_id}</code>\n\n'
                    f'<tg-emoji emoji-id="5798831858263265607">💡</tg-emoji> '
                    f'You can use this ID in bots that support custom emoji.'
                )
                bot.reply_to(message, response, parse_mode="HTML")
                return

    # No custom emoji found - error response with custom cross mark
    error_response = (
        f'<tg-emoji emoji-id="6179128006615765757">❌</tg-emoji> '
        f'<b>No custom emoji found.</b>\n\n'
        f'Please send a message that includes a Telegram Premium custom emoji.\n'
        f'Use /help for instructions.'
    )
    bot.reply_to(message, error_response, parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
