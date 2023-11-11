from flask import *
from utils.database import *
import json
import bson.json_util as json_util
from flask_socketio import SocketIO, emit
from base64 import b64decode
import os
from datetime import datetime
import time

app = Flask(__name__, static_folder='public')
socketio = SocketIO(app, transports='websocket', async_mode='threading')
authenticated_connections = {}
guest_connections = {}
resetTimers() #Sets all question timers to 0 so no frozen timers

@app.after_request
def addHeader(response): #Applies no sniff header
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

#Base URL request
#Check if user is logged in, if true redirect to app, else send login page
@app.route('/')
def root():
    existingCookie = request.cookies.get('auth_token')
    if existingCookie:
        token, username = authenticate(None, None, existingCookie, False)
        if token != False: #User is logged in, send app html
            return render_template('app.html')
        else: #Not logged in or expired cookie, send login page
            return render_template('login.html')
    else: #Not logged in, send login page
        return render_template('login.html')



@app.route('/app')
def guestView():
    return render_template('app.html')

#For registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get("username_reg")
    password = request.form.get("password_reg")
    result = registerDB(username, password)
    if result == False:
        response = app.response_class(
            response="Username is taken, try a different username",
            status=200,
            mimetype='text/plain'
        )
        return response
    elif result == True:
        response = app.response_class(
            response="Registration successful",
            status=200,
            mimetype='text/plain'
        )
        return response

#If you're looking to check if a user is authenticated, check authenticate() in utils/database.py
#This is for processing the login from the login.html page only
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username_login")
    password = request.form.get("password_login")
    token, username = authenticate(username, password, None, True)
    if token == False:
        response = app.response_class(
            response = "Incorrect username or password",
            status = 200,
            mimetype = 'text/plain'
        )
        return response
    elif token != False: #Set cookie
        response = app.response_class(
            response = "Login Successful! Welcome " + username,
            status = 200,
            mimetype='text/plain'
        )
        response.set_cookie("auth_token", token, max_age=3600, httponly=True)
        return response

@app.route('/new_post', methods=['POST'])
def new_post():
    body = json.loads(request.get_data())

    username = request.form.get("username_login")
    password = request.form.get("password_login")
    token, username = authenticate(username, password, None, True)

    #Checks for authentication
    if request.cookies.get("auth_token") == None:
        response = app.response_class(
            response = "Access Denied, Login to make a post",
            status = 403,
            mimetype = 'text/plain'
        )
        return response
    else: 
        #Checks if the auth token matches
        auth_token = request.cookies.get("auth_token")
        token_check, username = authenticate("", "", auth_token, False)
        if username == False and token_check == False:
            response = app.response_class(
                response = "Access Denied, Login to make a post",
                status = 403,
                mimetype = 'text/plain'
                )
            return response
        else:
            #Adds the post to database
            title = HTMLescaper(body.get("title"))
            description = HTMLescaper(body.get("description"))
            answer = HTMLescaper(body.get("answer"))
            #Find the next ID available
            cur = postDB.find()
            id = 0
            for i in cur:
                if(i["id"] >= id):
                    id = i["id"] + 1
            postDB.insert_one({"id": id, "title": title, "description": description, "username": username, "answer": answer, "likes": []})
            response = app.response_class(
                response="Post submitted",
                status=200,
                mimetype='text/plain'
            )
            return response #The http response shouldn't change the page but you can still see this response in the network tab

