from functools import wraps

import cfg
from db import User, init_db
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters, Job,
                          MessageHandler, Updater)


def check_auth(func):
    @wraps(func)
    def wrapped(self, update, context, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user = update.message.from_user
        except (NameError, AttributeError):
            print('No hay user_id en el mensaje.')
            return ConversationHandler.END
        user, created = User.get_or_create(
            id=user.id,
            last_name=user.last_name,
            first_name=user.first_name,
        )
        if created:
            print("Usuario {} creado".format(user.id))
        context.user_data['user'] = user
        return func(self, update, context, *args, **kwargs)
    return wrapped


class CarreritasBot(object):

    def __init__(self, bot_key, db_path):

        init_db(db_path)

        self._updater = Updater(bot_key, use_context=True)
        self._dp = self._updater.dispatcher

        self._dp.add_handler(CommandHandler(
            "start",
            self._start,
            pass_user_data=True))
        self._dp.add_handler(MessageHandler(
            Filters.text,
            self._start,
            pass_user_data=True))
        self._dp.add_error_handler(self._error)

    @check_auth
    def _start(self, update, context):
        msg = 'Bienvenido {0}... \n\n'.format(
            context.user_data['user'].first_name)
        msg += 'Que querés hacer?\nA) Nueva Partida\nB) Unirse a una partida'
        markup = ReplyKeyboardMarkup([["A"], ["B"]], resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(msg, reply_markup=markup)

    def _error(self, update, context):
        print('Update "%s" caused error "%s"' % (update, context.error))

    def run(self):
        self._updater.start_polling()
        self._updater.idle()

if __name__ == "__main__":
    bot = CarreritasBot(cfg.BOT_TOKEN, cfg.DB_PATH)
    bot.run()
