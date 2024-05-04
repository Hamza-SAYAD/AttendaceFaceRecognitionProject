import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

import streamlit as st
import os

from time import sleep, time
import cv2

import cvzone

from datetime import datetime

import random, string

from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

from geopy.distance import distance

from firebase_admin import auth
import json


class FunctionsUtilis:

    def __init__(self, messages_placeholder=st.empty()):
        self.messages_placeholder = messages_placeholder
        self.geolocator = Nominatim(user_agent="attendance_mask_app")


    # def send_email(self):
    #     import streamlit as st
    #     import requests  # Assuming you're using requests for the API call
    #
    #     # # Streamlit form to collect email address (with consent checkbox)
    #     # email = st.text_input("Enter your email address:")
    #     # consent_checkbox = st.checkbox("I consent to receiving notifications")
    #     #
    #     # send_button = st.button("Send Notification")
    #     # SG.PctTex3-5N68f7UtvK1cBg .Eo2Mtarx1C0oHy3bYGI0AqJFzLB-gop0oD3417kb6so
    #     # if send_button and consent_checkbox: ngeVfQFYQlKU0ufo8x5d1A
    #     # Replace with your SendGrid API endpoint and details PctTex3-5N68f7UtvK1cBg
    #     url = "https://api.sendgrid.com/v3/mail/send"
    #     headers = {
    #         "Authorization": "ngeVfQFYQlKU0ufo8x5d1A",
    #         "Content-Type": "application/json"
    #     }
    #     data = {
    #         "personalizations": [
    #             {
    #                 "to": [{"email": "hamzasayad1736@gmail.com"}]
    #             }
    #         ],
    #         "from": {"email": "hamzasayad16@gmail.com"},
    #         "subject": "Your Streamlit Notification",
    #         "content": [
    #             {
    #                 "type": "text/plain",
    #                 "value": "Your notification content here (e.g., list of people without masks)"
    #             }
    #         ]
    #     }
    #
    #     response = requests.post(url, headers=headers, json=data)
    #
    #     if response.status_code == 202:
    #         st.success("Notification sent successfully!")
    #     else:
    #         st.error(f"Error sending notification: {response.text}")



    def send_email(self, subject, body, recipient_email = "kooolmnjksiiolm@gmail.com" ):
        # Replace with your SMTP server details
        smtp_server = "smtp.gmail.com"
        port = 465  # Use 465 for SSL 587 hsdhsdensas hamzasayad16@gmail.com rgvj cgwh rqoy iyix
        sender_email = "luvthakur262001@gmail.com"
        sender_password = "blwq zpnq mbda zwac"

        # Create a secure connection with the SMTP server
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, sender_password)

            # Create a MIMEMultipart message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject

            # Attach the email body as plain text
            message.attach(MIMEText(body, "plain"))

            try:
                # Send the email
                server.sendmail(sender_email, recipient_email, message.as_string())
                self.show_message(is_success=True,
                                  text='Email sent successfully!',
                                  delai=3)

            except Exception as e:
                self.show_message(is_error=True,
                                  text=f"Error sending email: {e}",
                                  delai=3)





    def login(self, app, email, password):

        try:

            user_by_email = auth.get_user_by_email(email, app=app)


            if user_by_email.uid == password:

                if email == "admin@gmail.com" or email == "hamza@gmail.com" : # these're admin's gmails
                    auth.update_user(user_by_email.uid, custom_claims={'admin': True, 'tolerance': 1500}, app=app)

                if 'email' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['email'] = None
                if st.session_state["email"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["email"] = user_by_email.email

                if 'username' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['username'] = None
                if st.session_state["username"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["username"] = user_by_email.display_name

                if 'user_id' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['user_id'] = None
                if st.session_state["user_id"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["user_id"] = user_by_email.uid

                if 'tolerance' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['tolerance'] = None
                if st.session_state["is_admin"] is None and st.session_state['tolerance'] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["is_admin"], st.session_state['tolerance'] = self.is_admin(user_by_email.uid, app)




                self.show_message(is_success=True,
                                  text=f'Connexion réussie ! Vous  êtes connecté   : {user_by_email.display_name}',
                                  delai=3)

                return True
            else:
                self.show_message(is_success=False, text=f'Échec de login: Mot de passe incorrect !!', delai=5)
                self.refresh()
                return False

        except Exception as error:

            self.show_message(is_success=False, text=f'Échec de login: {error}', delai=3)
            self.refresh()
            return False

    def register(self, app, email, displayname, is_admin, tolerance):
        userid = None
        try:
            user = auth.create_user(email=email, app=app, display_name=displayname)

            if email == "admin@gmail.com" or is_admin:
                auth.update_user(user.uid, custom_claims={'admin': True, "tolerance": tolerance}, app=app)
            else:
                auth.update_user(user.uid, custom_claims={'admin': False, "tolerance": tolerance}, app=app)
            body = \
                f"""
                            Bonjour Mr {user.display_name}, j'espère que vous allez bien ,
                    On vous adresse en vue de vous informer que votre compte scolaire dont l'id 
                    est {user.uid} a été créé avec succès !

                    et merci ,
                         cordialement
                    """

            self.send_email(body=body, subject="Etat de creation de votre compte scolaire ")
            self.show_message(is_success=True,
                              text=f"Utilisateur créé avec succès, votre mot de passe est: {user.uid} (vous devez l'utiliser pour s'authentifier)",
                              delai=5)

            userid = user.uid
            return True, userid
        except Exception as error:

            st.error(f"Échec d'\inscription: {error}")
            if userid is not None:
                auth.delete_user(userid)
            # self.refresh()
            return False, None

    def is_admin(self, user_id, app):
        user = auth.get_user(user_id, app=app)
        if user.custom_claims is not None:
            return user.custom_claims.get('admin', False), user.custom_claims.get('tolerance', False)
        else:
            return False, None

    def test_admin(self, app):
        # User login and ID retrieval
        user_id = st.session_state['user_id']

        if user_id:
            is_admin, _  = self.is_admin(user_id, app)
            if is_admin:
                # self.messages_placeholder.write("Welcome, Admin!")

                return True
            else:
                # st.write("Welcome, User!")
                return False


    def connexion(self, app, print= True):
        if st.session_state["is_logged_in"]:
            button_ph = st.empty()
            if print :
                current_time = time()
                elapsed_t = current_time - st.session_state['starting_time']
                if elapsed_t < 0:
                    elapsed_t = 0
                test = self.test_admin(app)
                if test :
                     welcome = "Welcome, Admin!"
                else :
                    welcome = "Welcome, User!"

                self.show_message(is_success=True,
                                  text=f"{welcome} \n\n Bonjour {st.session_state['username']} ! Vous êtes connecté depuis ({round((elapsed_t / 60), 2)}min = {round((elapsed_t), 2)}sec)",
                                  )
                # st.success(
                #     f" Bonjour {st.session_state['username']} ! Vous êtes connecté depuis ({round((elapsed_t / 60), 2)}min = {round((elapsed_t), 2)}sec)"
                #     )

            deconnec_button = button_ph.button("Deconnexion")
            if deconnec_button:
                self.messages_placeholder.empty()
                button_ph.empty()
                self.logout()


    def login_form(self, app):
        if st.session_state["is_logged_in"]:
            deconnec_button = st.button("Deconnexion")
            if deconnec_button:
                self.logout()
        else:
            login_form_placeholder = st.empty()
            register_button_placeholder = st.empty()

            with login_form_placeholder.form(key='login_form'):

                st.header("Formulaire de login  : ")

                email = st.text_input('Votre email (doit être valide) :')

                password = st.text_input('Votre password :', type="password")

                submit_button = st.form_submit_button("S'authentifier")

            if submit_button:
                login_form_placeholder.empty()
                register_button_placeholder.empty()
                if email is not None and password is not None:
                    with st.spinner('Authentification est en cours ...'):
                        sleep(1)
                        is_logged_in = self.login(app, email, password)

                    return is_logged_in
                else:
                    self.show_message(f"Veuillez remplir tous les champs !! .", is_error=True)

    def logout(self, ):
        with st.spinner('Deconnexion est en cours ...'):
            sleep(2)
            st.session_state.clear()



        self.show_message(is_success=True,
                          text=f"Vous avez déconnecté avec success!",
                          delai=3)


        self.refresh()

    def refresh(self):
        st.rerun()  # Trigger automatic refresh
        sleep(1)  # Add a slight delay to avoid rapid refreshes (optional)
        sys.exit(0)

    def space(self, length):
        for i in range(length ):
            st.write("\n")


    def get_location_path(self):

        # Obtenir le chemin d'accueil de l'utilisateur
        home_dir = os.path.expanduser('~')

        # Construire le chemin complet du dossier Téléchargements
        downloads_dir = os.path.join(home_dir, 'Downloads\location.json')

        return downloads_dir

    def get_location_navigator(self):
        jscode = """

                    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
                        
                    <script type="text/javascript">
                    /*// config de la base de données,ceci ne peut aura lieu qu'après l'intégration de login et authentification, afin d'enregistrer les cordonnées de localisation chez l'utilisateur connecté
                    // Import the functions you need from the SDKs you need
                        import { initializeApp } from "firebase/app";
                        import { getDatabase, ref, set, get, child } from "firebase/app";
                        //import { getAnalytics } from "firebase/analytics";
                        // TODO: Add SDKs for Firebase products that you want to use
                        // https://firebase.google.com/docs/web/setup#available-libraries
                        
                        // Your web app's Firebase configuration
                        // For Firebase JS SDK v7.20.0 and later, measurementId is optional
                        const firebaseConfig = {
                          apiKey: "AIzaSyDmnt05H_hnLTuTmIjD1cfOJnav4oeHaU8",
                          authDomain: "realtimeensasattendancesystem.firebaseapp.com",
                          databaseURL: "https://realtimeensasattendancesystem-default-rtdb.firebaseio.com",
                          projectId: "realtimeensasattendancesystem",
                          storageBucket: "realtimeensasattendancesystem.appspot.com",
                          messagingSenderId: "52022986400",
                          appId: "1:52022986400:web:529bfb74111df4771fabc5",
                          measurementId: "G-L27T5JC965"
                        };
                        
                        // Initialize Firebase
                        const app = initializeApp(firebaseConfig);
                        //const analytics = getAnalytics(app);
                        const database = firebase.database();
                        const reference = database.ref('locations');
                        
                        reference.set({
                          latitude: latitude,
                          longitude: longitude
                        })
                        .then(() => {
                          console.log("Coordonnées stockées avec succès dans Firebase");
                        })
                        .catch(error => {
                          console.error("Échec du stockage des coordonnées dans Firebase:", error);
                        });


                        */
                        
                        
                     if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {

                            const latitude = position.coords.latitude;
                            const longitude = position.coords.longitude;
                            const location = {
                                "Latitude": latitude,
                                "Longitude": longitude,
                            };
                            const location_json = JSON.stringify(location);
                            const blob = new Blob([location_json], {type: 'application/json'});
                            saveAs(blob, 'location.json');

                        });
                    } else {
                        alert("La géolocalisation n'est pas prise en charge par votre navigateur.");
                    }
                </script>
                                """
        st.components.v1.html(
            jscode
            , height=0
        )

    def get_location(self):

        try:

            if st.session_state['location_data'] is None:
                with open(self.get_location_path(), "r") as f:
                    location_data = json.load(f)


                st.session_state['location_data'] = location_data

            latitude = st.session_state['location_data']['Latitude']
            longitude = st.session_state['location_data']['Longitude']

            self.messages_placeholder.markdown(f"longitude: {longitude}, latitude: {latitude}")
            sleep(3)

            if os.path.exists(self.get_location_path()):
                # supprimer le fichier location pour le mettre à jour avec une nouvelle location
                os.remove(self.get_location_path())

            return latitude, longitude


        except Exception as e:

            self.messages_placeholder.markdown(f"Échec de géolocalisation .")
            return None, None  # Handle location failure

    def autoriser_presence(self, app):
        user_latitude, user_longitude = self.get_location()
        if not user_latitude or not user_latitude:
            return False

        target = "ensa safi"
        try:
            location = self.geolocator.geocode(target)
            target_latitude = location.latitude
            target_longitude = location.longitude

        except GeocoderServiceError as e:  # si le quota de requêtes est atteint pour l'ip actuel dans l'api

            # Fournir manuellement les cordonnées geo de l'Ensas
            target_latitude = 32.32638585
            target_longitude = -9.263595630981976

        distance_to_target = distance((user_latitude, user_longitude), (target_latitude, target_longitude)).km
        tolerance_distance = st.session_state['tolerance']  # 500 meters

        if tolerance_distance is not None:

            if float(distance_to_target) <= float(tolerance_distance):
                self.messages_placeholder.markdown(
                    f"**Présence autorisée**\n **Distance à {target} : {distance_to_target:.2f} km ou {distance_to_target * 1000:.2f} m**")
                sleep(5)
                st.session_state['is_authorized'] = True
                return True
            else:
                self.space(3)
                self.messages_placeholder.markdown(
                    f"**Présence refusée : Vous êtes hors de la zone autorisée**     \n\n "
                    f"**Distance à {target} : {distance_to_target:.2f} km ou {distance_to_target * 1000:.2f} m**\n\n"
                    f"**Votre tolerance est : {float(tolerance_distance)}km ou {float(tolerance_distance) * 1000:.2f} m**\n\n"
                    f"**Vous devez approcher  : {distance_to_target - float(tolerance_distance):.2f}km ou {(distance_to_target - float(tolerance_distance)) * 1000:.2f} m encore plus**")

                sleep(3)
                st.session_state['is_authorized'] = False
                self.connexion(app, print= False)
                return False

    def read_data(self, form_placeholder):
        max_time_mask_def = 60  # 1 minute
        max_time_remark_def = 60  # 1 minute
        standing_tresh_def = 10

        with form_placeholder.form(key="myform", clear_on_submit=True):
            st.header("Veuillez remplir les paramètres suivantes : ")
            st.subheader("Veuillez choisir une unité de temps : ")
            max_time_mask_unit = st.radio("Choisissez :", ["heure", "minute", "seconde"], key="max_time_mask_unit")
            st.subheader("Saisissez le temps maximum pour refaire la détection de mask :")
            max_time_mask = int(st.number_input("max_time_mask", key="max_time_mask"))
            st.subheader("Veuillez choisir une unité de temps : ")
            max_time_remark_unit = st.radio("Choisissez :", ["heure", "minute", "seconde"], key="max_time_remark_unit")
            st.subheader("Saisissez le temps maximum pour refaire la présence :")
            max_time_remark = int(st.number_input("max_time_remark", key="max_time_remark"))

            st.subheader("Saisissez le seuil de niveau de présence (standing) :")
            standing_tresh = int(st.number_input("standing_tresh", key="standing_tresh"))

            if st.form_submit_button("Set parameters & Start"):

                if not max_time_mask and not max_time_remark and not standing_tresh:
                    st.error(f"Warning : Aucun paramètre n'a été modifié.")
                    return max_time_mask_def, max_time_remark_def, standing_tresh_def

                if max_time_mask:
                    # Convert time based on unit chosen
                    if max_time_mask_unit == "seconde":
                        pass  # No conversion needed

                    elif max_time_mask_unit == "minute":
                        max_time_mask *= 60
                    else:
                        max_time_mask *= 3600
                else:
                    max_time_mask = max_time_mask_def

                if max_time_remark:
                    if max_time_remark_unit == "seconde":
                        pass
                    elif max_time_remark_unit == "minute":
                        max_time_remark *= 60
                    else:
                        max_time_remark *= 3600
                else:
                    max_time_remark = max_time_remark_def

                if standing_tresh:
                    pass
                else:
                    standing_tresh = standing_tresh_def

                return max_time_mask, max_time_remark, standing_tresh

    def adding_info(self, imgBackground, total_attendance, major, email, total_mask_detected, year, standing,
                    name, starting_year):
        cv2.putText(imgBackground, str(total_attendance), (861, 125),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(standing), (1026, 575),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(major), (1026, 530),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(email), (948, 480),
                    cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(total_mask_detected), (945, 635),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(imgBackground, str(year), (1045, 635),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(imgBackground, str(starting_year), (1155, 635),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

        # Centering the text
        (w, h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
        offset = (414 - w) // 2

        cv2.putText(imgBackground, str(name), (825 + offset, 150),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

        return imgBackground

    def update_standing(self, total_attendance, ref, standing_tresh):
        standing = "G" if total_attendance >= standing_tresh else "B"
        ref.child('standing').set(standing)

    def draw_fancy_rect(self, faceLoc, imgBackground):
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
        return imgBackground

    def compute_elapsed_time(self, last_date):
        datetimeObject = datetime.strptime(last_date, "%Y-%m-%d %H:%M:%S")
        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
        return secondsElapsed

    def show_message(self, text, delai=1, is_warning=False, is_error=False, is_success=False):
        if is_warning:
            self.messages_placeholder.warning(text)
            sleep(delai)
        elif is_error:
            self.messages_placeholder.error(text)
            sleep(delai)
        else:
            self.messages_placeholder.success(text)
            sleep(delai)

    def generate_random_string(self, length=6):
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def markAttendance(self, id, name, starting_year, year, standing, major, total_attendance, last_attendance_time,
                       total_mask_detected, last_mask_time, messages_placeholder):
        date = datetime.today().strftime('%Y-%m-%d')
        file = 'Excel files/Attendance_' + str(date) + '.csv'

        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write(
                    'id; name; starting_year; year; standing; major; total_attendance; last_attendance_time; total_mask_detected;last_mask_time')

        with open(file, 'r+') as f:
            status = False
            last_date = None
            myDataList = f.readlines()
            raw_dict = {}
            for line in myDataList:
                entry = line.split(';')
                raw_dict[entry[0]] = entry[7]

            if id not in raw_dict.keys():
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')

                f.writelines(
                    f'\n{id};{name};{starting_year};{year};{standing};{major};{total_attendance};{dtString};{total_mask_detected};{dtString}')

                self.show_message(f"Saving student info in an xlsx file", is_success=True)
                status = True
            else:
                last_date = raw_dict[id]

        return status, last_date
