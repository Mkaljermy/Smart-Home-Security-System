import cv2
import time
from datetime import datetime
import argparse
import os
from twilio.rest import Client

account_sid = 'AC0d2ddfdef4dcbf4596692af8b967b434'
auth_token = 'e07dd0f16bf62bcff2d830e6ab2170c5'
twilio_phone_number = '+17372656389'
destination_phone_number = '+962791916343'

client = Client(account_sid, auth_token)

cascade_path = "haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    print(f"Error: The file {cascade_path} does not exist.")
    exit()

face_casacde = cv2.CascadeClassifier(cascade_path)
if face_casacde.empty():
    print("Error loading cascade file. Check the path and filename.")
    exit()

video = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 5.0
frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = None
sms_sent = False
video_index = 0

video_folder = "detected_videos"
if not os.path.exists(video_folder):
    os.makedirs(video_folder)

while True:
    check, frame = video.read()
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_casacde.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)
        if len(faces) > 0:
            if not sms_sent:

                message = client.messages.create(
                    body="Alert: Face detected on camera!",
                    from_=twilio_phone_number,
                    to=destination_phone_number
                )
                print(f"SMS sent: {message.sid}")
                sms_sent = True

            if out is None:

                exact_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                output_file = os.path.join(video_folder, f'output_{exact_time}_{video_index}.mp4')
                out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))
                video_index += 1

            for x, y, w, h in faces:
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            out.write(frame)
        else:
            if out is not None:

                out.release()
                out = None

        cv2.imshow("home surv", frame)
        key = cv2.waitKey(1)

        if key == ord('e'):
            break

video.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()