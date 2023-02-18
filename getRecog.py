import face_recognition
import cv2
import numpy as np

video_capture = cv2.VideoCapture(0)

# ดึงข้อมูลรูป
known_face_encodings = [
    face_recognition.face_encodings(face_recognition.load_image_file("imgs/source/6319c10022.jpg"))[0]
]

known_face_names = [
    "Detected"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

