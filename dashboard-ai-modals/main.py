import threading
import os

from server import app
from worker import worker


def main():

    os.makedirs(
        "received_images",
        exist_ok=True
    )

    os.makedirs(
        "results",
        exist_ok=True
    )


    # Start AI worker
    worker_thread = threading.Thread(
        target=worker,
        daemon=True
    )

    worker_thread.start()


    # Start HTTP server
    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )


if __name__ == "__main__":

    main()