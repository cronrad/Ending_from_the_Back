from flask import *
from utils.database import *
import json
import bson.json_util as json_util

app = Flask(__name__, static_folder='public')

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
            #Find the next ID available
            cur = postDB.find()
            id = 0
            for i in cur:
                if(i["id"] >= id):
                    id = i["id"] + 1
            postDB.insert_one({"id": id, "title": title, "description": description, "username": username, "likes": []})
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
        post["_id"] = json_util.dumps(post["_id"])
        post_list.append(post)
    response = app.response_class(
        response=str(json.dumps(post_list)),
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
            username = body.get("username")

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
        response=username,
        status=200,
        mimetype='text/plain'
    )
    return response
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080, debug=True)