import streamlit as st

st.set_page_config(
    page_title="Attendace Marking & Mask Detection app",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="Resources/attendance.png",

)
import os
import pickle
import sys
from time import sleep, time
import cv2
import face_recognition
import cvzone

from firebase_admin import db

import numpy as np
from datetime import datetime

from py_files.FunctionsUtilis import FunctionsUtilis
import py_files.AddDatatoDatabase as data_db

from py_files.FirebaseManager import FirebaseManager
from keras.models import load_model

########################################################################


face_model = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
# Load the trained model
model = load_model('models/masknet.h5')
mask_label = {0: 'MASK', 1: 'NO MASK'}
modeType = 0
counter = 0  # this is used in order to download the infos just once in the first iteration, otherwise it will be inefficient !
id = -1
imgStudent = []



########################################################################


def space(length):
    for i in range(length):
        st.write("\n")
title_placeholder = st.empty()
# Add some vertical space using markdown with empty lines
title_placeholder.title("*Welcome* to the :orange[***Attendace***] Marking & :orange[***Mask***] Detection app.")
space(4)

form_placeholder2 = st.empty()
form_placeholder = st.empty()
final_result_placeholder = st.empty()
capture_placeholder = st.empty()
messages_placeholder = st.empty()
button_placeholder = st.empty()



# Instantiation of the FunctionsUtilis class
functions = FunctionsUtilis(messages_placeholder)
path_js = functions.get_location_path()

