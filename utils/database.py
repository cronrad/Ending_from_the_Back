import secrets
import bcrypt
import os
from pymongo import MongoClient
from flask_mail import Mail
import string
from flask_mail import Message

mongoClient = MongoClient("localhost") #For testing only
#mongoClient = MongoClient("mongo")

db = mongoClient["cse312_project"]
authDB = db["auth"]
postDB = db["post"]
fileDB = db["file"]
answDB = db["answ"]
gradeDB = db["grade"]

#HTML escaper function #TODO: Percent encoding?
#Author: Gordon Tang
#Inputs: String
#Outputs: String that has escaped html characters
def HTMLescaper(HTMLString):
    if HTMLString == None:
        return None
    else:
        removedAmp = HTMLString.replace("&", "&amp;")
        removedLess = removedAmp.replace("<", "&lt;")
        removedGreat = removedLess.replace(">", "&gt;")
        return removedGreat

#Registration function
#Author: Gordon Tang
#Inputs: username, password
#Outputs: returns True if registration is successful, False if the username already exists
def registerDB(username, password):
    safe_username = HTMLescaper(username)
    exists = authDB.find_one({"username": safe_username})
    if exists == None:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        authDB.insert_one({"username": safe_username, "password": hashed_password})
        return True
    elif exists != None:
        return False

#Login authentication function. Takes a username, password, authentication token from a cookie, and the option to ignore the token
#Author: Gordon Tang
#Inputs: username, password, and token can be None or "". ignore_token is either True or False
#Outputs: Returns a tupple that contains a token and username. Token can be used for cookie. If it's an invalid login, then it returns (False, False)
#Example call: auth_token, verified_name = authenticate(username, password, token, False)
def authenticate(username, password, token, ignore_token):
    if username == "":
        username = None
    if password == "":
        password == None
    if token == "":
        token == None
    safe_username = HTMLescaper(username)
    if token == None or ignore_token == True: #No token or ignoring token means user must supply username and password
        exists = authDB.find_one({"username": safe_username})
        if exists == None: #Username doesn't exist in db, don't authenticate
            return False, False
        elif exists != None: #User exists, check password
            valid_password = bcrypt.checkpw(password.encode(), exists["password"])
            if valid_password == False: #Wrong password
                return False, False
            elif valid_password == True: #Correct password, generate + store token, return token and username
                generated_token = secrets.token_hex(32)
                hashed_token = bcrypt.hashpw(generated_token.encode(), bcrypt.gensalt())
                authDB.update_one({"username": username}, {"$set": {"authToken": hashed_token}})
                return generated_token, exists["username"]
    elif token != None: #We want to use the token to see if it is a valid user
        #TODO: Check how to salt with the same salt in order to do a db lookup or loop through and perform hash operation
        #TODO: Former option is probably better? Less hash operations performed
        #Or loop through all db documents and perform a bcrypt.checkpw on every document if there is a token field?
        iterator = authDB.find()
        userDoc = None
        for i in iterator:
            if "authToken" in i:
                match = bcrypt.checkpw(token.encode(), i["authToken"])
                if match == True:
                    userDoc = i
                    break
        if userDoc == None: #No user matches token
            return False, False
        elif userDoc != None: #Found token that matches user
            return token, userDoc["username"]

#Takes the websocket post data and stores the data in the db
#Returns a object that will be broadcasted to all websocket connection
#Author: Gordon Tang
def handlePost(username, title, description, answer, file_name):
    #Finds or creates the post id system in the postDB collection
    postIDs = postDB.find_one({"postIDCounter": {"$exists": True}})
    if postIDs == None:  # First message in db
        postDB.insert_one({"postIDCounter": 1})
    #Inserts the post data into the db
    postID = postDB.find_one({"postIDCounter": {"$exists": True}})
    postDB.insert_one({"postID": postID["postIDCounter"], "username": username, "title": title, "description": description, "answer": answer, "file_name": file_name, "Answerable": 60, "user_answers": {}})
    #Create the response json
    response = {"postID": postID["postIDCounter"] ,"username": username, "title": title, "description": description}
    postDB.update_one({}, {"$inc": {"postIDCounter": 1}})
    return response


#Takes a the file name of a file that has been uploaded and a username, takes only username since this is for websockets
#Returns the name of the file that will be saved if token is valid and file gets saved, otherwise False
#Author: Gordon Tang
def setFileID(username, originalFileName):
    #Retrieve the user's doc
    #Create/Retrieve the latest file ID
    originalFileName = originalFileName.replace("/", "")
    fileIDs = fileDB.find_one({"fileNameCounter": {"$exists": True}})
    if fileIDs == None:
        fileDB.insert_one({"fileIDCounter": 1})
    #Set the person's doc to have a file name id
    fileID = fileDB.find_one({"fileIDCounter": {"$exists": True}})
    fileName = "image" + str(fileID["fileIDCounter"]) + ".jpg"
    #Set the file id in the file db
    fileDB.insert_one({"original": originalFileName, "new": fileName})
    #Increment the next ID
    fileDB.update_one({}, {"$inc": {"fileIDCounter": 1}})
    return fileName

