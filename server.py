from flask import *
from utils.database import *
import json

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
    body = request.get_json()
    #Checks for authentication
    if body.get("auth_token") == None:
        response = app.response_class(
            response = "Access Denied, Login to make a post",
            status = 403,
            mimetype = 'text/plain'
        )
        return response
    else:
        #Adds the post to database
        title = body.get("title")
        description = body.get("description")
        content = body.get("content")
        postDB.insert_one({"title": title, "description": description, "content": content})
        return response                #Frontend should ignore the response

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8080, debug=True)