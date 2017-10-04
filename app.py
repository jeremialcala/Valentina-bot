import os
import sys
import json
from flask import Flask, request
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)


update_id = None
app = Flask(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Age', 'Favourite colour'],
                  ['Number of siblings', 'Something else...'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup)

    return CHOOSING


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text('Your %s? Yes, I would love to hear about that!' % text.lower())

    return TYPING_REPLY


def custom_choice(bot, update):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "%s"
                              "You can tell me more, or change your opinion on something."
                              % facts_to_str(user_data),
                              reply_markup=markup)

    return CHOOSING


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "%s"
                              "Until next time!" % facts_to_str(user_data))

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    log('Update "%s" caused error "%s"' % (update, error))


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/347715594:AAFxTVbmmV1pLhXAmnXLd72XWnxyYxqwlvE', methods=['POST'])
def new_msg():
    headers = {
        "Content-Type": "application/json"
    }

    TOKEN = "347715594:AAFxTVbmmV1pLhXAmnXLd72XWnxyYxqwlvE"
    updater = Updater(TOKEN)

    # endpoint for processing incoming messaging events
    data = request.get_json()
    dp = updater.dispatcher
    log(data)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [RegexHandler('^(Age|Favourite colour|Number of siblings)$',
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Something else...$',
                                    custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },
        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    return "OK", 200, headers


@app.route('/set-webhook', methods=['POST'])
def webhook():
    headers = {
        "Content-Type": "application/json"
    }
    # endpoint for processing incoming messaging events
    data = request.get_json()
    # TOKEN = os.environ["VERIFY_TOKEN"]
    TOKEN = "347715594:AAFxTVbmmV1pLhXAmnXLd72XWnxyYxqwlvE"
    # URL = os.environ["MY_URL"]
    URL = "https://valentina-bot-demo.herokuapp.com/"
    updater = Updater(TOKEN)

    # add handlers
    try:
        updater.start_webhook(listen="0.0.0.0",
                              port=80,
                              url_path=TOKEN)
        updater.bot.set_webhook(URL + TOKEN)
        updater.idle()
    except PermissionError:
        log("Permission denied")
    log(request.environ.get('REMOTE_PORT'))
    log(URL + TOKEN)
    return json.dumps(data, sort_keys=False, indent=4, separators=(',', ': ')), 200, headers


def log(message):  # simple wrapper for logging to stdout on heroku
    print(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(port=5050, debug=False)
