from flask import (
    Flask,
    request,
    jsonify
)

import os
import uuid
import threading

from image_queue import add_image
from config import IMAGE_DIR

app = Flask(__name__)

UPLOAD_DIR = IMAGE_DIR

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status": "online",

        "service": "Farm Assistant AI"

    })


@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    if "image" not in request.files:

        return jsonify({

            "success": False,

            "error": "image field missing"

        }), 400


    uploaded = request.files["image"]


    filename = (
        uuid.uuid4().hex
        + ".jpg"
    )


    path = os.path.join(
        UPLOAD_DIR,
        filename
    )


    uploaded.save(path)


    event = threading.Event()


    item = {

        "path": path,

        "event": event,

        "result": None

    }


    accepted = add_image(
        item
    )


    if not accepted:

        try:
            os.remove(path)
        except:
            pass


        return jsonify({

            "success": False,

            "error": "queue full"

        }), 429


    # Wait for AI worker
    finished = event.wait(
        timeout=20
    )


    if not finished:

        return jsonify({

            "success": False,

            "error": "AI processing timeout"

        }), 504


    return jsonify(
        item["result"]
    )


if __name__ == "__main__":

    print()
    print(
        "Farm Assistant server starting..."
    )
    print(
        "Listening on port 5000"
    )
    print()


    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )