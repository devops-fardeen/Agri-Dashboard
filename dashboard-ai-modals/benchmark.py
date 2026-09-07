import time
import cv2
from ultralytics import YOLO


IMAGE = "received_images/test.jpg"
MODEL = "models/stage.onnx"


print("Loading model...")

model = YOLO(
    MODEL,
    task="detect"
)

print("Model loaded.")


image = cv2.imread(IMAGE)

if image is None:
    print("ERROR: image not found")
    exit()


print("\nWARM-UP")

for i in range(2):

    start = time.perf_counter()

    model.predict(
        image,
        imgsz=640,
        conf=0.40,
        iou=0.45,
        verbose=False
    )

    elapsed = time.perf_counter() - start

    print(
        f"Warmup {i+1}: "
        f"{elapsed:.3f} seconds"
    )


print("\nREAL TEST")

times = []


for i in range(10):

    start = time.perf_counter()

    model.predict(
        image,
        imgsz=640,
        conf=0.40,
        iou=0.45,
        verbose=False
    )

    elapsed = time.perf_counter() - start

    times.append(elapsed)

    print(
        f"Test {i+1}: "
        f"{elapsed:.3f} seconds"
    )


average = sum(times) / len(times)

print()
print("==========================")
print(
    f"Average: {average:.3f} seconds"
)
print(
    f"FPS: {1 / average:.2f}"
)
print("==========================")