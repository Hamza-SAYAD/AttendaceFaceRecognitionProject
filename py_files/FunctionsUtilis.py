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

from firebase_admin import auth, exceptions
import json


class FunctionsUtilis:

    def __init__(self, messages_placeholder=st.empty()):
        self.messages_placeholder = messages_placeholder
        self.geolocator = Nominatim(user_agent="attendance_mask_app")

    def login(self, app, email, password):

        try:

            user_by_email = auth.get_user_by_email(email, app=app)
            # user_by_id = auth.get_user(password, app=app )

            if user_by_email.uid == password:
                # print(user_by_email)
                # if user_by_email == user_by_id :
                # print('Connexion réussie:', user_by_email.uid)
                if email == "admin@gmail.com" :
                    auth.update_user(user_by_email.uid, custom_claims={'admin': True}, app=app)

                # auth.update_user(user_by_email.uid, custom_claims={'admin': True}, app=app)
                if 'username' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['username'] = None

                # is_registered = functions.register_form(app)
                if st.session_state["username"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["username"] = user_by_email.display_name

                if 'user_id' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['user_id'] = None

                # is_registered = functions.register_form(app)
                if st.session_state["user_id"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["user_id"] = user_by_email.uid

                if 'is_admin' not in st.session_state:  # insertion de email et user name dans la session
                    st.session_state['is_admin'] = None

                # is_registered = functions.register_form(app)
                if st.session_state["is_admin"] is None:  # si l'utilisateur n'est pas logged in
                    st.session_state["is_admin"] = self.is_admin(user_by_email.uid, app)

                self.show_message(is_success=True,
                                  text=f'Connexion réussie ! Vous  êtes connecté   : {user_by_email.display_name}',
                                  delai=3)
                # self.refresh()
                return True
            else:
                self.show_message(is_success=False, text=f'Échec de login: Mot de passe incorrect !!', delai=5)
                self.refresh()
                return False

        except Exception as error:
            # print('Échec de la connexion:', error)
            # print(f'Échec de login: {error}')
            self.show_message(is_success=False, text=f'Échec de login: {error}', delai=3)
            self.refresh()
            return False

    def register(self, app, email, displayname, is_admin):
        userid = None
        try:
            user = auth.create_user(email=email, app=app, display_name=displayname)
            # print('Utilisateur créé avec succès:', user.uid)
            # auth.create_session_cookie()
            if email == "admin@gmail.com" or is_admin:
                auth.update_user(user.uid, custom_claims={'admin': True}, app=app)
            else:
                auth.update_user(user.uid, custom_claims={'admin': False}, app=app)
            self.show_message(is_success=True,
                              text=f"Utilisateur créé avec succès, votre mot de passe est: {user.uid} (vous devez l'utiliser pour s'authentifier)",
                              delai=5)
            # print(f"\n\nLe user de register : {user.uid}")
            userid = user.uid
            return True, userid
        except Exception as error:
            # print('Échec de la création de l\'utilisateur:', error)
            st.error(f"Échec d'\inscription: {error}")
            if userid is not None:
                auth.delete_user(userid)
            # self.refresh()
            return False, None

    def is_admin(self, user_id, app):
        user = auth.get_user(user_id, app=app)
        if user.custom_claims is not None:
            return user.custom_claims.get('admin', False)
        else:
            return False

    def test_admin(self, app):
        # User login and ID retrieval (replace with your login logic)
        user_id = st.session_state['user_id']

        if user_id:
            if self.is_admin(user_id, app):
                st.write("Welcome, Admin!")
                # Display admin-specific functionalities
                return True
            else:
                st.write("Welcome, User!")
                return False
            # Display regular user functionalities

    # else:
    #
    # # Login form or instructions
    # # ...

    def register_form(self, app):
        if st.session_state["is_logged_in"]:
            current_time = time()
            elapsed_t = current_time - st.session_state['starting_time']
            if elapsed_t < 0:
                elapsed_t = 0
            self.test_admin(app)
            # self.space(3)
            st.success(
                f" Bonjour {st.session_state['username']} ! Vous êtes connecté depuis ({round((elapsed_t / 60), 2)}min = {round((elapsed_t), 2)}sec)"
                )
            deconnec_button = st.button("Deconnexion")
            if deconnec_button:
                self.logout()
        # else :
        #     register_form_placeholder = st.empty()
        #     login_button_placeholder = st.empty()
        #     with register_form_placeholder.form(key='register_form'):
        #
        #         st.header("Formulaire d'inscription  : ")
        #
        #         email = st.text_input('Votre email (doit être valide) :')
        #
        #         displayname = st.text_input('Nom et prenom :')
        #
        #         submit_button = st.form_submit_button("S'inscrire")
        #     login_button = login_button_placeholder.button("S'authentifier")
        #     # print("\n\navant submit_button register")
        #     if submit_button:
        #         # print("\ndebut de  submit_button register")
        #         register_form_placeholder.empty()
        #         login_button_placeholder.empty()
        #         if email is not None and displayname is not None:
        #             with st.spinner('Inscription est en cours ...'):
        #                 sleep(1)
        #                 is_registred = self.register(app, email, displayname)
        #             return is_registred
        #         else :
        #             self.show_message(f"Veuillez remplir tous les champs !! .", is_error=True)
        #         # print("\nfin de  submit_button register")
        #     elif login_button:
        #         register_form_placeholder.empty()
        #         login_button_placeholder.empty()
        #         self.login_form(app)

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
            # register_button = register_button_placeholder.button("S'inscrire")

            if submit_button:
                login_form_placeholder.empty()
                register_button_placeholder.empty()
                if email is not None and password is not None:
                    with st.spinner('Authentification est en cours ...'):
                        sleep(1)
                        is_logged_in = self.login(app, email, password)
                        print(is_logged_in)
                    return is_logged_in
                else:
                    self.show_message(f"Veuillez remplir tous les champs !! .", is_error=True)
            # elif register_button:
            #     login_form_placeholder.empty()
            #     register_button_placeholder.empty()
            #     self.register_form(app)

    def logout(self):
        with st.spinner('Deconnexion est en cours ...'):
            sleep(2)
            st.session_state.clear()
            # st.session_state["is_logged_in"] = None
        self.show_message(is_success=True,
                          text=f"Vous avez déconnecté avec success!",
                          delai=3)
        # st.rerun()

        self.refresh()

    def refresh(self):
        st.rerun()  # Trigger automatic refresh
        sleep(1)  # Add a slight delay to avoid rapid refreshes (optional)
        sys.exit(0)

    def space(self, length):
        for i in range(length * 2):
            st.write("\n")

    # def get_tolerance_value(self):
    #     tolerance_distance = 5
    #     tolerance_form_placeholder = st.empty()
    #
    #     with tolerance_form_placeholder.form(key='tolerance_location_form'):
    #
    #         # Champs du formulaire
    #         st.header("Saisie de tolerance de localisation : ")
    #
    #         st.subheader("Veuillez saisir la valeur de tolerance de distance  : (en km) ")
    #         tolerance = st.text_input('La tolerance :', value=0.5)
    #
    #
    #         # Bouton de soumission
    #         submit_button = st.form_submit_button('Set tolerance')
    #
    #     if submit_button:
    #         tolerance_form_placeholder.empty()
    #         if tolerance is not None :
    #
    #             st.success(f"La tolerance est : {tolerance} km")
    #
    #             return  float(tolerance)
    #         else :
    #             st.success(f"La tolerance est : {tolerance_distance} km")
    #
    #             return float(tolerance_distance)

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

                # print(location_data)
                st.session_state['location_data'] = location_data

            latitude = st.session_state['location_data']['Latitude']
            longitude = st.session_state['location_data']['Longitude']

            self.messages_placeholder.markdown(f"longitude: {longitude}, latitude: {latitude}")
            sleep(1)

            if os.path.exists(self.get_location_path()):
                # supprimer le fichier location pour le mettre à jour avec une nouvelle location
                os.remove(self.get_location_path())

            return latitude, longitude


        except Exception as e:

            self.messages_placeholder.markdown(f"Échec de géolocalisation .")
            return None, None  # Handle location failure

    def autoriser_presence(self):
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
        tolerance_distance = 1500  # 500 meters
        # tolerance_distance = self.get_tolerance_value()
        if tolerance_distance is not None:

            if float(distance_to_target) <= tolerance_distance:
                self.messages_placeholder.markdown(
                    f"**Présence autorisée**\n **Distance à {target} : {distance_to_target:.2f} km ou {distance_to_target * 1000:.2f} m**")
                sleep(1)

                return True
            else:

                self.messages_placeholder.markdown(
                    f"**Présence refusée : Vous êtes hors de la zone autorisée**     \n **Distance à {target} : {distance_to_target:.2f} km ou {distance_to_target * 1000:.2f} m**")

                sleep(1)
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

    def adding_info(self, imgBackground, total_attendance, major, id, total_mask_detected, year, standing,
                    name, starting_year):
        cv2.putText(imgBackground, str(total_attendance), (861, 125),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(standing), (1026, 575),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(major), (1026, 530),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(id), (1026, 480),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
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
