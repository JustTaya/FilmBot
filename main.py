import logging
import os

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackContext
import openai

from handlers.RecommendationHandler import RecommendationHandler

# Get your Telegram bot token from environment variable or other secure means
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Get your OpenAI API key from environment variable or other secure means
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Set up OpenAI API credentials
openai.api_key = OPENAI_API_KEY  # Replace with your OpenAI API key



async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Цей бот було створено, щоб надати рекомендації для фільмів та серіалів за "
                                        "введеними категоріями або описом."
                                        "\n\nЗагальні команди:"
                                        "\n/start - початкова команда"
                                        "\n/help - для виводу підказки"
                                        "\n\nКоманди для отримання рекомендацій:"
                                        "\n/series - отримати рекомендації лише для серіалів"
                                        "\n/films - отримати рекомендації лише для фільмів"
                                        "\n/general - отримати рекомендації і для фільмів і для серіалів")


async def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Вибачте, я не розумію цієї команди. Будь ласка, спробуйте щось інше.")


def main() -> None:
    # Create an instance of the Telegram Updater
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )
    # Register the command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', start))
    RecommendationHandler('films', 'фільми', app)
    RecommendationHandler('series', 'серіали', app)
    RecommendationHandler('general', 'фільми та серіали', app)

    # Register the unknown command handler
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start the bot
    logging.info("Bot start.")
    app.run_polling()


if __name__ == '__main__':
    main()
