import openai
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters


class RecommendationHandler:
    DESCRIPTION = 'description'
    CATEGORY = 'category'
    UKR_DESC_BUTTON = 'За описом'
    UKR_CAT_BUTTON = 'За категорією'
    REC_TYPES = [UKR_CAT_BUTTON, UKR_DESC_BUTTON]

    def __init__(self, command: str, text: str, app: Application):
        self.method = None
        self.command = command
        self.text = text
        self.main_state = self.command
        self.desc_state = self.main_state + self.DESCRIPTION
        self.cat_state = self.main_state + self.CATEGORY

        self.handlers_setup(app)

    async def _choose_rec_type(self, update: Update, context: CallbackContext, text: str):
        keyboard_buttons = [[KeyboardButton(rec_type)] for rec_type in self.REC_TYPES]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=True)
        )

    async def recommend(self, update: Update, context: CallbackContext):
        msg_to_send = f"Ви обрали тип '{self.text}'!\n" \
                      f"Оберіть як ви хочете отримати рекомендації." \
                      f"\nЯкщо хочете відмінити дію, то використайте команду /cancel."
        await self._choose_rec_type(update, context, msg_to_send)
        return self.main_state

    async def get_recommendations_info(self, update: Update, context: CallbackContext):
        if update.message.text == self.UKR_DESC_BUTTON:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Для типу '{self.text}' введіть ваш опис. "
                     f"\nЯкщо хочете відмінити дію, то використайте команду /cancel.",
                reply_markup=ReplyKeyboardRemove()
            )
            return self.desc_state
        elif update.message.text == self.UKR_CAT_BUTTON:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Для типу '{self.text}' введіть вашу категорію."
                     f"\nНаприклад: комедія; жахи; фантастика з елемементами драми"
                     f"\nЯкщо хочете відмінити дію, то використайте команду /cancel.",
                reply_markup=ReplyKeyboardRemove()
            )
            return self.cat_state
        else:
            msg_to_send = f"Ви ввели не дійсну опцію '{update.message.text}', " \
                          f"оберіть те що дається вам на вибір у кнопкочках :)"
            await self._choose_rec_type(update, context, text=msg_to_send)
            return self.main_state

    async def _get_recommendation(self, update: Update, context: CallbackContext, info_type: str):
        user_msg = update.message.text
        recommendations = await self.get_recommendations(
            f"Порекомендуй пронумерованим списком назви існуючих {self.text} за {info_type}: {user_msg}.")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=recommendations)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Введіть команду /help, щоб отримати список команд.")
        return ConversationHandler.END

    async def get_recommendation_by_description(self, update: Update, context: CallbackContext):
        return await self._get_recommendation(update, context, 'описом')

    async def get_recommendation_by_category(self, update: Update, context: CallbackContext):
        return await self._get_recommendation(update, context, 'категорією')

    @staticmethod
    async def get_recommendations(prompt: str) -> str:
        # Use OpenAI's GPT-3 model to generate a recommendation
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.5
        )
        # Extract the generated recommendation from the response
        recommendation = response["choices"][0]["text"].strip()
        return recommendation

    @staticmethod
    async def cancel(update: Update, context: CallbackContext):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Останню команду відмінено",
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Введіть команду /help, щоб отримати список команд.")
        return ConversationHandler.END

    @staticmethod
    async def unknown(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Вибачте, я не розумію цієї команди. Будь ласка, спробуйте щось інше. "
                                            "Попередні дії відмінені. Введіть команду /help, щоб отримати список команд.",
                                       reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def handlers_setup(self, app: Application):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(self.command, self.recommend)],
            states={self.main_state: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.get_recommendations_info)],
                    self.desc_state: [
                        MessageHandler(filters.TEXT & (~filters.COMMAND), self.get_recommendation_by_description)],
                    self.cat_state: [
                        MessageHandler(filters.TEXT & (~filters.COMMAND), self.get_recommendation_by_category)]
                    },
            fallbacks=[CommandHandler('cancel', self.cancel), MessageHandler(filters.COMMAND, self.unknown)]
        )

        app.add_handler(conv_handler)
