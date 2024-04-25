import os
import sys
from time import sleep

from py_files.FirebaseManager import FirebaseManager
import streamlit as st
import py_files.EncodeGenerator as encode
from io import BytesIO
from PIL import Image
import plotly.express as px
import pandas as pd
from firebase_admin import db

bucket, app = FirebaseManager().__enter__()

ref = db.reference('Students', app=app)
data = {}
folderPath = 'Images'

import random


def dashboard():

    student_data = db.reference('Students', app=app).get()
    if student_data is not None :
        student_data = dict(student_data)

        # Prepare data for visualizations (extract from student_data dictionary)
        year_counts = {int(student['starting_year']): len(student_data) for student in student_data.values()}
        gpa_data = [student.get('gpa', None) for student in student_data.values() if
                    student.get('gpa', None) is not None]  # Handle potential missing GPA data
        attendance_data = [student['total_attendance'] for student in student_data.values()]

        # Create a Streamlit page for student dashboard
        st.title("Students Dashboard")

        # Student Distribution by Year
        fig = px.bar(x=list(year_counts.keys()), y=list(year_counts.values()), title="Student Distribution by Year")
        st.plotly_chart(fig)


        # Attendance Distribution
        fig = px.histogram(attendance_data, title="Attendance Distribution")
        st.plotly_chart(fig)


        # Year vs. Attendance Box Plot x='starting_year', y='total_attendance'
        year_attendance = [(student['starting_year'], student['total_attendance']) for student in student_data.values()]
        fig = px.box(year_attendance, x=0, y=1,
                     title="Attendance Distribution by Year (0 for starting _year and 1 is the total_attendance)")
        st.plotly_chart(fig)

        # Major vs. Attendance Scatter Plot (if available) if 'major' in student_data.values()[0]

        major_attendance = [(student['major'], student['total_attendance']) for student in student_data.values()]
        fig = px.scatter(major_attendance, x=0, y=1,
                         title="Attendance Distribution (1) by Major (0)")
        st.plotly_chart(fig)


        # Standing (Nivea de présence) vs. Attendance (total nombre de présence) Bar Chart
        standing_attendance = {}
        for student in student_data.values():
            standing = student.get('standing', None)  # Handle potential missing standing data
            attendance = student['total_attendance']
            if standing:
                if standing not in standing_attendance:
                    standing_attendance[standing] = []
                standing_attendance[standing].append(attendance)
        fig = px.bar(x=list(standing_attendance.keys()), y=[sum(v) for v in standing_attendance.values()],
                     title="Average Attendance by Standing")
        st.plotly_chart(fig)




        # delete students
        # Convert student data to a Pandas DataFrame
        student_df = pd.DataFrame(student_data.values())
        # student_df.index = student_df['id']  # Set student ID as index
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
                except Exception as e:  # Catch any potential exception
                    if "NOT_FOUND" in str(e):  # Check for a string containing "NOT_FOUND"
                        st.info(f"Student image for ID {student_id} not found in Storage.")
                    else:
                        st.error(f"Error deleting student image: {e}")  # Log or display the error

                # Remove student from local data

                image_path = f'{folderPath}/{student_id}.png'
                if os.path.exists(image_path):
                    # supprimer l'étudiant en question
                    os.remove(image_path)

                del student_data[student_id]  # Remove student from dictionary (for UI update)
                student_df.drop(student_id, inplace=True)  # Remove student from DataFrame
                st.success(f"Student with ID {student_id} deleted successfully!")
                # refresh
                st.rerun()  # Trigger automatic refresh
                sleep(1)  # Add a slight delay to avoid rapid refreshes (optional)
                sys.exit(0)


            else:
                st.error(f"Student with ID {student_id} not found.")

        # Create a Streamlit page for student dashboard
        st.header("Students list :")



        # Student Table with Delete Confirmation Button
        student_table = st.table(student_df[['name', 'major', 'starting_year', 'total_attendance', 'standing']])


        for index, row in student_df.iterrows():
            student_id = index

            # student_id = row['id']
            delete_button = st.button(f"Delete Student {student_id}")
            if delete_button:
                delete_student_from_firebase(student_id)


        # Total Attendance by Student Graph
        attendance_fig = px.bar(student_df, x='name', y='total_attendance', title="Total Attendance by Student")
        # Display the attendance graph
        st.plotly_chart(attendance_fig)

        # Assuming 'major' exists in student_df
        attendance_by_major = student_df.groupby('major')['total_attendance'].sum().reset_index()
        attendance_fig = px.pie(attendance_by_major, values='total_attendance', names='major',
                                title="Attendance Distribution by Major")
        st.plotly_chart(attendance_fig)



        # Standing level by Student Graph
        attendance_fig = px.bar(student_df, x='name', y='standing', title="Total Attendance by Student")
        # Display the attendance graph
        st.plotly_chart(attendance_fig)



        # Number of Students by Standing Graph
        standing_counts_df = student_df['standing'].value_counts().reset_index(name='Count')
        standing_fig = px.bar(standing_counts_df, x='standing', y='Count', title="Number of Students by Standing")
        # Display the standing graph
        st.plotly_chart(standing_fig)




        # Distribution of Students by Starting Year
        starting_year_counts = student_df['starting_year'].value_counts().reset_index(name='Count')
        starting_year_fig = px.pie(starting_year_counts, values='Count', names='starting_year', title="Distribution of Students by Starting Year")
        st.plotly_chart(starting_year_fig)

         # we can add more graphs for the masm as the attendance

