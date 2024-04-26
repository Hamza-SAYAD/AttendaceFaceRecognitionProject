import streamlit as st
import os

from time import sleep
import cv2

import cvzone



from datetime import datetime

import random, string


from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

from geopy.distance import distance
import json

class FunctionsUtilis:


    def __init__(self, messages_placeholder = st.empty()):
        self.messages_placeholder = messages_placeholder
        self.geolocator = Nominatim(user_agent="attendance_mask_app")

    def get_location_path(self) :

        # Obtenir le chemin d'accueil de l'utilisateur
        home_dir = os.path.expanduser('~')

        # Construire le chemin complet du dossier Téléchargements
        downloads_dir = os.path.join(home_dir, 'Downloads\location.json')


        return downloads_dir

    def get_location_navigator(self) :
        jscode = """

                    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
                    <script type="text/javascript">
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
    def get_location(self ):



        try :



            with open(self.get_location_path(), "r") as f:
                location_data = json.load(f)


            latitude = location_data['Latitude']
            longitude = location_data['Longitude']

            self.messages_placeholder.markdown(f"longitude: {longitude}, latitude: {latitude}")
            sleep(1)


            if os.path.exists(self.get_location_path()):
                # supprimer le fichier location pour le mettre à jour avec une nouvelle location
                os.remove(self.get_location_path())

            return latitude, longitude


        except Exception as e:
            # print(f"Échec de la géolocalisation du navigateur: {e}")
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

        except GeocoderServiceError as e: # si le quota de requêtes est atteint pour l'ip actuel dans l'api

            # Fournir manuellement les cordonnées geo de l'Ensas
            target_latitude = 32.32638585
            target_longitude = -9.263595630981976

        distance_to_target = distance((user_latitude, user_longitude), (target_latitude, target_longitude)).km
        tolerance_distance = 5 # 500 meters

        if distance_to_target <= tolerance_distance:
            self.messages_placeholder.markdown("**Présence autorisée**")
            sleep(1)
            self.messages_placeholder.markdown(f"**Distance à {target} : {distance_to_target:.2f} km**")
            sleep(2)
            return True
        else:
            self.messages_placeholder.markdown("**Présence refusée : Vous êtes hors de la zone autorisée**")
            sleep(1)
            self.messages_placeholder.markdown(f"**Distance à {target} : {distance_to_target:.2f} km**")
            # sleep(1)
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

                self.show_message( f"Saving student info in an xlsx file", is_success=True)
                status = True
            else:
                last_date = raw_dict[id]

        return status, last_date

