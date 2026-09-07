import cv2


def blur_score(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()


def check_image(image):

    if image is None:

        return False, "invalid image", 0


    height, width = image.shape[:2]


    if width < 320 or height < 240:

        return False, "resolution too low", 0


    score = blur_score(image)


    # Temporary value.
    # We will tune this after testing your camera.
    if score < 25:

        return False, "too blurry", score


    brightness = image.mean()


    if brightness < 20:

        return False, "too dark", score


    if brightness > 245:

        return False, "too bright", score


    return True, "OK", score