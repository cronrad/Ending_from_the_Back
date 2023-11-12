import json
import bson.json_util as json_util
from utils.database import *

def calculateGrade(username, post):
    userAnswer = post["user_answers"].get(username)
    # if userAnswer != None:
    if post["answer"] == userAnswer:
        return "Correct"
    else:
        return "Incorrect"


            