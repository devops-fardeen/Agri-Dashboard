import cv2
import os
import json
import time

from image_queue import image_queue
from image_quality import check_image
from model_engine import ModelEngine

from config import RESULT_DIR


def draw_detections(
    image,
    detections,
    prefix
):

    for detection in detections:

        x1, y1, x2, y2 = detection["bbox"]

        name = detection["name"]

        confidence = detection["confidence"]


        label = (
            f"{prefix}: "
            f"{name} "
            f"{confidence:.2f}"
        )


        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )


        cv2.putText(
            image,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )


def draw_results(
    image,
    results
):

    draw_detections(
        image,
        results["disease"],
        "Disease"
    )


    draw_detections(
        image,
        results["pest"],
        "Pest"
    )


    draw_detections(
        image,
        results["nutrition"],
        "Nutrition"
    )


    draw_detections(
        image,
        results["stage"],
        "Stage"
    )


    return image


def process_item(
    item,
    engine
):

    image_path = item["path"]

    image = cv2.imread(
        image_path
    )


    if image is None:

        return {
            "success": False,
            "error": "Could not read image"
        }


    good, reason, blur = check_image(
        image
    )


    if not good:

        return {

            "success": False,

            "error": reason,

            "blur_score": round(
                blur,
                2
            )

        }


    # AI
    results = engine.process(
        image
    )


    # Draw boxes
    annotated = draw_results(
        image.copy(),
        results
    )


    # Save annotated image
    output_path = os.path.join(
        RESULT_DIR,
        "latest.jpg"
    )


    cv2.imwrite(
        output_path,
        annotated
    )


    response = {

        "success": True,

        "image": os.path.basename(
            image_path
        ),

        "blur_score": round(
            blur,
            2
        ),

        "results": results

    }


    # Save JSON
    with open(
        os.path.join(
            RESULT_DIR,
            "latest.json"
        ),
        "w"
    ) as file:

        json.dump(
            response,
            file,
            indent=4
        )


    return response


def worker():

    os.makedirs(
        RESULT_DIR,
        exist_ok=True
    )


    engine = ModelEngine()


    while True:

        item = image_queue.get()


        try:

            print()
            print(
                "Processing:",
                item["path"]
            )


            result = process_item(
                item,
                engine
            )


            # Give result back to HTTP request
            item["result"] = result


            if item.get("event"):

                item["event"].set()


            print(
                "Finished."
            )


        except Exception as error:

            print(
                "Worker error:",
                error
            )


            item["result"] = {

                "success": False,

                "error": str(error)

            }


            if item.get("event"):

                item["event"].set()


        finally:

            try:

                os.remove(
                    item["path"]
                )

            except Exception:

                pass


            image_queue.task_done()