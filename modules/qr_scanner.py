def qr_code_scanner(camera_index=0):
    """
    Open the webcam and scan a QR code.

    Args:
        camera_index: Webcam index passed to OpenCV.

    Returns:
        Decoded QR content as a string, or None when cancelled or unavailable.

    Side effects:
        Opens a webcam and a temporary OpenCV window, then releases both.
    """
    try:
        import cv2
    except ImportError:
        print("OpenCV is not installed; use manual product ID entry.")
        return None

    camera = cv2.VideoCapture(camera_index)

    if not camera.isOpened():
        print("Camera not detected.")
        return None

    detector = cv2.QRCodeDetector()
    qr_data_result = None

    print("QR Code Scanner Started.")
    print("Press Q to cancel scanning.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Unable to read camera frame.")
                break

            qr_data, points, _ = detector.detectAndDecode(frame)

            if qr_data:
                print("QR Code Scanned Successfully!")
                print("QR Content:", qr_data)

                qr_data_result = qr_data
                break

            try:
                cv2.imshow("QR Code Scanner", frame)
                key = cv2.waitKey(1) & 0xFF
            except cv2.error:
                print("Camera display is unavailable; scanning cancelled.")
                break

            if key == ord("q"):
                print("Scanning cancelled.")
                break

    except Exception as error:
        print("QR scanning error:", error)

    finally:
        camera.release()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass

    return qr_data_result


if __name__ == "__main__":
    result = qr_code_scanner()

    if result:
        print("Scanned Product ID:", result)
