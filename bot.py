import telebot
import logging
import re

# Replace with your actual bot token from @BotFather
BOT_TOKEN = '8307990040:AAGt9Xfh0gli2Tbb1CA42c_E-mAlLWjkOM4'
bot = telebot.TeleBot(BOT_TOKEN)

# Enable logging to see errors (optional)
logging.basicConfig(level=logging.WARNING)

# A publicly accessible image URL for the start message
WELCOME_IMAGE_URL = "https://tmpfiles.org/dl/26326290/download7.jpg"  # Random placeholder

def extract_emoji_id_from_message(message):
    """Helper function to extract custom emoji ID from a message"""
    if message.entities:
        for entity in message.entities:
            if entity.type == 'custom_emoji':
                return entity.custom_emoji_id
    return None

def is_bot_mentioned(message):
    """Check if the bot is mentioned in the message"""
    bot_username = bot.get_me().username
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                mention = message.text[entity.offset:entity.offset + entity.length]
                if mention == f"@{bot_username}":
                    return True
    return False

def should_process_message(message):
    """Determine if the bot should process this message in a group"""
    chat_type = message.chat.type
    
    # Always process in private chats
    if chat_type == 'private':
        return True
    
    # In groups/supergroups, only process if:
    # 1. Bot is mentioned, OR
    # 2. Message starts with /emoji_id command
    if chat_type in ['group', 'supergroup']:
        # Check for bot mention
        if is_bot_mentioned(message):
            return True
        
        # Check for /emoji_id command
        if message.text and message.text.startswith('/emoji_id'):
            return True
    
    return False

def clean_message_for_emoji(message):
    """Remove command and bot mention to process only the emoji part"""
    if message.text and message.text.startswith('/emoji_id'):
        # Remove the command part
        text_without_command = re.sub(r'^/emoji_id@?\w*\s*', '', message.text)
        
        # Create a new message object with cleaned text
        # Note: This is a simplified approach. In production, you might want to
        # create a proper copy of the message or handle this differently
        message.text = text_without_command if text_without_command else message.text
    
    return message

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Send a welcome message with instructions and an image."""
    chat_id = message.chat.id
    welcome_text = (
        '<tg-emoji emoji-id="6336707083940927246">👋</tg-emoji> <b>Welcome to Custom Emoji ID Bot!</b>\n\n'
        'Send me any message containing a <b>Telegram Premium custom emoji</b> '
        'and I\'ll reply with its unique ID.\n\n'
        '<tg-emoji emoji-id="5325547803936572038">✨</tg-emoji> <b>How to use:</b>\n'
        '• <b>In private chat:</b> Just send any message with a custom emoji\n'
        '• <b>In groups:</b> Tag me (@dax_emoji_id_bot) or use /emoji_id followed by the emoji\n'
        '• I\'ll instantly reply with the emoji\'s ID\n\n'
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

@bot.message_handler(commands=['emoji_id'])
def emoji_id_command(message):
    """Handle the /emoji_id command specifically"""
    # Clean the message to remove the command part
    cleaned_message = clean_message_for_emoji(message)
    
    # Process the cleaned message for emoji ID
    emoji_id = extract_emoji_id_from_message(cleaned_message)
    
    if emoji_id:
        response = (
            f'<tg-emoji emoji-id="6257784371227399216">✅</tg-emoji> '
            f'<b>Custom Emoji Detected!</b>\n\n'
            f'<tg-emoji emoji-id="6336581950068757210">🆔</tg-emoji> '
            f'<b>ID:</b> <code>{emoji_id}</code>\n\n'
            f'<tg-emoji emoji-id="5798831858263265607">💡</tg-emoji> '
            f'You can use this ID in bots that support custom emoji.'
        )
    else:
        response = (
            f'<tg-emoji emoji-id="6179128006615765757">❌</tg-emoji> '
            f'<b>No custom emoji found.</b>\n\n'
            f'Please include a Telegram Premium custom emoji after the command.\n'
            f'Example: <code>/emoji_id {get_emoji_example()}</code>'
        )
    
    bot.reply_to(message, response, parse_mode="HTML")

def get_emoji_example():
    """Return a sample custom emoji for the example"""
    # This is just a placeholder - you might want to use a real custom emoji ID
    return "😊"

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all messages, but filter based on context"""
    # Check if we should process this message
    if not should_process_message(message):
        return
    
    # If this was triggered by a mention, we don't want to process commands again
    if message.text and message.text.startswith('/emoji_id'):
        return
    
    # For mentions, clean the message (remove the mention)
    if is_bot_mentioned(message):
        # Remove the bot mention from the message text for processing
        bot_username = f"@{bot.get_me().username}"
        if message.text:
            message.text = message.text.replace(bot_username, '').strip()
    
    # Extract emoji ID from the message
    emoji_id = extract_emoji_id_from_message(message)
    
    if emoji_id:
        response = (
            f'<tg-emoji emoji-id="6257784371227399216">✅</tg-emoji> '
            f'<b>Custom Emoji Detected!</b>\n\n'
            f'<tg-emoji emoji-id="6336581950068757210">🆔</tg-emoji> '
            f'<b>ID:</b> <code>{emoji_id}</code>\n\n'
            f'<tg-emoji emoji-id="5798831858263265607">💡</tg-emoji> '
            f'You can use this ID in bots that support custom emoji.'
        )
    else:
        response = (
            f'<tg-emoji emoji-id="6179128006615765757">❌</tg-emoji> '
            f'<b>No custom emoji found.</b>\n\n'
            f'Please send a message that includes a Telegram Premium custom emoji.\n'
            f'Use /help for instructions.'
        )
    
    bot.reply_to(message, response, parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is running...")
    print(f"Bot username: @{bot.get_me().username}")
    bot.infinity_polling()
