import cv2
import face_recognition
import pickle
import os

from py_files.FirebaseManager import FirebaseManager

bucket, app = FirebaseManager().__enter__()

# Importing student images
folderPath = 'Images'

imgList = []
studentIds = []


def send_images():
    # car ce fichier est importé dans le lancement de l"appli du coup le path list contient les ancienns images qui se change juste après l'import de ces ancniennes images

    pathList = os.listdir(folderPath)

    imgList.clear()
    studentIds.clear()
    for path in pathList:

        if os.path.exists(f"{folderPath}/{path}"):
            imgList.append(cv2.imread(f"{folderPath}/{path}"))  # use Images/id.png instead of join function

            studentIds.append(os.path.splitext(path)[0])  # extracti ng the ids by splitting up the paths


def findEncodings(imagesList):
    send_images()  # preparing image list & studentsIDS
    encodeList = []
    is_encoded = False
    for img in imagesList:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
            is_encoded = True
        except:

            is_encoded = False

    return is_encoded, encodeList


def get_store_encodings():
    is_encoded, encodeListKnown = findEncodings(imgList)
    if is_encoded:
        encodeListKnownWithIds = [encodeListKnown, studentIds]
        # Remove student from local data

        # s'il y un problème d"encodage d'une image
        if len(encodeListKnown) == len(studentIds):  # s'il y a pas une incohérence entre l'encodage et le nombre de ids

            if os.path.exists("py_files/EncodeFile.p"):
                # supprimer l'étudiant en question
                os.remove("py_files/EncodeFile.p")

            file = open("py_files/EncodeFile.p", 'wb')
            pickle.dump(encodeListKnownWithIds, file)  # saving the encoding as well the ids the pickle file
            file.close()

            return True
        else:
            return False
    else:
        return False
