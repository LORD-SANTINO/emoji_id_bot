import telebot

# Replace 'YOUR_BOT_TOKEN' with the token from @BotFather
bot = telebot.TeleBot('8307990040:AAGt9Xfh0gli2Tbb1CA42c_E-mAlLWjkOM4')


@bot.message_handler(func=lambda message: True)
def get_emoji_id(message):
    if message.entities:
        for entity in message.entities:
            if entity.type == 'custom_emoji':
                emoji_id = entity.custom_emoji_id
                # Using HTML mode here so we don't have to escape "!" or "."
                response = f"<b>✅ Custom Emoji ID found!</b>\n\nID: <code>{emoji_id}</code>"
                bot.reply_to(message, response, parse_mode="HTML")
                return

    bot.reply_to(message, "❌ No custom emoji detected. Please send a premium emoji.")

print("Bot is running...")
bot.infinity_polling()
