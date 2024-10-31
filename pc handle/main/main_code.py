import cv2
import cv2.aruco as aruco
import serial
import time
import threading
import numpy as np
import requests
import mimetypes

backend_url = "http://localhost:5000"

bluetooth_port = 'COM7'
baud_rate = 9600  # Baud rate for HC-05/06 module

marker_id = 0
receive_ack = False

box_dict = {}


def send_product_data(image_path, encoder_value, marker_ID, backend_url):
    mime_type, _ = mimetypes.guess_type(image_path)
    files = {
        "image": (image_path, open(image_path, "rb"), mime_type)  # filename, file object, and MIME type
    }
    # Define the data payload
    product_data = {
        "position": encoder_value,
        "marker_ID": marker_ID,
        "status": "not_scanned"
    }

    # Send the POST request
    try:
        response = requests.post(f"{backend_url}/api/products/", data=product_data, files=files)
        response.raise_for_status()  # Check for HTTP request errors

        # Print success message and server response
        print("Image and data successfully sent.")
        print("Server response:", response.json())

    except requests.exceptions.RequestException as e:
        print("Failed to send product data:", e)


def contains_number(string):
    return True if set(string).intersection('0123456789') else False


def sharpen_image(image):
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)


def aruco_detect():
    # Initialize the camera
    global marker_id, receive_ack, marker_id

    cap = cv2.VideoCapture(1)  #("http://192.168.205.167:4747/video")

    # Load the dictionary that was used to generate the Aruco markers
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
    parameters = aruco.DetectorParameters()

    parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX
    parameters.minMarkerPerimeterRate = 0.02

    while True:
        ret, frame = cap.read()  # Capture frame-by-frame

        if not ret:
            print("Failed to grab frame")
            break

        frame = sharpen_image(frame)

        # Get the dimensions of the camera frame
        frame_height, frame_width, _ = frame.shape

        # Convert to grayscale (necessary for Aruco detection)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect markers in the frame
        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None:
            # Draw the detected markers
            aruco.drawDetectedMarkers(frame, corners, ids)

            # Get the center of the first detected Aruco marker
            for i, corner in enumerate(corners):
                marker_id = ids[i][0]  # Get the ArUco marker ID

                if marker_id in box_dict:
                    print(f"Marker ID {marker_id} is Skipping... \t {box_dict}")
                    continue

                # corner[0] gives 4 points: top-left, top-right, bottom-right, bottom-left
                # Calculate the middle point of the Aruco marker
                x_sum = corner[0][:, 0].sum()
                y_sum = corner[0][:, 1].sum()
                marker_center_x = int(x_sum / 4)
                marker_center_y = int(y_sum / 4)

                # Draw a vertical line through the Aruco marker center (A)
                cv2.line(frame, (marker_center_x, 0), (marker_center_x, frame_height), (0, 255, 0), 2)

                # Draw a circle at the marker center for visualization
                cv2.circle(frame, (marker_center_x, marker_center_y), 5, (0, 255, 0), -1)

                # Get the center of the camera frame (B)
                frame_center_x = int(frame_width / 2)
                frame_center_y = int(frame_height / 2)

                # Draw a vertical line through the camera frame center (B)
                cv2.line(frame, (frame_center_x, 0), (frame_center_x, frame_height), (255, 0, 0), 2)

                # Draw a circle at the camera frame center for visualization
                cv2.circle(frame, (frame_center_x, frame_center_y), 5, (255, 0, 0), -1)

                # Calculate the horizontal distance between the two vertical lines (A and B)
                horizontal_distance = (marker_center_x - frame_center_x)

                if abs(horizontal_distance) < 50 and marker_id not in box_dict:
                    send_msg("BOX")
                    print("===========Box Founded==============")

                    # Print the horizontal distance
                print(f"distance: {horizontal_distance} \t {box_dict}")

        # Display the resulting frame
        cv2.imshow('Aruco Detection', frame)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def send_msg(msg):
    global receive_ack
    try:
        while msg:
            if receive_ack:
                print("stop sending")
                receive_ack = False
                break

            message = f"{msg}\n"
            ser.write(message.encode())  # Send the distance
            print(f"Sent: {message.strip()}")

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("Disconnected")
        ser.close()


def recv_msg(ser):
    global receive_ack, marker_id

    try:
        while True:
            response = ser.readline().decode().strip()
            if response:
                print(f"\nReceived: {response}")
                if "A" in response or "C" in response or "K" in response:
                    receive_ack = True
                    print("ACK received")
                elif contains_number(response):
                    receive_ack = False
                    print("number received")
                    if marker_id not in box_dict:
                        encoder_value = int(response)
                        box_dict[marker_id] = encoder_value
                        print(f"Saved marker {marker_id} with encoder value {encoder_value}")
                        filename = f"{marker_id}_{encoder_value}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"Image saved as {filename}")
                else:
                    receive_ack = False
                    print("different message")
            time.sleep(0.3)

    except Exception as e:
        print(f"Error: {e}")


try:
    ser = serial.Serial(bluetooth_port, baud_rate, timeout=10, write_timeout=10)
    print(f"Connected to {bluetooth_port}")
except Exception as e:
    print(f"Failed to connect: {e}")
    exit()

# Create and start the send and receive threads
aruco_check_thread = threading.Thread(target=aruco_detect)
receive_thread = threading.Thread(target=recv_msg, args=(ser,))

aruco_check_thread.start()
receive_thread.start()

# Wait for both threads to finish
aruco_check_thread.join()
receive_thread.join()

# Close the serial port
ser.close()
print("Communication stopped and port closed.")