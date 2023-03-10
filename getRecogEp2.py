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
                video_capture.release()
                cv2.destroyAllWindows()
                showNoclass()
                main()
            
def recognation(res):
    known_face_names = []
    known_face_encodings = []

    for item in res:
        image = face_recognition.load_image_file("imgs/source/"+item['path'])
        encoding = face_recognition.face_encodings(image)
        known_face_encodings.extend(encoding)
        known_face_names.append(item['Users']['code'])

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        while True:
            print('loop 2')
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if process_this_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(
                    rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame, face_locations)

                face_names = []
                face_percent = []
                percent = 0

                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    face_percent_value = 1-face_distances[best_match_index]

                    if face_percent_value >= 0.60:
                        name = known_face_names[best_match_index]
                        percent = round(face_percent_value*100, 2)
                        face_percent.append(percent)
                        #print('Scanning!')
                    else:
                        name = "UNKNOWN"
                        face_percent.append(0)
                    face_names.append(name)

            process_this_frame = not process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
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
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    cv2.rectangle(frame, (left-1, top),
                                (right+1, top), color, cv2.FILLED)
                    cv2.rectangle(frame, (left-1, bottom),
                                (right+1, bottom+30), color, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left+6, bottom+23),
                                font, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, str(percent), (left+6, bottom+50),
                                font, 0.6, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)
            checkDateTime() 
            
            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
    











    

def main():
    getStatus = False

    while True:
        print('loop 1')

        if getStatus == False:
            
            today = date.today()

            response = requests.get("http://localhost:30000/api/checks/date")
            if response.status_code == 200:
                res = response.json()

                # ???????????????????????????????????????
                if str(today) == str(res['date']):

                    # ?????????????????????????????? major_id ??????????????????????????????
                    major_id = res['major_id']

                    # ????????????????????? time
                    time_rp = datetime.datetime.now().time().strftime('%H:%M:%S')
                    time_db_start = res['time_start']
                    time_db_end = res['time_end']

                    # ?????????????????????????????????????????????????????????
                    if time_rp >= time_db_start and time_rp <= time_db_end:
                        #print('?????????????????????????????????')
                        response = requests.get(
                            "http://localhost:30000/api/checks/imgs/"+str(major_id))
                        if response.status_code == 200:
                            print(response.status_code)
                            getStatus = True
                            res = response.json()
                            recognation(res)
                        else:
                            print(response.status_code)
                            getStatus = False
                            #print(response.json())
                    else:
                        getStatus = False
                        #print('No time!')
                else:
                    getStatus = False
                    #print('No date!')

            else:
                """ print(response.status_code)
                print(response.json()) """


main()
