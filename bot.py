import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from recipe_data import RECIPES

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    welcome_text = (
        "🍳 Welcome to the Recipe Bot!\n\n"
        "Just send me the name of any dish, for example:\n"
        "• Tomato Scrambled Eggs\n"
        "• Braised Pork Belly\n"
        "• Egg Fried Rice\n\n"
        "I'll reply with the ingredients and step-by-step instructions."
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when /help is issued."""
    help_text = (
        "📖 How to use:\n\n"
        "Just type the name of a dish, like \"Pancakes\" or \"Chicken Biryani\".\n"
        "If it's in the database, I'll reply with the ingredients and steps.\n\n"
        "Type /start to see the welcome message again."
    )
    await update.message.reply_text(help_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user's dish name input."""
    user_text = update.message.text.strip()
    logger.info("User query: %s", user_text)

    # Look up in the local recipe database (case-insensitive)
    key = user_text.lower()
    recipe = RECIPES.get(key)

    if recipe:
        ingredients_text = "\n".join(f"• {item}" for item in recipe["ingredients"])
        steps_text = "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(recipe["steps"])
        )

        reply = (
            f"🍽️ *{user_text.title()}*\n\n"
            f"📝 *Ingredients:*\n{ingredients_text}\n\n"
            f"👨‍🍳 *Steps:*\n{steps_text}"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            f"Sorry, I couldn't find a recipe for \"{user_text}\".\n\n"
            "Try one of these instead: Tomato Scrambled Eggs, Braised Pork Belly, "
            "Egg Fried Rice, Pancakes, Chicken Biryani, Cola Chicken Wings, "
            "Pepper Steak Stir Fry, Spaghetti Bolognese.\n\n"
            "(You can add more recipes by editing recipe_data.py.)"
        )


def main() -> None:
    """Start the bot."""
    # Read token from environment variable (set on Railway)
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable.")

    # Create the Application (long polling mode)
    application = Application.builder().token(token).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    logger.info("Bot is running and listening for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
