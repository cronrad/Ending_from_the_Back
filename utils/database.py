import secrets
import bcrypt
import os
from pymongo import MongoClient

mongoClient = MongoClient("localhost") #For testing only
#mongoClient = MongoClient("mongo")

db = mongoClient["cse312_project"]
authDB = db["auth"]
postDB = db["post"]
fileDB = db["file"]

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
    postDB.insert_one({"postID": postID["postIDCounter"], "username": username, "title": title, "description": description, "answer": answer, "file": file_name})
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
    file_dict = data["file"]
    # Get the actual data of the file
    file_content = bytearray(file_dict["content"])
    # Get the new file name
    file_name = setFileID(username, file_dict["name"])
    filePath = os.path.join('public/image/', file_name)
    with open(filePath, 'wb') as file:
        file.write(file_content)
    return file_name


#TODO: Function will enter the data we received into database
def enteringAnswers(username, answerID, answerContent):
    print(username)
    print(answerContent)
    print(answerID)