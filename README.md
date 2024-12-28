---

### **Step 1: Install Python and Required Libraries**

Before you start coding, ensure you have **Python** installed on your machine.

1. **Install Python** (if you don’t have it yet):
   - Download from: [Python Official Website](https://www.python.org/downloads/).
   - Follow installation instructions for your operating system.

2. **Install the Required Libraries**:
   Open a terminal/command prompt and run:
   ```bash
   pip install python-telegram-bot web3
   ```

---

### **Step 2: Create a Telegram Bot**

1. Open Telegram and search for **BotFather**.
2. Start a conversation and send the command `/newbot`.
3. Follow the instructions and give your bot a name and a unique username.
4. Once the bot is created, you’ll receive a **Token** (it looks like a long string of characters). **Save this token** as you’ll need it for the code.

---

### **Step 3: Set Up Your Files**

1. **Create a Project Folder**:
   Create a folder on your computer where you will keep all your bot files. Let’s call it **etherdrops-bot**.

   Example:
   ```
   etherdrops-bot/
   ```

2. **Create the Main Python Script**:
   Inside the **etherdrops-bot** folder, create a file named `etherdrops_bot.py`.

3. **Create a `.env` File (Optional but Recommended)**:
   To keep your Telegram bot token and Infura/Alchemy API key secure, you can create a `.env` file inside the same directory and store the sensitive data there. (Make sure to install `python-dotenv` if using this approach).

   Example `.env` file:
   ```
   TELEGRAM_TOKEN=your_telegram_token_here
   INFURA_PROJECT_ID=your_infura_project_id_here
   ```

   You can install the dotenv library with:
   ```bash
   pip install python-dotenv
   ```

   **Note**: If you are not using the `.env` file, simply replace the token and provider URL in the code directly.

---

### **Step 4: Write the Bot Code**

1. Open `etherdrops_bot.py` in your preferred code editor (e.g., Visual Studio Code, Sublime Text, etc.).
2. Paste the following code into the file:

```python
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
```

---

### **Step 5: Run the Bot**

1. **Create `.env` File** (optional but recommended):
   - Create a file named `.env` in the **etherdrops-bot** folder and add the following (replace with your values):
   ```
   TELEGRAM_TOKEN=your_telegram_token_here
   INFURA_PROJECT_ID=your_infura_project_id_here
   ```

2. **Run the Bot**:
   In the terminal/command prompt, navigate to the folder where your bot script is located:
   ```bash
   cd path/to/etherdrops-bot
   ```

   Then, run the script:
   ```bash
   python etherdrops_bot.py
   ```

3. **Test Your Bot**:
   - Open Telegram and search for your bot.
   - Start interacting with the bot using commands like `/add`, `/balance`, `/remove`, etc.

---

### **Step 6: Enhancements and Customization**

- **Rate Limiting**: Add limits on how often users can request updates.
- **Gas Price Alerts**: Add a feature to notify users when gas prices reach a certain threshold.
- **Security**: Ensure that private keys and other sensitive data are stored securely.
- **Database**: If you plan to scale the bot, use a database (e.g., SQLite, PostgreSQL) to store user subscriptions.

---