imgBackground = cv2.imread('Resources/background.png')
# Graphics
# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)  # Get the names of the images in the Modes folder
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
file = open('py_files/EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
######################################################################################

bucket, app = FirebaseManager().__enter__()

# Initialization (singleton)
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = None
if 'starting_time' not in st.session_state:
    st.session_state['starting_time'] = None
if 'location_data' not in st.session_state:  # insertion de email et user name dans la session
    st.session_state['location_data'] = None
if 'is_authorized' not in st.session_state:  # insertion de email et user name dans la session
    st.session_state['is_authorized'] = None
if 'is_admin' not in st.session_state:  # insertion de email et user name dans la session
    st.session_state['is_admin'] = None

if st.session_state["is_logged_in"] is None:  # si l'utilisateur n'est pas logged in
    is_logged_in = functions.login_form(app)  # il doit faire le login
    st.session_state["is_logged_in"] = is_logged_in  # update de l'état de login
    st.session_state['starting_time'] = time()

######################################################################################
# Lancer le fichier JS pour obtenir la localisation de l'utilisateur
if st.session_state["is_logged_in"]:
    if st.session_state['location_data'] is None and not st.session_state['is_admin']:
        with st.spinner('Obtention des cordonnées de localisation ...'):
            functions.get_location_navigator()
            sleep(3)  # un freeze afin de donner le temps au code js pour télécharger le fichier json de location
            functions.get_location()

if st.session_state['is_admin']:  # s'il est admin, on l'autorise directement sans verifier sa position actuelle
    autoriser = True

else:
    if st.session_state['is_authorized']:  # si le use est dèjà verifié pas la peine de refaire la vérification
        autoriser = True

    else:

        if st.session_state['location_data'] is not None:
            with st.spinner('Verification d\'autorisation de présence ...'):

                autoriser = functions.autoriser_presence(app)

        else:

            autoriser = False


def clear_forms():
    form_placeholder.empty()
    form_placeholder2.empty()


# Define functions for each page (adding data, parameters, dashboard, attendance system)
def add_data_page():
    form_placeholder.empty()
    data_db.add_data_to_db(form_placeholder2)


def dashboard_page():
    clear_forms()

    data_db.dashboard()


def attendance_system_page():
    pass


if st.session_state["is_logged_in"] and autoriser:
    start_button_pressed = False

    data_config = functions.read_data(form_placeholder)

    #################################################################
    # Create a sidebar menu with radio buttons for page selection
    connection_page = f"Connexion :  :large_green_circle:  :green[***{st.session_state['username']} (connecté)***] "
    selected_page = st.sidebar.radio("Menu", (connection_page,
                                              "Add Data", "Dashboard", "Attendance & mask detection System"))

    # Display the selected page content based on user choice
    if selected_page == "Add Data":

        if st.session_state["is_admin"]:
            add_data_page()
        else:
            form_placeholder.empty()
            st.header(":no_entry: Accès  interdit !!")
            st.error(" Vous n'êtes pas un admin, pour accéder à la page d'ajout des données .  ")


    elif selected_page == "Dashboard":
        if st.session_state["is_admin"]:
            dashboard_page()
        else:
            clear_forms()
            st.header(" :no_entry: Accès  interdit !!")
            st.error(" Vous n'êtes pas un admin, pour accéder à cette page de tableau de bord .  ")

    elif selected_page == "Attendance & mask detection System":
        attendance_system_page()
    elif selected_page == connection_page:
        clear_forms()
        functions.connexion(app)

        ##################################################################

    if data_config is not None:  # Pour la première fois data_confsig retourne None qu'on ne pas  bien sur le packager sur les trois param
        max_time_mask, max_time_remark, standing_tresh, recipient_email = data_config

        start_button_pressed = True

        clear_forms()
    else:

        sys.exit(0)  # ça permet de faire une sorte de reinitialisation de streamlit

    if standing_tresh > 0:
        standing_tresh = standing_tresh - 1
    else:
        standing_tresh = 0
    capture_placeholder.caption(f"""                          
    
                            :red[***Note :***] :orange[***- D'une part, vous avez :red[***{int(max_time_remark / 3600)}h({round((max_time_remark / 60), 2)}min)({max_time_remark}sec)***] pour refaire une nouvelle tentative de présence. 
                                                          - D'autre part, la vérification de port de masque s'effectue chaque :red[***{int(max_time_mask / 3600)}h({round((max_time_mask / 60), 2)}min)({max_time_mask}sec)***] .
                                                          - De plus, en ce qui concerne le niveau de présence (standing),  il est qualifié de :red[***bon (G pour Good)***], s’il dépasse :red[***{standing_tresh} fois de présence***], sinon il est :red[***mauvais (B pour Bad)***]  .
                                                            Et bonne journée !!***]
             """)

    if start_button_pressed:

        stop_button_pressed = button_placeholder.button(":no_entry: Stop", help="Arrêter le système de présence et de détection de masque puis la webcam ")

        capture = None

        while True:

            if capture is None and start_button_pressed:  # instance unique de cap
                with st.spinner('Intializing the webcam ...'):
                    # Initialisation de la variable 'cap' pour la capture vidéo.
                    cap = cv2.VideoCapture(0)

                    capture = True
                    functions.show_message(is_success=True, text="The webcam was succesfully initialized !! ")

                    functions.show_message(is_success=True,
                                           text="The firebase_admin app was succesfully initialized !! ")

            success, img = cap.read()

            imgS = cv2.resize(img, (0, 0), None, 0.25,
                              0.25)  # image small , that's very important, otherwise it will not work propely
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS,
                                                             faceCurFrame)  # finding the encodings just for the face not the whole image, so that we're passing the face locations

            imgBackground[162:162 + 480,
            55:55 + 640] = img  # 162:162 + 480, 55:55 + 640 are the positions in the BG where we've to put the webcam and the image modes
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]  # l'emplacement des 4 modes

            if faceCurFrame:  # If a face is detected in the webcam
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):  # the equivilant of nested loop
                    matches = face_recognition.compare_faces(encodeListKnown,
                                                             encodeFace)  # bool result for comparing the current face from the webcam with the number of the encoding of faces stored in the system
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)  # getting the index of the lower distance wich matchs the curr face

                    if matches[matchIndex]:  # ensure the matching

                        imgBackground = functions.draw_fancy_rect(faceLoc, imgBackground)
                        id = studentIds[matchIndex]
                        if st.session_state[
                            "is_admin"]:  # s'il est admin, ça peut vérifier la présence de tous les étudiants
                            if counter == 0:  # download just for once

                                # using an opencv rectangle as well but the one in cvzone is a little bit fancier
                                cvzone.putTextRect(imgBackground, "Marking...", (275,
                                                                                 400))  # using this loading mechanism it's showing like progression, while downloading the data from the databases, and to avoid the lag
                                imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
                                final_result_placeholder.image(imgBackground, channels="RGB")

                                # cv2.waitKey(1)  # adding a dellay of 1 ms
                                counter = 1
                                modeType = 1  # show info's modetype
                        else:
                            if id == st.session_state[
                                'user_id']:  # on peut aussi tester eventuellement sur s'il est admin ou pas
                                if counter == 0:  # download just for once

                                    # using an opencv rectangle as well but the one in cvzone is a little bit fancier
                                    cvzone.putTextRect(imgBackground, "Marking...", (275,
                                                                                     400))  # using this loading mechanism it's showing like progression, while downloading the data from the databases, and to avoid the lag
                                    imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
                                    final_result_placeholder.image(imgBackground, channels="RGB")

                                    # cv2.waitKey(1)  # adding a dellay of 1 ms
                                    counter = 1
                                    modeType = 1  # show info's modetype

                            else:  # if the face is unrecognized

                                imgBackground = functions.draw_fancy_rect(faceLoc, imgBackground)
                                cvzone.putTextRect(imgBackground, "Unknown", (275,
                                                                              400))  # using this loading mechanism it's showing like progression, while downloading the data from the databases, and to avoid the lag
                                imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
                                final_result_placeholder.image(imgBackground, channels="RGB")


                    #####################################################################################################################

                    else:  # if the face is unrecognized

                        imgBackground = functions.draw_fancy_rect(faceLoc, imgBackground)
                        cvzone.putTextRect(imgBackground, "Unknown", (275,
                                                                      400))  # using this loading mechanism it's showing like progression, while downloading the data from the databases, and to avoid the lag
                        imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
                        final_result_placeholder.image(imgBackground, channels="RGB")

                        # cv2.waitKey(1)  # adding a dellay of 1 ms
                if counter != 0:  # it keep increasing

                    if counter == 1:  #
                        # Get the Data just for the first iteration (counter=1)
                        studentInfo = db.reference(f'Students/{id}',
                                                   app=app).get()  # getting all the student data for the  given id

                        # Get the student Image from the storage for a given id
                        blob = bucket.get_blob(
                            f'Images/{id}.png')  # the blob format from the bucket storage for a given id

                        # the numpy encoding the array of a given student
                        array = np.frombuffer(blob.download_as_string(), np.uint8)  # using the unsigned interger 8bit
                        imgStudent = cv2.imdecode(array,
                                                  cv2.COLOR_BGRA2BGR)  # decoding the numpy array encoding to get the student image
                        # # Update data of attendance

                        secondsElapsed = functions.compute_elapsed_time(studentInfo['last_attendance_time'])

                        functions.show_message(
                            f"The remaining time for the next attendance marking for {studentInfo['name']} :  {abs(int(max_time_remark / 3600) - int(secondsElapsed / 3600))}h = {abs(int(max_time_remark / 60) - int(secondsElapsed / 60))}m = {abs(int(max_time_remark) - int(secondsElapsed))}s",
                            is_error=True)

                        if st.session_state["is_admin"]:
                            status, last_date = functions.markAttendance(id, studentInfo['name'],
                                                                         studentInfo['starting_year'],
                                                                         studentInfo['year'],
                                                                         studentInfo['standing'], studentInfo['major'],
                                                                         studentInfo['total_attendance'],
                                                                         studentInfo['last_attendance_time'],
                                                                         studentInfo['total_mask_detected'],
                                                                         studentInfo['last_mask_time'],
                                                                         messages_placeholder)

                        if secondsElapsed > max_time_remark:  # after each 86400 sec (or 24h / 1J) then  we can remark the attendance, we can actually replace with a day for example but in seconds
                            ref = db.reference(f'Students/{id}', app=app)
                            studentInfo['total_attendance'] += 1

                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                            functions.update_standing(studentInfo['total_attendance'], ref, standing_tresh)

                            if st.session_state["is_admin"]:
                                #   Saving student's info in an xlsx file
                                status, last_date = functions.markAttendance(id, studentInfo['name'],
                                                                             studentInfo['starting_year'],
                                                                             studentInfo['year'],
                                                                             studentInfo['standing'],
                                                                             studentInfo['major'],
                                                                             studentInfo['total_attendance'],
                                                                             datetime.now().strftime(
                                                                                 "%Y-%m-%d %H:%M:%S"),
                                                                             studentInfo["total_mask_detected"],
                                                                             studentInfo['last_mask_time'],
                                                                             messages_placeholder)




                        else:  # otherwise we will get the 3rd modetype already marked
                            modeType = 3  # making modetype as already marked
                            counter = 0  # after a while we're making it as active
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if modeType != 3:  # if mode differs to the last one which's already marked

                        if 10 < counter < 20:
                            modeType = 2  # making modetype as marked after showing up the student's info for the 10 first iterations

                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                        if counter <= 10:
                            imgBackground = functions.adding_info(imgBackground,
                                                                  studentInfo['total_attendance'],
                                                                  studentInfo['major'],
                                                                  id,
                                                                  studentInfo['total_mask_detected'],
                                                                  studentInfo['year'],
                                                                  studentInfo['standing'],
                                                                  studentInfo['name'],
                                                                  studentInfo['starting_year'],

                                                                  )

                            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                        counter += 1

                        if counter >= 20:  # if the counter is
                            counter = 0
                            modeType = 0
                            studentInfo = []
                            imgStudent = []
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            else:  # If there's nothing in the webcam
                modeType = 0  # then we should show the active modetype
                counter = 0

            imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)  # Attendance marking showing  up !!
            final_result_placeholder.image(imgBackground, channels="RGB")

            if modeType == 1:  # on doit attendre 5sec dans les mode marked, ou le mode d'affichage d'infos

                sleep(3)

            if modeType == 2:  # on doit attendre 5sec dans les mode marked, ou le mode d'affichage d'infos

                sleep(1)

            #################################################################################################################
            # Mask detection & Detect faces in the frame

            if id != -1:  # checking if a student is detected or not

                if st.session_state["is_admin"]:  # s'il est admin, ça peut vérifier la présence de tous les étudiants
                    ref = db.reference(f'Students/{id}', app=app)

                    studentInfo = db.reference(f'Students/{id}', app=app).get()
                    # setting up the timer, and getting the time from the last attendance
                    mask_seconds_elapsed = functions.compute_elapsed_time(studentInfo['last_mask_time'])

                    functions.show_message(is_error=True,
                                           text=f"The remaining time for the next mask detecting for {studentInfo['name']} :  {abs(int(max_time_mask / 3600) - int(mask_seconds_elapsed / 3600))}h = {abs(int(max_time_mask / 60) - int(mask_seconds_elapsed / 60))}min = {abs(int(max_time_mask) - int(mask_seconds_elapsed))}s")
                    if mask_seconds_elapsed > max_time_mask:

                        face_model = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
                        faces = face_model.detectMultiScale(img, scaleFactor=1.1, minNeighbors=4)

                        # the elapsed time should be here
                        for (x, y, w, h) in faces:
                            # Preprocess the face image for your model
                            face_img = img[y:y + h, x:x + w]
                            face_img = cv2.resize(face_img, (128, 128))
                            face_img = np.reshape(face_img, [1, 128, 128, 3]) / 255.0

                            # Make a prediction
                            mask_result = model.predict(face_img)

                            # Choose color: Green for 'MASK', Red for 'NO MASK'
                            color = (0, 255, 0) if mask_label[mask_result.argmax()] == 'MASK' else (0, 0, 255)

                            cvzone.putTextRect(img, mask_label[mask_result.argmax()], (275,
                                                                                       400))

                            cv2.rectangle(img, (x, y), (x + w, y + h), color, 5)

                            # Display the resulting frame
                            imgBackground[162:162 + 480, 55:55 + 640] = img

                            if mask_label[mask_result.argmax()] == 'MASK':

                                studentInfo['total_mask_detected'] += 1
                                ref.child('total_mask_detected').set(studentInfo['total_mask_detected'])
                                ref.child('last_mask_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                                modeType = 4  # making modetype as mask checked
                                counter = 0  # after a while we're making it as active
                                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                                functions.show_message(is_success=True,
                                                       text=f"The total_mask_detected was increased !!  ")

                            else:
                                if studentInfo['total_mask_detected'] > 0:
                                    studentInfo['total_mask_detected'] -= 1
                                    ref.child('total_mask_detected').set(studentInfo['total_mask_detected'])
                                    ref.child('last_mask_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                                    modeType = 5  # making modetype as no mask was detected
                                    counter = 0  # after a while we're making it as active
                                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                                    body = \
                                        f"""
                    Bonjour Mr , j'espère que vous allez bien ,
            Voici ci-dessous le rapport sur le port de masque des étdiants, l'étudiant {studentInfo['name']} 
            qui a un total de masque détectés ègale à {studentInfo['total_mask_detected']},et qui fait partie 
            de la filière {studentInfo['major']}, a été détecté avec aucun masque le  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
            
            et merci ,
                 cordialement
            """

                                    functions.send_email(body=body, subject="Detection de non port de  masque",
                                                         user_id=st.session_state['user_id'], app=app,
                                                         recipient_email=recipient_email)
                                    functions.show_message(is_error=True,
                                                           text=f"The total_mask_detected was decreased !!  ")

                else:
                    if id == st.session_state['user_id']:
                        ref = db.reference(f'Students/{id}', app=app)

                        studentInfo = db.reference(f'Students/{id}', app=app).get()
                        # setting up the timer, and getting the time from the last attendance
                        mask_seconds_elapsed = functions.compute_elapsed_time(studentInfo['last_mask_time'])

                        functions.show_message(is_error=True,
                                               text=f"The remaining time for the next mask detecting for {studentInfo['name']} :  {abs(int(max_time_mask / 3600) - int(mask_seconds_elapsed / 3600))}h = {abs(int(max_time_mask / 60) - int(mask_seconds_elapsed / 60))}min = {abs(int(max_time_mask) - int(mask_seconds_elapsed))}s")
                        if mask_seconds_elapsed > max_time_mask:

                            face_model = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
                            faces = face_model.detectMultiScale(img, scaleFactor=1.1, minNeighbors=4)

                            # the elapsed time should be here
                            for (x, y, w, h) in faces:
                                # Preprocess the face image for your model
                                face_img = img[y:y + h, x:x + w]
                                face_img = cv2.resize(face_img, (128, 128))
                                face_img = np.reshape(face_img, [1, 128, 128, 3]) / 255.0

                                # Make a prediction
                                mask_result = model.predict(face_img)

                                # Choose color: Green for 'MASK', Red for 'NO MASK'
                                color = (0, 255, 0) if mask_label[mask_result.argmax()] == 'MASK' else (0, 0, 255)

                                cvzone.putTextRect(img, mask_label[mask_result.argmax()], (275,
                                                                                           400))

                                cv2.rectangle(img, (x, y), (x + w, y + h), color, 5)

                                # Display the resulting frame
                                imgBackground[162:162 + 480, 55:55 + 640] = img

                                if mask_label[mask_result.argmax()] == 'MASK':

                                    studentInfo['total_mask_detected'] += 1
                                    ref.child('total_mask_detected').set(studentInfo['total_mask_detected'])
                                    ref.child('last_mask_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                                    modeType = 4  # making modetype as mask checked
                                    counter = 0  # after a while we're making it as active
                                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                                    functions.show_message(is_success=True,
                                                           text=f"The total_mask_detected was increased !!  ")

                                else:
                                    if studentInfo['total_mask_detected'] > 0:
                                        studentInfo['total_mask_detected'] -= 1
                                        ref.child('total_mask_detected').set(studentInfo['total_mask_detected'])
                                        ref.child('last_mask_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                                        modeType = 5  # making modetype as no mask was detected
                                        counter = 0  # after a while we're making it as active
                                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                                        body = \
                                            f"""
                                            Bonjour Mr , j'espère que vous allez bien ,
                                    Voici ci-dessous le rapport sur le port de masque des étdiants, l'étudiant {studentInfo['name']} 
                                    qui a un total de masque détectés ègale à {studentInfo['total_mask_detected']},et qui fait partie 
                                    de la filière {studentInfo['major']}, a été détecté avec aucun masque le  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.

                                    et merci ,
                                         cordialement
                                    """

                                        functions.send_email(body=body, subject="Detection de non port de  masque", user_id=st.session_state['user_id'], app=app,
                                                         recipient_email=recipient_email)
                                        functions.show_message(is_error=True,
                                                               text=f"The total_mask_detected was decreased !!  ")

            imgBackground = cv2.cvtColor(imgBackground, cv2.COLOR_BGR2RGB)
            final_result_placeholder.image(imgBackground, channels="BGR")  # mask detection BGR

            if modeType == 4 or modeType == 5:  # on doit attendre 2sec dans les mode marked, ou le mode d'affichage d'infos

                sleep(2)

            if stop_button_pressed:
                cap.release()
                break

functions.space(2)
st.caption(f"""                          Powered by OpenCV, Streamlit . \n
                CREATED BY :  :orange[***SAYAD HAMZA &  OTHMAN TRIGUI***]\n
                4TH YEAR IDIA\n
                2023/2024


 """, )
