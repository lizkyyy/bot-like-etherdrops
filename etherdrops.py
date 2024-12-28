import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from web3 import Web3
from threading import Thread
import time

# Load the Telegram token and Infura/Alchemy URL from the .env file
from dotenv import load_dotenv
load_dotenv()

# Fetch environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BLOCKCHAIN_PROVIDER = os.getenv("INFURA_PROJECT_ID")

# Web3 setup
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{BLOCKCHAIN_PROVIDER}"))
if not web3.is_connected():
    print("Error: Unable to connect to the blockchain.")
    exit()

# Dictionary to store user subscriptions
subscriptions = {}

# Command: Start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to EtherDrops Bot!\n\n"
        "Use /add <wallet_address> to monitor a wallet.\n"
        "Use /remove <wallet_address> to stop monitoring a wallet.\n"
        "Use /balance <wallet_address> to check a wallet's balance.\n"
    )

# Command: Add a wallet to monitor
def add_wallet(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if len(context.args) != 1:
        update.message.reply_text("Usage: /add <wallet_address>")
        return

    wallet_address = context.args[0]
    if not web3.is_address(wallet_address):
        update.message.reply_text("Invalid wallet address.")
        return

    if user_id not in subscriptions:
        subscriptions[user_id] = set()

    subscriptions[user_id].add(wallet_address)
    update.message.reply_text(f"Added {wallet_address} to your monitoring list.")

# Command: Remove a wallet from monitoring
def remove_wallet(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if len(context.args) != 1:
        update.message.reply_text("Usage: /remove <wallet_address>")
        return

    wallet_address = context.args[0]
    if user_id in subscriptions and wallet_address in subscriptions[user_id]:
        subscriptions[user_id].remove(wallet_address)
        update.message.reply_text(f"Removed {wallet_address} from your monitoring list.")
    else:
        update.message.reply_text(f"{wallet_address} is not in your monitoring list.")

# Command: Check wallet balance
def check_balance(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /balance <wallet_address>")
        return

    wallet_address = context.args[0]
    if not web3.is_address(wallet_address):
        update.message.reply_text("Invalid wallet address.")
        return

    balance = web3.eth.get_balance(wallet_address)
    balance_in_eth = web3.from_wei(balance, "ether")
    update.message.reply_text(f"Balance of {wallet_address}: {balance_in_eth} ETH")

# Background thread to monitor wallets
def monitor_wallets():
    while True:
        for user_id, wallets in subscriptions.items():
            for wallet in wallets:
                balance = web3.eth.get_balance(wallet)
                balance_in_eth = web3.from_wei(balance, "ether")
                # Notify the user (you can add more conditions or alerts here)
                updater.bot.send_message(
                    chat_id=user_id,
                    text=f"Wallet {wallet} has a balance of {balance_in_eth} ETH."
                )
        time.sleep(60)  # Adjust the monitoring interval as needed

# Main function to run the bot
def main():
    global updater
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add_wallet))
    dispatcher.add_handler(CommandHandler("remove", remove_wallet))
    dispatcher.add_handler(CommandHandler("balance", check_balance))

    # Start the monitoring thread
    Thread(target=monitor_wallets, daemon=True).start()

    # Start the bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
  
