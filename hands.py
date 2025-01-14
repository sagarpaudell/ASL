import cv2
import time
import mediapipe as mp
import sys
import modellib as M
from PIL import Image

# Open the default camera or a video stream
cap = cv2.VideoCapture(0)

# Initialize the MediaPipe Hands model
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Initialize variables
ptime = 0
prediction = ""
conf = 0
counter = 0

while True:
    # Capture frame-by-frame
    success, img = cap.read()

    # Flip the image horizontally for a mirror effect
    img = cv2.flip(img, 1)

    # Process the image with MediaPipe Hands
    results = hands.process(img)

    # Get the image dimensions
    h, w, c = img.shape 

    # Reset counter if no hands are detected
    if not results.multi_hand_landmarks:
        counter = 0
        prediction = ""

    # Otherwise, detect and crop each hand
    for handLms in results.multi_hand_landmarks:
        x_max = 0
        y_max = 0
        x_min = w
        y_min = h
        for lm in handLms.landmark:
            # Get the coordinates of each landmark
            x, y = int(lm.x * w), int(lm.y * h)

            # Find the maximum and minimum coordinates to crop the image
            if x > x_max:
                x_max = x + 100
            if x < x_min:
                x_min = x - 100
            if y > y_max:
                y_max = y + 100
            if y < y_min:
                y_min = y - 100

        # Adjust the crop size to make it square
        xdiff = x_max - x_min
        ydiff = y_max - y_min
        diff = abs(xdiff-ydiff)
        if xdiff > ydiff:
            y_max += int(diff/2)
            y_min -= int(diff/2)
        else:
            x_max += int(diff/2)
            x_min -= int(diff/2)

        # Crop the image to the hand region
        hand_img = img[y_min:y_max, x_min: x_max]

        # Perform gesture recognition every 60 frames
        if counter%60 == 0:
            try:
                # Preprocess the image for the model
                hand_img = cv2.resize(hand_img, (200,200), interpolation = cv2.INTER_AREA)
                hand_img = cv2.cvtColor(hand_img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(hand_img)

                # Get the prediction from the model
                conf, prediction = M.get_prediction(pil_img)

            except Exception as e:
                print(str(e))

        # Draw a rectangle around the hand region
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        # Display the gesture prediction and confidence level
        cv2.putText(img, f"{prediction}  {conf*100:.2f}%", (x_min, y_max+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)

        # Increment the counter
        counter += 1

    # Calculate the frames per second
    ctime = time.time()
    fps = 1/(ctime-ptime)

    ptime = ctime
    cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    cv2.imshow("Image", img)

    # If 'q' is pressed, the program will break the loop and exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all windows
cap.release()
cv2.destroyAllWindows()