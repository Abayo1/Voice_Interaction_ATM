# Voice_Interaction_ATM(VIA)
A proof of concept simulating ATM speech interaction which can be used by blind people.
# steps to run the VIA-API
Note: create a virtual environment and install packages in the venv
1. pip install -r requirements.txt
2. put your face image in the folder 'timothy' which is within 'face_db' directory
2. run 'uvicorn main:app --reload --port'
3. you can test the VIA-API in the browser using localhost (127.0.0.1:8000)
4. After firing up the API activate the app by the word 'ATM'
5. When asked your first name, say 'timothy'. You can change the folder name or add another folder with the same structure in the 'face_db'.
