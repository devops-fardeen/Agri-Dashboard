from queue import Queue
import os


MAX_QUEUE_SIZE = 3

image_queue = Queue(maxsize=MAX_QUEUE_SIZE)


def add_image(item):

    # If queue is full, remove the oldest image.
    if image_queue.full():

        try:

            old_item = image_queue.get_nowait()

            old_path = old_item["path"]

            try:
                os.remove(old_path)
            except FileNotFoundError:
                pass

            image_queue.task_done()

        except Exception:
            pass

    try:

        image_queue.put_nowait(item)

        return True

    except Exception:

        return False