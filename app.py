import os
import sys
import json
from flask import Flask, request
import telegram
from telegram.ext import Updater, CommandHandler
from telegram.error import NetworkError, Unauthorized
from time import sleep
import socket

update_id = None

app = Flask(__name__)


def echo(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            update.message.reply_text(update.message.text)


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
    bot = telegram.Bot(TOKEN)

    # endpoint for processing incoming messaging events
    data = request.get_json()

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    log(data)

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1
    # return json.dumps(data, sort_keys=False, indent=4, separators=(',', ': ')), 200, headers


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
