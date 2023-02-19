import face_recognition
import cv2
import numpy as np
import requests
from datetime import date, datetime
import datetime

video_capture = cv2.VideoCapture(0)
getStatus = False

def showNoclass():
    img = cv2.imread('imgs/source/noclass.png')
    cv2.imshow('image', img)

def checkDateTime():
    response = requests.get("http://localhost:30000/api/checks/date")
    if response.status_code == 200:
        res = response.json()
        today = date.today()
        if str(today) == str(res['date']):
            time_rp = datetime.datetime.now().time().strftime('%H:%M:%S')
            time_db_start = res['time_start']
            time_db_end = res['time_end']
            if time_rp < time_db_start or time_rp > time_db_end:
                """ video_capture.release()
                cv2.destroyAllWindows()
                showNoclass() """
                main()
            else:
                print('NO')
                

def recognation(res):
    known_face_names = []
    known_face_encodings = []

    for item in res:
        image = face_recognition.load_image_file("imgs/source/"+item['path'])
        encoding = face_recognition.face_encodings(image)
        known_face_encodings.extend(encoding)
        known_face_names.append(item['Users']['code'])
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            ret, frame = video_capture.read()
            if process_this_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                face_locations = face_recognition.face_locations(
                    rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame, face_locations)

                face_names = []
                face_percent = []
                percent = 0

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    face_percent_value = 1-face_distances[best_match_index]

                    if face_percent_value >= 0.60:
                        name = known_face_names[best_match_index]
                        percent = round(face_percent_value*100, 2)
                        face_percent.append(percent)
                    else:
                        name = "UNKNOWN"
                        face_percent.append(0)
                    face_names.append(name)
            process_this_frame = not process_this_frame
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                if name == "UNKNOWN":
                    color = [192, 192, 192]
                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), color, 2)
                    cv2.rectangle(frame, (left-1, top),
                                  (right+1, top), color, cv2.FILLED)
                    cv2.rectangle(frame, (left-1, bottom),
                                  (right+1, bottom+30), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left+6, bottom+23),
                                font, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(percent), (left+6, bottom+50),
                                font, 0.6, (255, 255, 255), 1)
                else:
                    color = [255, 102, 51]
                    cv2.rectangle(frame, (left, top),
                                  (right, bottom), color, 2)
                    cv2.rectangle(frame, (left-1, top),
                                  (right+1, top), color, cv2.FILLED)
                    cv2.rectangle(frame, (left-1, bottom),
                                  (right+1, bottom+30), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left+6, bottom+23),
                                font, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(percent), (left+6, bottom+50),
                                font, 0.6, (255, 255, 255), 1)
            cv2.imshow('Video', frame)
            checkDateTime()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        cv2.destroyAllWindows()

def main():
    getStatus = False
    while True:
        if getStatus == False:
            today = date.today()
            response = requests.get("http://localhost:30000/api/checks/date")
            if response.status_code == 200:
                res = response.json()
                if str(today) == str(res['date']):
                    major_id = res['major_id']
                    time_rp = datetime.datetime.now().time().strftime('%H:%M:%S')
                    time_db_start = res['time_start']
                    time_db_end = res['time_end']
                    if time_rp >= time_db_start and time_rp <= time_db_end:
                        response = requests.get(
                            "http://localhost:30000/api/checks/imgs/"+str(major_id))
                        if response.status_code == 200:
                            getStatus = True
                            res = response.json()
                            recognation(res)
                        else:
                            getStatus = False
                    else:
                        getStatus = False
                else:
                    getStatus = False

main()
