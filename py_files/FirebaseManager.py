import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Instantiation of the FunctionsUtilis class

from py_files.FunctionsUtilis import FunctionsUtilis

functions = FunctionsUtilis()




class FirebaseManager:
    def __init__(self):
        self.app = None

    def __enter__(self):
        # Initialize Firebase app
        # self.app = firebase_admin.initialize_app(...)
        if self.app == None:
            cred = credentials.Certificate("serviceAccountKey.json")
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': "https://realtimeensasattendancesystem-default-rtdb.firebaseio.com/",
                'storageBucket': "realtimeensasattendancesystem.appspot.com"
            }, name=str(functions.generate_random_string(30)))
            # Getting the storage bucket instance app=FirebaseManager().app
            bucket = storage.bucket(app=self.app)

        return bucket, self.app  # Allow using the manager as a context manager