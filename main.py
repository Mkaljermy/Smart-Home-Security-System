import cv2
import os
from datetime import datetime
from twilio.rest import Client
import streamlit as st
import threading

account_sid = 'AC0d2ddfdef4dcbf4596692af8b967b434'
auth_token = 'e07dd0f16bf62bcff2d830e6ab2170c5'
twilio_phone_number = '+17372656389'
destination_phone_number = '+962791916343'
client = Client(account_sid, auth_token)


cascade_path = "haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    raise FileNotFoundError(f"Error: The file {cascade_path} does not exist.")
face_cascade = cv2.CascadeClassifier(cascade_path)


video = cv2.VideoCapture(0)
fps = 5.0

video_folder = "detected_videos"
if not os.path.exists(video_folder):
    os.makedirs(video_folder)

out = None
sms_sent = False
video_index = 0
current_frame = None
is_processing = False

def process_video():
    global out, sms_sent, video_index, current_frame, is_processing
    is_processing = True
    while is_processing:
        check, frame = video.read()
        if frame is not None:
            current_frame = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)
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
                    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame.shape[1], frame.shape[0]))
                    video_index += 1

                for x, y, w, h in faces:
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                out.write(frame)
            else:
                if out is not None:
                    out.release()
                    out = None

def start_surveillance():
    global is_processing
    if not is_processing:
        threading.Thread(target=process_video).start()

def stop_surveillance():
    global is_processing
    is_processing = False


st.set_page_config(
    page_title="Home Security System",
    page_icon="🚨",
    layout="wide"
)

st.title("Home Security System")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Surveillance Controls")
    start_button = st.button("Start Surveillance", on_click=start_surveillance)
    stop_button = st.button("Stop Surveillance", on_click=stop_surveillance)

with col2:
    st.subheader("Live Video Feed")
    frame_placeholder = st.empty()

while True:
    frame = current_frame
    if frame is not None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
