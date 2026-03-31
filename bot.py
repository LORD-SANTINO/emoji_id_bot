import telebot
import logging
import re

BOT_TOKEN = '8307990040:AAGt9Xfh0gli2Tbb1CA42c_E-mAlLWjkOM4'
bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(level=logging.WARNING)

WELCOME_IMAGE_URL = "https://tmpfiles.org/dl/26326290/download7.jpg"

# --- Helper functions ---

def get_bot_username():
    """Return bot's username (cached)."""
    return bot.get_me().username

def is_bot_mentioned(message):
    """Check if the message contains a mention of the bot."""
    bot_username = get_bot_username()
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                mention = message.text[entity.offset:entity.offset + entity.length]
                if mention == f"@{bot_username}":
                    return entity  # Return the entity object for later skipping
    return None

def find_command_entity(message):
    """Return the bot_command entity if present, else None."""
    if message.entities:
        for entity in message.entities:
            if entity.type == 'bot_command':
                # Check if it's our command (optional)
                command = message.text[entity.offset:entity.offset + entity.length]
                if command.startswith('/emoji_id'):
                    return entity
    return None

def extract_custom_emojis(message, skip_offsets=None):
    """
    Extract all custom emoji entities from the message.
    Returns a list of dicts: [{'id': str, 'text': str}, ...]
    If skip_offsets is provided (list of (offset, length) tuples), entities
    that overlap with any of those ranges are ignored.
    """
    emojis = []
    if not message.entities:
        return emojis

    # Build a set of offsets to skip (we'll check each entity)
    skip_ranges = skip_offsets or []

    for entity in message.entities:
        if entity.type != 'custom_emoji':
            continue

        # Check if this entity should be skipped (e.g., part of a command)
        skip = False
        for start, length in skip_ranges:
            # If entity is entirely inside a skip range, ignore it
            if start <= entity.offset < start + length:
                skip = True
                break
        if skip:
            continue

        # Extract the emoji text (the actual character)
        emoji_text = message.text[entity.offset:entity.offset + entity.length]
        emojis.append({
            'id': entity.custom_emoji_id,
            'text': emoji_text
        })

    return emojis

def should_process_message(message):
    """Decide if the bot should respond to this message."""
    chat_type = message.chat.type
    if chat_type == 'private':
        return True
    if chat_type in ('group', 'supergroup'):
        # Mention or command triggers processing
        if is_bot_mentioned(message) or find_command_entity(message):
            return True
    return False

def format_response(emojis):
    """Format the reply message with the list of emojis and their IDs."""
    if not emojis:
        return (
            '<tg-emoji emoji-id="6179128006615765757">❌</tg-emoji> '
            '<b>No custom emoji found.</b>\n\n'
            'Please send a message that includes a Telegram Premium custom emoji.\n'
            'Use /help for instructions.'
        )

    if len(emojis) == 1:
        # Single emoji – simple response
        emoji = emojis[0]
        return (
            f'<tg-emoji emoji-id="6257784371227399216">✅</tg-emoji> '
            f'<b>Custom Emoji Detected!</b>\n\n'
            f'<tg-emoji emoji-id="{emoji["id"]}">🔹</tg-emoji> '
            f'<b>ID:</b> <code>{emoji["id"]}</code>\n\n'
            f'<tg-emoji emoji-id="5798831858263265607">💡</tg-emoji> '
            f'You can use this ID in bots that support custom emoji.'
        )
    else:
        # Multiple emojis – list them
        lines = []
        for i, emoji in enumerate(emojis, 1):
            lines.append(
                f'{i}. <tg-emoji emoji-id="{emoji["id"]}">🔹</tg-emoji> '
                f'ID: <code>{emoji["id"]}</code>'
            )
        list_text = '\n'.join(lines)
        return (
            '<tg-emoji emoji-id="6257784371227399216">✅</tg-emoji> '
            f'<b>Custom Emojis Detected!</b> ({len(emojis)} total)\n\n'
            f'{list_text}\n\n'
            '<tg-emoji emoji-id="5798831858263265607">💡</tg-emoji> '
            'You can use these IDs in bots that support custom emoji.'
        )

# --- Command handlers ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
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
        bot.send_photo(message.chat.id, photo=WELCOME_IMAGE_URL, caption=welcome_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send photo: {e}")
        bot.send_message(message.chat.id, welcome_text, parse_mode="HTML")

@bot.message_handler(commands=['emoji_id'])
def emoji_id_command(message):
    """Handle /emoji_id command: skip the command part and extract emojis."""
    # Find the command entity to skip it
    command_entity = find_command_entity(message)
    skip_ranges = []
    if command_entity:
        skip_ranges.append((command_entity.offset, command_entity.length))

    emojis = extract_custom_emojis(message, skip_offsets=skip_ranges)
    response = format_response(emojis)
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages: private or group mentions."""
    if not should_process_message(message):
        return

    # Determine if the message contains a mention that should be skipped
    skip_ranges = []
    mention_entity = is_bot_mentioned(message)
    if mention_entity:
        skip_ranges.append((mention_entity.offset, mention_entity.length))

    emojis = extract_custom_emojis(message, skip_offsets=skip_ranges)
    response = format_response(emojis)
    bot.reply_to(message, response, parse_mode="HTML")

if __name__ == "__main__":
    print("Bot is running...")
    print(f"Bot username: @{bot.get_me().username}")
    bot.infinity_polling()
