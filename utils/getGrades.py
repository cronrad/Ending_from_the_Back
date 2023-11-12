import json
import bson.json_util as json_util
from utils.database import *

def calculateGrade(username, post):
    userAnswer = post["user_answers"].get(username)
    # if userAnswer != None:
    if str(post["answer"]).lower() == str(userAnswer).lower():
        return "Correct"
    else:
        return "Incorrect"
    

def user_grades(request, app):
    post_list = []
    auth_token = request.cookies.get("auth_token")
    token_check, username = authenticate("", "", auth_token, False)

    for post in postDB.find():
        if "postIDCounter" in post: #ignores post id counter in db
            continue
        elif username in post["user_answers"]:
            grade = calculateGrade(username, post)
            post["grade"] = grade
            post["real_username"] = username
            post_list.append(post)
    response = app.response_class(
        response=str(json_util.dumps(post_list)),
        status=200,
        mimetype='application/json'
    )
    return response

def question_grades(request, app):
    post_list = []
    auth_token = request.cookies.get("auth_token")
    token_check, username = authenticate("", "", auth_token, False)
    if token_check == False:
        response = app.response_class(
            response="Access Denied, login to view gradebook",
            status=403,
            mimetype='text/plain'
        )
        return response
    elif token_check != False:
        for post in postDB.find():
            if "postIDCounter" in post:  # ignores post id counter in db
                continue
            elif username in post["username"]:
                grade_dict = {}  # Use a dictionary to store grades for each user
                for user_answer in post["user_answers"]:
                    grade = calculateGrade(user_answer, post)
                    grade_dict[user_answer] = grade

                post["question_grades"] = grade_dict
                post_list.append(post)

        response = app.response_class(
            response=str(json_util.dumps(post_list)),
            status=200,
            mimetype='application/json'
        )
    return response
            