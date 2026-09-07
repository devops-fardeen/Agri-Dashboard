import cv2
import requests
import time


# ============================================================
# CONFIGURATION
# ============================================================

# Your phone is the hotspot gateway
PHONE_IP = "10.202.46.77"

# Camera server port shown by your phone
PHONE_PORT = 8080

# Main MJPEG camera stream from phone IP Webcam app
PHONE_STREAM_URL = f"http://{PHONE_IP}:{PHONE_PORT}/video"
PHONE_SNAPSHOT_URL = f"http://{PHONE_IP}:{PHONE_PORT}/shot.jpg"

# Raspberry Pi Flask upload endpoint
PI_UPLOAD_URL = "http://127.0.0.1:5000/upload"

# Capture one image every 2 seconds
CAPTURE_INTERVAL = 2.0

# JPEG quality sent to Pi
JPEG_QUALITY = 85


# ============================================================
# SEND IMAGE TO AI SERVER
# ============================================================

def send_to_pi(frame):

    # Convert OpenCV frame to JPEG
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
    )

    if not success:
        print("ERROR: Could not encode image.")
        return

    image_bytes = encoded.tobytes()

    print(
        f"Sending image to AI pipeline "
        f"({len(image_bytes) / 1024:.1f} KB)..."
    )

    try:

        response = requests.post(
            PI_UPLOAD_URL,
            files={
                "image": (
                    "phone_camera.jpg",
                    image_bytes,
                    "image/jpeg"
                )
            },
            timeout=30
        )

        print(f"Pi HTTP status: {response.status_code}")
        print(f"Pi response: {response.text}")

    except requests.exceptions.RequestException as e:

        print("ERROR sending image to Pi:")
        print(e)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==========================================")
    print("     AGRI ASSISTANT PHONE CAMERA")
    print("==========================================")
    print()

    print("Phone camera:")
    print(PHONE_STREAM_URL)

    print()
    print("Pi AI server:")
    print(PI_UPLOAD_URL)

    print()
    print("Opening phone camera stream...")

    cap = cv2.VideoCapture(PHONE_STREAM_URL)

    # Give the connection some time
    time.sleep(2)

    if not cap.isOpened():

        print()
        print("==========================================")
        print("ERROR: CAMERA STREAM COULD NOT BE OPENED")
        print("==========================================")
        print()
        print("Check this URL from Chromium on the Pi:")
        print(PHONE_STREAM_URL)
        print()

        return

    print()
    print("PHONE CAMERA CONNECTED!")
    print("Starting AI image transmission...")
    print()

    last_capture = time.time()

    while True:

        ret, frame = cap.read()

        if not ret:

            print("WARNING: Failed to read camera frame.")

            time.sleep(1)

            continue

        current_time = time.time()

        # Capture every 2 seconds
        if current_time - last_capture >= CAPTURE_INTERVAL:

            last_capture = current_time

            print()
            print("------------------------------------------")
            print("Capturing image...")

            print(
                f"Frame resolution: "
                f"{frame.shape[1]}x{frame.shape[0]}"
            )

            send_to_pi(frame)

            print("------------------------------------------")

        time.sleep(0.01)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()