#Takes the file part of the dictionary and username and saves a file
#Author: Gordon Tang
def saveFile(username, data):
    file_dict = data["file_name"]
    # Get the actual data of the file
    file_content = bytearray(file_dict["content"])
    # Get the new file name
    file_name = setFileID(username, file_dict["name"])
    filePath = os.path.join('public/image/', file_name)
    with open(filePath, 'wb') as file:
        file.write(file_content)
    return file_name


#Function will enter the data we received into database
#Returns None if the question id doesn't exist, False if the user has already submitted or they create it, True if successful
#Author: Aryan Kum / Sam Palutro / Gordon Tang
def enteringAnswers(username, answerID, answerContent):
    #Retrieve the question post document
    question_doc = postDB.find_one({"postID": int(answerID)})
    if question_doc == None: #Trying to answer a question that doesn't exist
        return None
    if question_doc["username"] == username: #Trying to answer their own question
        return "1"
    if question_doc["Answerable"] == 0: #Trying to answer when time limit is reached
        return "2"
    elif question_doc != None: #Retrieve the dictionary of stored answers
        user_answers = question_doc["user_answers"]
        #Check if the user has already answered
        if username in user_answers: #User has already submitted an answer, cannot submit more than once
            return "3"
        else: #Submit the answer into db
            user_answers[username] = HTMLescaper(answerContent) #Update the dictionary we retrieved
            postDB.update_one({"postID": int(answerID)}, {"$set": {"user_answers": user_answers}}) #Update the entry in the db
            return True

#Finds the doc and updates the time for it
def getTimeRemaining(id):
    question_doc = postDB.find_one({"postID": id})
    remaining = question_doc["Answerable"]
    return remaining

def updateTimeRemaining(id, seconds):
    postDB.update_one({"postID": id}, {"$set": {"Answerable": seconds}})

def resetTimers():
    postDB.update_many({}, {"$set": {"Answerable": 0}})

#Grades and stores the grade for functions
def grading():
    for post in postDB.find({}):
        if "postIDCounter" in post:
            continue
        else:
            user_scores = {}
            for key, val in post["user_answers"].items():
                if str(post["answer"]).lower() == str(val).lower():
                    user_scores[str(key)] = 1
                else:
                    user_scores[str(key)] = 0

            postDB.update_one({"postID": post["postID"]}, {'$set': {'user_scores': user_scores}})


#Function will grade and store grade for each user of a question
#Author: Sam Palutro
def gradeQuestion(q_id, answer):
    answer = answer.lower()
    q_query = {"q_id": q_id}
    for i in answDB.find(q_query):
        if(i["answer"] == answer): #CORRECT ANSWER
            gradeDB.insert_one({"user": i["a_user"], "q_id": q_id, "answ": i["answer"], "corr": answer, "grade": 1})
        else: #WRONG ANSWER
            gradeDB.insert_one({"user": i["a_user"], "q_id": q_id, "answ": i["answer"], "corr": answer, "grade": 0})


def generateVerificationLink():                                                                 #GENERATE 120 ENTROPY UNIQUE VERIFICATION TOKEN
    charaters = string.ascii_letters + string.digits
    verification_code = ''.join(secrets.choice(charaters) for _ in range(120))
    return verification_code


def inputVerificationInDatabase(username, email):
    unique_link = generateVerificationLink()                                                     #GENERATE THE UNIQUE VERIFICATION TOKEN
    authDB.update_one({"username": username}, {"$set": {"verificationToken": unique_link}})      #INPUTS THE UNIQUE VERIFICATION TOKEN IN DATABASE FOR THE SPECIFIC USERNAME
    authDB.update_one({"username": username}, {"$set": {"verified": False}})                     #FIELD TO DISPLAY IF USER IS VERIFIED
    authDB.update_one({"username": username}, {"$set": {"email": email}})
    return unique_link


def emailVerificationLink(username, email):                                                           #SEND THE VERIFICATION EMAIL
    unique_token = inputVerificationInDatabase(username, email)
    email = Message(
        subject="Verify Your Email",
        recipients=[email],
        html="Verify your email for cse312.duckdns.org by visiting this link: https://cse312.duckdns.org:8080/verification/" + unique_token,
        sender="312endingfromtheback@gmail.com"
    )
    return email

def checkEmail(username, email):
    if username != "":
        userDoc = authDB.find_one({"username": username})
        if userDoc == None: #Not verified email
            return False
        elif userDoc != None: #Email is verified
            if userDoc["verified"] == False:
                return False
            elif userDoc["verified"] == True:
                safe_email = HTMLescaper(userDoc["email"])
                return safe_email
    elif username == "":
        userDoc = authDB.find_one({"email": email})
        if userDoc == None:
            return True
        if userDoc != None:
            return False

