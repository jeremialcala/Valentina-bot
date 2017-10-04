import os
import sys
import json
from flask import Flask, request
from telegram.ext import Updater, CommandHandler
import socket


update_id = None

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    headers = {
        "Content-Type": "application/json"
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()

    # endpoint for processing incoming messaging events
    data = request.get_json()
    TOKEN = os.environ["VERIFY_TOKEN"]

    URL = os.environ["MY_URL"]

    updater = Updater(TOKEN)
    # add handlers
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=TOKEN)
    updater.bot.set_webhook(URL + TOKEN)
    updater.idle()
    log(URL)
    return json.dumps(data, sort_keys=False, indent=4, separators=(',', ': ')), 200, headers


def log(message):  # simple wrapper for logging to stdout on heroku
    print(message)
    sys.stdout.flush()


if __name__ == '__main__':

    app.run(debug=True)