def generate_random_id():
    """Generates a random 6-digit ID with at least one non-zero digit."""
    while True:
        id_str = ''.join(str(random.randint(0, 9)) for _ in range(6))
        if any(digit != '0' for digit in id_str):  # Ensure at least one non-zero digit
            return id_str


def add_student_data(student_data, image_path=""):
    with st.spinner('Ajout de données de l\'étudiant ...'):
        id = student_data['id']
        # student_data.pop(id)
        student_data = {key: value for key, value in student_data.items() if key != 'id'}
        data[id] = student_data
        # print(data)
        for key, value in data.items():  # for each row in the json format
            ref.child(key).set(value)


# ,
#             'image': image_encoded


def add_data_to_db(form_placeholder):
    # Définition des options des menus déroulants
    specialties = ["AI", "INFO", "GTR", "GATE", "INDUS"]
    years = [1, 2, 3, 4, 5]

    # Définition du formulaire
    student_data = {}
    import datetime

    current_year = datetime.datetime.now().year
    starting_years = list(range(current_year - 4, current_year + 1))  # Last 5 years

    # ... (existing code for the form)

    with form_placeholder.form(key='student_data_form', clear_on_submit=True):

        # Champs du formulaire
        st.header("Adding student data : ")
        student_data['id'] = generate_random_id()
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
        st.subheader("Veuillez choisir une image (max 3MO) : ")
        image_file = st.file_uploader('Image de l\'étudiant')

        # Bouton de soumission
        submit_button = st.form_submit_button('Ajouter l\'étudiant')

    if submit_button:
        with st.spinner('Adding data to database ...'):
            # Vérification si l'image a été téléchargée
            if image_file is not None:

                # Enregistrement de l'image dans un fichier temporaire
                image_path = f'{folderPath}/{student_data["id"]}.png'

                image_data = image_file.read()
                image_stream = BytesIO(image_data)  # Create an in-memory stream from image data
                image = Image.open(image_stream)  # Open the image from the stream
                resized_image = image.resize((216, 216), Image.ANTIALIAS)

                with open(image_path, 'wb') as f:
                    resized_image.save(f, 'PNG')  # Save as JPEG

                # Ajout des données à Firebase
                add_student_data(student_data)

                # Ajout de l'image dans firebase
                blob = bucket.blob(image_path)  # converting the image to the proper format for storing
                blob.upload_from_filename(image_path)  # send images to the storage bucket


                with st.spinner('Obtention de l\'encodage des images ...'):
                    # obtention de l'encodage des images
                    encode.get_store_encodings()
                # Affichage d'un message de confirmation
                st.success('L\'Étudiant est ajouté avec succès!')
            else:
                # Affichage d'un message d'erreur si l'image n'a pas été téléchargée
                st.error('Veuillez télécharger une image de l\'étudiant.')
