import cv2
import face_recognition
import pickle
import os

from py_files.FirebaseManager import FirebaseManager

bucket, app = FirebaseManager().__enter__()

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)

imgList = []
studentIds = []


def send_images():
    for path in pathList:
        imgList.append(cv2.imread(os.path.join(folderPath, path)))
        studentIds.append(os.path.splitext(path)[0])  # extracti ng the ids by splitting up the paths


def findEncodings(imagesList):

    send_images()  # preparing image list & studentsIDS
    encodeList = []
    for img in imagesList:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except:
            pass
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


def get_store_encodings():
    encodeListKnown = findEncodings(imgList)
    encodeListKnownWithIds = [encodeListKnown, studentIds]

    file = open("py_files/EncodeFile.p", 'wb')
    pickle.dump(encodeListKnownWithIds, file)  # saving the encoding as well the ids the pickle file
    file.close()
