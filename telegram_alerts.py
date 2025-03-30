import telebot

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_alert(wallet, amount, to):
    message = f"🚨 Insider Trade Alert!\nWallet: {wallet}\nAmount: {amount} SOL\nSent To: {to}"
    bot.send_message(CHAT_ID, message)

# Example Alert:
# send_alert("0x123456", "500 SOL", "0x789abc")