@app.route('/posts', methods=['GET'])
def posts():
    #This keeps track of all the posts and updates
    post_list = []
    for post in postDB.find({}):
        if "postIDCounter" in post: #ignores post id counter in db
            continue
        else:
            post_list.append(post)
    response = app.response_class(
        response=str(json_util.dumps(post_list)),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/logout', methods=['POST'])
def logout():
    #This logs user out incase they want to logout or switch to a different account
    auth_token = request.cookies.get("auth_token")
    token_check, username = authenticate("", "", auth_token, False)
    authDB.update_one({},{"$unset": {"authToken": ""}})
    response = app.response_class(
        response=username,
        status=200,
        mimetype='text/plain'
    )
    response.set_cookie("auth_token", "", max_age=3600, httponly=True)
    return response #The http response shouldn't change the page but you can still see this response in the network tab
@app.route('/like_post', methods=['POST'])
def like_post():
    body = json.loads(request.get_data())
    #Checks for authentication
    if request.cookies.get("auth_token") == None:
        response = app.response_class(
            response = "Access Denied, Login to make a post",
            status = 403,
            mimetype = 'text/plain'
        )
        return response
    else:
        #Checks if the auth token matches
        auth_token = request.cookies.get("auth_token")
        token_check, username = authenticate("", "", auth_token, False)
        if username == False and token_check == False:
            response = app.response_class(
                response = "Access Denied, Login to make a post",
                status = 403,
                mimetype = 'text/plain'
                )
            return response
        else:
            #Adds like to the post in database
            id = body.get("id")
            token_check, username = authenticate("", "", auth_token, False)

            cur = postDB.find_one({"id": id})
            if username not in cur["likes"]:
                cur["likes"].append(username)
                myquery = {"id": id}
                newvalues = {"$set": {"likes": cur["likes"]}}
                postDB.update_one(myquery, newvalues)
                cur["likes"].append(username)
            else:
                cur["likes"].remove(username)
                myquery = {"id": id}
                newvalues = {"$set": {"likes": cur["likes"]}}
                postDB.update_one(myquery, newvalues)
                cur["likes"].append(username)

            response = app.response_class(
                response="Post submitted",
                status=200,
                mimetype='text/plain'
            )

            return response

            # return response #The http response shouldn't change the page but you can still see this response in the network tab

@app.route('/username', methods=['GET'])
def username():
    #This sends the username from backend to frontend for displaying once user is logged in
    auth_token = request.cookies.get("auth_token")
    token_check, username = authenticate("", "", auth_token, False)
    response = app.response_class(
        response=str(json.dumps(username)),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/grades')
def grades():
    # check if user is logged in
    # send them to page filled with user data for gradess
    return render_template("grades.html")


#This is where the http request for a 101 switching protocol occurs
#We authenticate the user here and tie their websocket connection session to their username here
@socketio.on('connect')
def initialConnection():
    auth_token = request.cookies.get("auth_token")
    token, username = authenticate("", "", auth_token, False)
    if guest_connections.get("counter") == None:
        guest_connections["counter"] = 0
    if username != False: #Authenticated user
        authenticated_connections[username] = request.sid
    elif username == False: #Unauthenticated user, will only be able to view
        guest_key = "Guest" + str(guest_connections["counter"])
        guest_connections["counter"] += 1
        guest_connections[guest_key] = request.sid
    postDB.update_many({},{'$set': {'answerIDS': []}},upsert=False)
    postDB.update_many({},{'$set': {'answerCon': []}},upsert=False)

#This is when the the websocket connection disconnects
#We remove them from either of our own maintained dictionary of connections
@socketio.on('disconnect')
def handleDisconnection():
    for i in authenticated_connections:
        if authenticated_connections[i] == request.sid:
            del authenticated_connections[i]
    for i in guest_connections:
        if guest_connections[i] == request.sid:
            del guest_connections[i]

#This is the endpoint for when a post is made
#To send a message to ALL websocket connections, do emit('event flag',*message data stuff here*,broadcast=True)
@socketio.on('message')
def handleWebsocket(data):
    #Find the username of the current connection
    username = None
    for i in authenticated_connections:
        if authenticated_connections[i] == request.sid:
            username = i
    if username == None: #Don't allow post
        emit('unauthenticated', room=request.sid)
    else: #Assume user
        #Load the data
        data = json.loads(data)
        if data["file"] != "null":  # File upload along with the text
            #Save the file
            file_name = saveFile(username, data) #this saves the file and returns a file name to be used to request on client side
            #Store the text data in db and get response object
            response = handlePost(username, data["title"], data["description"], data["answer"], file_name)
            response["file_name"] = file_name
            response_json = json.dumps(response)
            emit('message',response_json, broadcast=True)
            #Handle the time
            seconds = getTimeRemaining(response["postID"])
            remaining = seconds
            while remaining >= 0:
                if remaining <= 0:
                    jsonObj = {"timer_id": ("question" + str(response["postID"]) + "time"), "remaining": remaining}
                    emit('timer', json.dumps(jsonObj), broadcast=True)
                    break
                time.sleep(1)
                remaining -= 1
                # Update db and emit
                updateTimeRemaining(response["postID"], remaining)
                jsonObj = {"timer_id": ("question" + str(response["postID"]) + "timer"), "remaining": remaining}
                emit('timer', json.dumps(jsonObj), broadcast=True)
            # Call grade function
        elif data.get("file") == "null":  # No image upload with the text
            #Store the text data in db and get response object
            response = handlePost(username, data["title"], data["description"], data["answer"], None)
            response_json = json.dumps(response)
            emit('message', response_json, broadcast=True)
            seconds = getTimeRemaining(response["postID"])
            remaining = seconds
            while remaining >= 0:
                if remaining <= 0:
                    jsonObj = {"timer_id": ("question" + str(response["postID"]) + "time"), "remaining": remaining}
                    emit('timer', json.dumps(jsonObj), broadcast=True)
                    break
                time.sleep(1)
                remaining -= 1
                # Update db and emit
                updateTimeRemaining(response["postID"], remaining)
                jsonObj = {"timer_id": ("question" + str(response["postID"]) + "time"), "remaining": remaining}
                emit('timer', json.dumps(jsonObj), broadcast=True)
            #Call grade function

#Endpoint for when a user answers a question
#To be clear:
@socketio.on('answering')
def answeringWebsocket(data):
    username = None
    for i in authenticated_connections:
        if authenticated_connections[i] == request.sid:
            username = i
    if username == None: #Don't allow post
        emit('unauthenticated', room=request.sid) #room=request.sid to specify only this connection
    else: #Run actual code for objective 2 below here
        data = json.loads(data)
        result = enteringAnswers(username, data["answerID"], str(data["answerContent"]).lower())     #Enters the answer in the database
        if result == None: #User is trying to submit answer for a question that doesn't exist
            emit('nonexist', room=request.sid)
        elif result == "1": #User is trying to answer their own question
            emit('own', room=request.sid)
        elif result == "2": #User is trying to submit after time limit
            emit('limit', room=request.sid)
        elif result == "3": #User is trying to submit more than once
            emit('repeat', room=request.sid)


#Called when the page is loaded by timers for questions are already going down
@socketio.on('timer_history')
def sendingTime(data):
    data = json.loads(data)
    id = int(data["id"])
    seconds = getTimeRemaining(id)
    remaining = seconds
    while remaining >= 0:
        if remaining <= 0:
            jsonObj = {"timer_id": ("question" + str(id) + "time"), "remaining": remaining}
            emit('timer', json.dumps(jsonObj), room=request.sid)
            break
        time.sleep(1)
        remaining = getTimeRemaining(id)
        # Update db and emit
        jsonObj = {"timer_id": ("question" + str(id) + "time"), "remaining": remaining}
        emit('timer', json.dumps(jsonObj), room=request.sid)


if __name__ == '__main__':
   socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)