import secrets
import bcrypt
from pymongo import MongoClient

#mongoClient = MongoClient("localhost") #For testing only
mongoClient = MongoClient("mongo")

db = mongoClient["cse312_project"]
authDB = db["auth"]
postDB = db["post"]

#HTML escaper function #TODO: Perent encoding?
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
    safe_username = HTMLescaper(username) #TODO: Check when to call HTML escape
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