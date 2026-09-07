# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# MODEL PATHS
# -----------------------------

DISEASE_MODEL = os.path.join(BASE_DIR, "models", "disease.onnx")
PEST_MODEL = os.path.join(BASE_DIR, "models", "pest.onnx")
NUTRITION_MODEL = os.path.join(BASE_DIR, "models", "nutrition.onnx")
STAGE_MODEL = os.path.join(BASE_DIR, "models", "stage.onnx")


# -----------------------------
# DIRECTORIES
# -----------------------------

IMAGE_DIR = os.path.join(BASE_DIR, "received_images")
RESULT_DIR = os.path.join(BASE_DIR, "results")



# -----------------------------
# DETECTION SETTINGS
# -----------------------------

IMAGE_SIZE = 640

DISEASE_CONF = 0.40
PEST_CONF = 0.35
NUTRITION_CONF = 0.45
STAGE_CONF = 0.45


# NMS IoU threshold
IOU = 0.45


# -----------------------------
# QUEUE
# -----------------------------

MAX_QUEUE_SIZE = 3


# -----------------------------
# NUTRITION CLASSES
# -----------------------------

NUTRITION_ALLOWED = {
    "healthy",
    "magnesium deficiency",
    "nitrogen deficiency",
    "potassium deficiency"
}