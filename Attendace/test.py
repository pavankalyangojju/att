from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

# Load the face recognition model and labels
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Error: Could not open camera.")
    exit()

facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

try:
    with open('data/names.pkl', 'rb') as w:
        LABELS = pickle.load(w)
    with open('data/faces_data.pkl', 'rb') as f:
        FACES = pickle.load(f)
except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
    print("Error loading face data:", e)
    exit()

# Ensure FACES is a NumPy array and reshape to 2D
FACES = np.array(FACES).reshape(FACES.shape[0], -1)
print('Shape of Faces matrix --> ', FACES.shape)

# Train KNN model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

COL_NAMES = ['NAME', 'TIME']

if not os.path.exists("Attendance"):
    os.makedirs("Attendance")

while True:
    ret, frame = video.read()
    
    if not ret:
        print("Error: Frame not captured.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        if w == 0 or h == 0:
            continue  # Skip invalid detections
        
        crop_img = frame[y:y+h, x:x+w]
        
        if crop_img.size == 0:
            print("Error: Cropped image is empty.")
            continue  # Skip this iteration
        
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        
        try:
            output = knn.predict(resized_img)
            print("Recognized:", output[0])
        except Exception as e:
            print("Prediction Error:", e)
            continue

        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        attendance_file = f"Attendance/Attendance_{date}.csv"
        exist = os.path.isfile(attendance_file)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        attendance = [str(output[0]), str(timestamp)]
    
    cv2.imshow("Frame", frame)

    k = cv2.waitKey(1) & 0xFF
    if k == ord('o'):
        speak("Attendance Taken.")
        time.sleep(1)  # Reduce sleep time
        
        with open(attendance_file, "a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not exist:
                writer.writerow(COL_NAMES)
            writer.writerow(attendance)

    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
