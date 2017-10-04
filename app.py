import os
import sys
import json
from flask import Flask, request


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
    # endpoint for processing incoming messaging events
    data = request.get_json()
    TOKEN = os.environ["VERIFY_TOKEN"]
    PORT = int(os.environ["PORT"])
    URL = os.environ["MY_URL"]

    log(URL)
    return json.dumps(data, sort_keys=False, indent=4, separators=(',', ': ')), 200, headers


def log(message):  # simple wrapper for logging to stdout on heroku
    print(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)

