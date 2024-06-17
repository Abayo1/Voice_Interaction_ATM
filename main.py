from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import logging
import time
import threading
from face_verifier import FaceVerifier
from speech_processor import SpeechProcessor
from image_capture import ImageCapture

templates = Jinja2Templates(directory="templates")

app = FastAPI()
face_verifier = FaceVerifier()
speech_processor = SpeechProcessor()
image_capture = ImageCapture()

if not os.path.exists('static'):
    os.makedirs('static')


logging.basicConfig(level=logging.INFO)#logging

class FirstNameRequest(BaseModel):
    firstName: str

def get_database_images(first_name: str):
    db_path = os.path.join('face_db', first_name.lower())
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database path not found for user: {first_name}")

    db_images = []
    for file_name in os.listdir(db_path):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            db_images.append(os.path.join(db_path, file_name))
    return db_images

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/activate-atm/")
async def activate_atm():
    # Waiting for the activation keyword
    speech_processor.text_to_speech("Waiting for activation keyword...")

    def handle_activation():
        print("Recognizing...")
        # Recognize the speech
        text = speech_processor.speech_to_text()                         
        print("You said:", text)             
        if "atm" in text.lower():
            return True               
        else:
            return False                                       

    activation_detected = handle_activation()
    if activation_detected:
        speech_processor.text_to_speech("Activation keyword detected. Activating ATM...")
        speech_processor.text_to_speech("Hello, welcome. What is your first name?")
        first_name = speech_processor.speech_to_text()
        speech_processor.text_to_speech(f"Welcome {first_name}. Please wait as we verify you.")

        
        image_path = image_capture.capture_image()# Capture image
        print(f"Image captured and saved to path: {image_path}")
        
        verification_result = await verify_face_from_path(first_name=first_name.lower(), image_path=image_path)# face verification

        logging.info(f"Verification result: {verification_result}")

        # verification result
        if verification_result and "Face verified successfully" in verification_result.get("result", ""):
            speech_processor.text_to_speech(f"Hello {first_name}, you are verified.")
            await present_services(first_name)
        else:
            speech_processor.text_to_speech("Unfortunately, we couldn't verify you. Please try again later.")
            return JSONResponse({"message": "Face verification failed. Please try again later."})
    else:
        speech_processor.text_to_speech("Activation failed. Please try again.")
        return JSONResponse({"message": "Activation failed"})

async def present_services(first_name):
    speech_processor.text_to_speech("Here are the services: (1) Withdraw money, (2) Check balance, (3) Other services. Please choose the service you want today.")
    
    
    service_choice = speech_processor.speech_to_text()# user's choice

    if "withdraw" in service_choice or "1" in service_choice:
        await handle_withdrawal()
    elif "check balance" in service_choice or "2" in service_choice:
        await handle_check_balance()
    elif "other services" in service_choice or "3" in service_choice:
        await handle_other_services()
    else:
        speech_processor.text_to_speech("Invalid choice. Please say the number of the service you want to choose.")
        await present_services(first_name)
    
    #restart the ATM service
    await activate_atm()

async def handle_withdrawal():
    speech_processor.text_to_speech("You chose to withdraw money. Please say the amount you want to withdraw less than or equal to 1000000")
    
    amount = speech_processor.speech_to_text()
    speech_processor.text_to_speech(f"You have requested to withdraw {amount} dollars. Please wait while we process your request.")
    
    # Simulating withdrawal process
    time.sleep(3)
    speech_processor.text_to_speech("Your withdrawal is successful. Please collect your cash. Thank you for using our ATM.")

async def handle_check_balance():
    speech_processor.text_to_speech("You chose to check your balance. Please wait while we retrieve your balance.")
    
    # Simulating balance retrieval process
    time.sleep(3)
    speech_processor.text_to_speech("Your current balance is 1,000,234.56. Thank you for using our ATM.")

async def handle_other_services():
    speech_processor.text_to_speech("You chose other services. Here are the options: (1) Change PIN, (2) Mini statement. Please say the number of the service you want to choose.")
    
    service_choice = speech_processor.speech_to_text()

    if "change pin" in service_choice or "1" in service_choice:
        await handle_change_pin()
    elif "mini statement" in service_choice or "2" in service_choice:
        await handle_mini_statement()
    else:
        speech_processor.text_to_speech("Invalid choice. Please say the number of the service you want to choose.")
        await handle_other_services()

async def handle_change_pin():
    speech_processor.text_to_speech("You chose to change your PIN. Please say your new PIN.")
    
    new_pin = speech_processor.speech_to_text()
    speech_processor.text_to_speech(f"Your PIN has been changed to {new_pin}. Thank you for using our ATM.")

async def handle_mini_statement():
    speech_processor.text_to_speech("You chose to receive a mini statement. Please wait while we retrieve your statement.")
    
    # Simulating mini statement retrieval process
    time.sleep(3)
    speech_processor.text_to_speech("Your mini statement is: Last 5 transactions: Debit Tanzanian shillings 100000, Credit Tanzanian shillings 50000, Debit Tanzanian shillings 3000000, Credit Tanzanian shillings 200000000, Debit Tanzanian shillings 70000. Thank you for using our ATM.")

# Verify the face
async def verify_face_from_path(first_name: str, image_path: str):
    try:
        
        if not os.path.exists(image_path):#captured image exists
            raise FileNotFoundError(f"Captured image not found at path: {image_path}")
        
        logging.info(f"Captured image path: {image_path}")

        
        db_images = get_database_images(first_name)# database images

        if not db_images:
            return {"result": "No images found in the database"}

        verified = False
        for db_image in db_images:
            logging.info(f"Comparing {image_path} with {db_image}")
            
            if not os.path.exists(db_image):
                logging.error(f"Database image not found at path: {db_image}")
                continue

            try:
                result = face_verifier.verify_faces(image_path, db_image)
                if result:
                    verified = True
                    break
            except Exception as e:
                logging.error(f"Error comparing {image_path} with {db_image}: {str(e)}")
                continue

        if verified:
            return {"result": "Face verified successfully"}
        else:
            return {"result": "Face verification failed"}
    except Exception as e:
        logging.error(f"General error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000)).start()
    
    speech_processor.text_to_speech("Waiting for activation keyword...")
    
    def listen_for_activation():
        while True:
            text = speech_processor.speech_to_text()
            print("You said:", text)
            if "atm" in text.lower():
                activate_atm()

    activation_thread = threading.Thread(target=listen_for_activation)
    activation_thread.start()
    


