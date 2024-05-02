import streamlit as st
import os
import sys
from time import sleep

from py_files.FirebaseManager import FirebaseManager

import py_files.EncodeGenerator as encode
from io import BytesIO
from PIL import Image
import plotly.express as px
import pandas as pd
from firebase_admin import db
from py_files.FunctionsUtilis import FunctionsUtilis
from firebase_admin import auth

functions = FunctionsUtilis()

bucket, app = FirebaseManager().__enter__()

ref = db.reference('Students', app=app)
data = {}
folderPath = 'Images'

import random


def dashboard():
    student_data = db.reference('Students', app=app).get()
    if student_data is not None:
        student_data = dict(student_data)

        # Prepare data for visualizations (extract from student_data dictionary)
        year_counts = {int(student['starting_year']): len(student_data) for student in student_data.values()}
        attendance_data = [student['total_attendance'] for student in student_data.values()]

        # Create a Streamlit page for student dashboard
        st.title("Students Dashboard")

        # delete students
        # Convert student data to a Pandas DataFrame
        student_df = pd.DataFrame(student_data.values())
        student_df.index = [id for id in student_data.keys()]  # Set student ID as index

        # Function to delete student from Firebase (separate function for security)
        def delete_student_from_firebase(student_id):
            if student_id in student_data:
                # Delete student data from database
                student_ref = db.reference(f'Students/{student_id}', app=app)
                student_ref.delete()

                # Delete student image from Storage (if applicable)
                student_image_path = f"Images/{student_id}.png"
                try:
                    bucket.delete_blob(student_image_path)
                    # delete user from authentification service
                    auth.delete_user(student_id, app=app)

                except Exception as e:  # Catch any potential exception

                    st.error(e)


                # Remove student from local data

                image_path = f'{folderPath}/{student_id}.png'
                if os.path.exists(image_path):
                    # supprimer l'étudiant en question
                    os.remove(image_path)

                del student_data[student_id]  # Remove student from dictionary (for UI update)
                student_df.drop(student_id, inplace=True)  # Remove student from DataFrame

                # Mise à jour de l'encoding
                with st.spinner('Obtention de l\'encodage des images ...'):
                    # obtention de l'encodage des images
                    encode.get_store_encodings()
                st.success(f"Student with ID {student_id} deleted successfully!")
                functions.refresh()



            else:
                st.error(f"Student with ID {student_id} not found.")

        # Create a Streamlit page for student dashboard
        st.header(f"Students list : le nombre totale des étudiants : {len(student_data.values())}")
        st.subheader(f"le nombre totale des étudiants : {len(student_data.values())}")
        ###############################################################
        table_cols = st.columns(2)

        with table_cols[0]:

            student_table = st.table(student_df[['name', 'major', 'starting_year', 'total_attendance', 'standing']])

        with table_cols[1]:

            for index, row in student_df.iterrows():
                student_id = index
                delete_button = st.button(f"Delete {row['name']}", type="primary", key=str(index))
                if delete_button:
                    delete_student_from_firebase(student_id)

        # Total Attendance by Student Graph
        fig1 = px.bar(student_df, x='name', y='total_attendance',
                      title="Le nombre total de présence par étudiant", width=400)

        # Total mask detected by Student Graph
        fig2 = px.line(student_df, x='name', y='total_mask_detected',
                       title="Le nombre total de mask détecté par étudiant", width=400)

        attendance_by_major = student_df.groupby('major')['total_mask_detected'].sum().reset_index()
        fig3 = px.pie(attendance_by_major, values='total_mask_detected', names='major',
                      title="La distribution de port de mask totale par filière", width=400)

        # Standing level by Student Graph
        fig4 = px.bar(student_df, x='name', y='standing',
                      title="Le niveau de présence par étudiant", width=400)

        attendance_by_major = student_df.groupby('major')['total_attendance'].sum().reset_index()
        fig5 = px.pie(attendance_by_major, values='total_attendance', names='major',
                      title="La distribution de présence totale par filière", width=400)

        # Number of Students by Standing Graph
        standing_counts_df = student_df['standing'].value_counts().reset_index(name='Count')
        fig6 = px.bar(standing_counts_df, x='standing', y='Count',
                      title="Le nombre des étudiants par niveau de présence", width=400)

        # Distribution of Students by Starting Year
        starting_year_counts = student_df['starting_year'].value_counts().reset_index(name='Count')
        fig7 = px.pie(starting_year_counts, values='Count', names='starting_year',
                      title="La distribution des étudiants par année d'entrée", width=400)

        # Student Distribution by Year
        fig8 = px.bar(x=list(year_counts.keys()), y=list(year_counts.values()),
                      title="La distribution des étudiants par année", width=400)

        # Attendance Distribution
        fig9 = px.histogram(attendance_data,
                            title="Le nombre d\'etudiants par categories\n en termes du totale de présence ", width=400)

        # Year vs. Attendance Box Plot x='starting_year', y='total_attendance'
        year_attendance = [(student['starting_year'], student['total_attendance']) for student in student_data.values()]
        fig10 = px.box(year_attendance, x=0, y=1,
                       title="La distribution de présence (1) par année d'entrée ", width=400)

        major_attendance = [(student['major'], student['total_attendance']) for student in student_data.values()]
        fig11 = px.scatter(major_attendance, x=0, y=1,
                           title="La distribution de présence (1) par filière ", width=400)

        standing_attendance = {}
        for student in student_data.values():
            standing = student.get('standing', None)  # Handle potential missing standing data
            attendance = student['total_attendance']
            if standing:
                if standing not in standing_attendance:
                    standing_attendance[standing] = []
                standing_attendance[standing].append(attendance)
        fig12 = px.bar(x=list(standing_attendance.keys()), y=[sum(v) for v in standing_attendance.values()],
                       title="Le total  de présence par niveau de présence ", width=400)

        ####################################################################
        # Define columns , think of the use of a for loop
        st.subheader("La dimension ou l'axe etudiant")
        etudiant_cols = st.columns(3, gap="medium")

        with etudiant_cols[0]:

            st.plotly_chart(fig1)

        with etudiant_cols[1]:

            st.plotly_chart(fig2)

        with etudiant_cols[2]:

            st.plotly_chart(fig4)

        ####################################################################
        st.subheader("La dimension ou l'axe filière")
        filiere_cols = st.columns(3, gap="medium")

        with filiere_cols[0]:

            st.plotly_chart(fig3)

        with filiere_cols[1]:

            st.plotly_chart(fig5)

        with filiere_cols[2]:

            st.plotly_chart(fig11)

        ####################################################################
        st.subheader("La dimension ou l'axe année et année d'entrée")
        anne_cols = st.columns(3, gap="medium")

        with anne_cols[0]:

            st.plotly_chart(fig7)

        with anne_cols[1]:

            st.plotly_chart(fig8)

        with anne_cols[2]:

            st.plotly_chart(fig10)

        ####################################################################
        st.subheader("La dimension niveau de présence")
        niv_presence_cols = st.columns(3, gap="medium")

        with niv_presence_cols[0]:

            st.plotly_chart(fig9)

        with niv_presence_cols[1]:

            st.plotly_chart(fig12)

        with niv_presence_cols[2]:

            st.plotly_chart(fig6)


