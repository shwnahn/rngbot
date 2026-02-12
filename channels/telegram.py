import os
import asyncio
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from memory.storage import save_telegram_message, get_telegram_history
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    def __init__(self, process_message_callback):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.process_message_callback = process_message_callback
        self.application = None
        self.running = False

    async def initialize(self):
        """Initialize the Telegram Application."""
        print(f"[Telegram] Initialize called. Token exists: {bool(self.token)}")
        if not self.token:
            print("[Telegram] Warning: TELEGRAM_BOT_TOKEN not found.")
            return

        print("[Telegram] Building application...")
        self.application = ApplicationBuilder().token(self.token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("[Telegram] Application.initialize()...")
        await self.application.initialize()
        print("[Telegram] Bot initialized.")

    async def start_polling(self):
        """Start polling for updates (non-blocking in theory)."""
        if not self.application:
            print("[Telegram] Application not initialized, skipping polling.")
            return

        print("[Telegram] Starting polling via updater...")
        self.running = True
        
        print("[Telegram] Application.start()...")
        await self.application.start()
        
        # We use updater.start_polling() 
        # Note: drop_pending_updates=True might be safer for testing
        await self.application.updater.start_polling()
        print("[Telegram] Polling started.")

    async def stop(self):
        """Stop the bot."""
        if self.application:
            print("[Telegram] Stopping bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self.running = False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I am RingleBot. How can I help you today?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"[Telegram] Received message: {update.message.text} from {update.effective_user.id}")
        user_id = update.effective_user.id
        text = update.message.text
        
        # Save user message
        save_telegram_message(user_id, "user", text)
        
        # Define callback to send chunks back
        async def reply_callback(chunk):
            print(f"[Telegram] Sending reply chunk: {chunk[:20]}...")
            await update.message.reply_text(chunk)
            # Save bot response
            save_telegram_message(user_id, "assistant", chunk)

        # Retrieve history
        history = get_telegram_history(user_id, limit=20)
        
        # Pass to main pipeline
        # Note: We don't need 'conn' (iMessage DB) here, so we pass None
        # We assume process_message_callback handles the logic
        await self.process_message_callback(text, "Telegram", None, reply_callback, history=history)
