from ultralytics import YOLO
import cv2
import time

from config import (
    DISEASE_MODEL,
    PEST_MODEL,
    NUTRITION_MODEL,
    STAGE_MODEL,

    IMAGE_SIZE,

    DISEASE_CONF,
    PEST_CONF,
    NUTRITION_CONF,
    STAGE_CONF,

    IOU,

    NUTRITION_ALLOWED
)


class ModelEngine:

    def __init__(self):

        print()
        print("Loading models...")
        print()

        self.disease = YOLO(
            DISEASE_MODEL,
            task="detect"
        )

        print("Disease model loaded.")

        self.pest = YOLO(
            PEST_MODEL,
            task="detect"
        )

        print("Pest model loaded.")

        self.nutrition = YOLO(
            NUTRITION_MODEL,
            task="detect"
        )

        print("Nutrition model loaded.")

        self.stage = YOLO(
            STAGE_MODEL,
            task="detect"
        )

        print("Stage model loaded.")

        print()
        print("ALL MODELS LOADED")
        print()


    def detect(
        self,
        model,
        image,
        confidence
    ):

        results = model.predict(
            source=image,
            imgsz=IMAGE_SIZE,
            conf=confidence,
            iou=IOU,
            verbose=False
        )

        result = results[0]

        detections = []

        if result.boxes is None:

            return detections


        names = result.names


        for box in result.boxes:

            class_id = int(
                box.cls[0].item()
            )

            conf = float(
                box.conf[0].item()
            )

            xyxy = box.xyxy[0].tolist()

            x1, y1, x2, y2 = map(
                int,
                xyxy
            )


            class_name = names[class_id]


            detections.append({

                "class_id": class_id,

                "name": class_name,

                "confidence": round(
                    conf,
                    3
                ),

                "bbox": [
                    x1,
                    y1,
                    x2,
                    y2
                ]

            })


        return detections


    def process(self, image):

        total_start = time.perf_counter()


        # -------------------------
        # DISEASE
        # -------------------------

        disease_start = time.perf_counter()

        disease = self.detect(
            self.disease,
            image,
            DISEASE_CONF
        )

        disease_time = (
            time.perf_counter()
            - disease_start
        )


        # -------------------------
        # PEST
        # -------------------------

        pest_start = time.perf_counter()

        pest = self.detect(
            self.pest,
            image,
            PEST_CONF
        )

        pest_time = (
            time.perf_counter()
            - pest_start
        )


        # -------------------------
        # NUTRITION
        # -------------------------

        nutrition_start = time.perf_counter()

        nutrition_all = self.detect(
            self.nutrition,
            image,
            NUTRITION_CONF
        )

        nutrition_time = (
            time.perf_counter()
            - nutrition_start
        )


        # Filter unwanted classes
        nutrition = []

        for detection in nutrition_all:

            name = detection["name"].strip().lower()

            if name in NUTRITION_ALLOWED:

                nutrition.append(
                    detection
                )


        # -------------------------
        # GROWTH STAGE
        # -------------------------

        stage_start = time.perf_counter()

        stage = self.detect(
            self.stage,
            image,
            STAGE_CONF
        )

        stage_time = (
            time.perf_counter()
            - stage_start
        )


        total_time = (
            time.perf_counter()
            - total_start
        )


        return {

            "disease": disease,

            "pest": pest,

            "nutrition": nutrition,

            "stage": stage,

            "timing": {

                "disease": round(
                    disease_time,
                    3
                ),

                "pest": round(
                    pest_time,
                    3
                ),

                "nutrition": round(
                    nutrition_time,
                    3
                ),

                "stage": round(
                    stage_time,
                    3
                ),

                "total": round(
                    total_time,
                    3
                )

            }

        }