def generate_random_id():
    """Generates a random 6-digit ID with at least one non-zero digit."""
    while True:
        id_str = ''.join(str(random.randint(0, 9)) for _ in range(6))
        if any(digit != '0' for digit in id_str):  # Ensure at least one non-zero digit
            return id_str


def add_student_data(student_data, image_path=""):
    with st.spinner('Ajout de données de l\'étudiant ...'):
        id = student_data['id']

        student_data = {key: value for key, value in student_data.items() if key != 'id'}
        data[id] = student_data

        for key, value in data.items():  # for each row in the json format
            ref.child(key).set(value)


def add_data_to_db(form_placeholder):
    # Définition des options des menus déroulants
    specialties = ["AI", "INFO", "GTR", "GATE", "INDUS"]
    years = [1, 2, 3, 4, 5]
    role = ["utilisateur simple ", "admin" ]

    # Définition du formulaire
    student_data = {}
    import datetime

    current_year = datetime.datetime.now().year
    starting_years = list(range(current_year - 4, current_year + 1))  # Last 5 years

    with form_placeholder.form(key='student_data_form', clear_on_submit=True):

        # Champs du formulaire
        st.header("Adding student data : ")
        # student_data['id'] = generate_random_id()
        st.subheader("Veuillez saisir Nom complet : ")
        student_data['name'] = st.text_input('Nom complet')
        st.subheader("Veuillez choisir une spécialité : ")
        student_data['major'] = st.selectbox('Spécialité', specialties)
        st.subheader("Veuillez choisir une année : ")
        student_data['starting_year'] = st.selectbox('Année d\'entrée', starting_years)
        student_data['total_attendance'] = 0
        student_data['standing'] = "B"
        st.subheader("Veuillez choisir  une année : ")
        student_data['year'] = st.selectbox('Année en cours', years)
        student_data['last_attendance_time'] = "2024-04-11 00:54:34"
        student_data['total_mask_detected'] = 0
        student_data['last_mask_time'] = "2024-04-11 00:54:34"
        st.subheader("Veuillez saisir un email valide: ")
        email = st.text_input('Votre email  :')
        displayname = student_data['name']
        st.subheader("Veuillez choisir le rôle : ")
        user_role = st.selectbox('Rôle', role)
        st.subheader("Veuillez choisir une image (max 3MO) : ")
        image_file = st.file_uploader('Image de l\'étudiant')

        # Bouton de soumission
        submit_button = st.form_submit_button('Créer et ajouter l\'étudiant')

    if submit_button:

        # Vérification si l'image a été téléchargée
        if image_file is not None:


                # creation de l'utilisateur
                if email is not None and displayname is not None:
                    with st.spinner("Inscription de l'utilisateur est en cours ..."):
                        sleep(1)
                        if user_role == "admin":
                            is_admin = True
                        else :
                            is_admin = False
                        is_registred, uid = functions.register(app, email, displayname, is_admin)
                        # print(f"Le user : {uid}")
                    # return is_registred
                else:
                    functions.show_message(f"Veuillez remplir l'email et le nom complet !! .", is_error=True)
                # print("avant user_role")
                if uid is not None:
                    with st.spinner('Adding data to database ...'):
                        # print(user_role)
                        student_data["id"] = uid

                        # Enregistrement de l'image dans localement
                        image_path = f'{folderPath}/{student_data["id"]}.png'

                        image_data = image_file.read()
                        image_stream = BytesIO(image_data)  # Create an in-memory stream from image data
                        image = Image.open(image_stream)  # Open the image from the stream
                        resized_image = image.resize((216, 216), Image.ANTIALIAS)

                        # enregistrement local de l'image
                        with open(image_path, 'wb') as f:
                            resized_image.save(f, 'PNG')  # Save as JPEG

                        with st.spinner('Obtention de l\'encodage des images ...'):
                            sleep(3)
                            # obtention de l'encodage des images
                            encoding_state = encode.get_store_encodings()
                            if encoding_state:
                                # student_data['latitude'] = 0
                                # student_data['longitude'] = 0
                                # Ajout des données à Firebase
                                add_student_data(student_data)

                                # Ajout de l'image dans firebase
                                blob = bucket.blob(image_path)  # converting the image to the proper format for storing
                                blob.upload_from_filename(image_path)  # send images to the storage bucket

                                # Affichage d'un message de confirmation
                                st.success('L\'Étudiant est ajouté avec succès!')
                                sleep(3)
                            else:  # suppression locale de l'image non valide
                                # Remove student from local data

                                if os.path.exists(image_path):
                                    # supprimer l'étudiant en question
                                    os.remove(image_path)
                                st.error("Problème d\'encodage : Veuillez choisir une autre image de l\'étudiant.")

                else:
                    functions.show_message(f"Un problème imprévue lors de création d'utilisateur ", is_error=True,
                                           delai=5)
        else:
            # Affichage d'un message d'erreur si l'image n'a pas été téléchargée
            st.error('Veuillez télécharger une image de l\'étudiant.')
