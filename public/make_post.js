const ws = true;
let socket = null;
let postList = [];

function initWS() {
    // Establish a WebSocket connection with the server
    socket = io.connect('wss://' + window.location.host, { transports: ["websocket"] });

    // Called whenever data is received from the server over the WebSocket connection
    socket.on('message', (ws_message) => {
        let message = JSON.parse(ws_message);
        addPosts(message);
    });

    socket.on('unauthenticated', () => {
        alert("You are unauthenticated, you cannot post or answer questions")
    });

    socket.on('nonexist', () => {
        alert("You are trying to submit an answer to a question that doesn't exist")
    });

    socket.on('own', () => {
        alert("You cannot answer your own question")
    });

    socket.on('repeat', () => {
        alert("You cannot submit an answer more than once")
    });

    socket.on('limit', () => {
        alert("The time limit has been reached, you can longer answer this question")
    });

    socket.on('timer', (ws_message) => {
        updateTimer(JSON.parse(ws_message));
    });

    /*
    socket.on('timer', (tim) => {                                                             //Time listner to constantly refresh time and once time is 0 automatically submits         //the answers
        if(tim.time == 0){                                                                    //TODO: THIS SOCKET LISTENER IS WHAT WE HAVE TO FIX TO GET RID OF DUPLICATE DATA
            document.getElementById("timer").innerHTML = "Time left to answer the question: 0";
            for(const x of postList){
                socket.emit("answering", JSON.stringify({"answerID": x, "answerContent": document.getElementById("question"+x+"box").value}));     //This sends some duplicate data 
            }                                                                                                                                      //that I will handle on server side
            postList = []// ^ Above is supposed to use submitAnswer(id) but I am not sure how to get "id"
        }
        else{
            document.getElementById("timer").innerHTML = "Time left to answer the question: "+tim.time;        //This displays time left for questions to be answered in
        }

    });
     */
     
    //This will respond with the time
    socket.on('answering', (ws_message) => {
        let message = JSON.parse(ws_message);
    });
}
function updateTimer(data) {
    let elementID = data["timer_id"]
    let remaining_time = data["remaining"]
    let timer_element = document.getElementById(elementID)
    if (remaining_time === 0){
        remaining_time = "Time Limit Reached"
    }
    if (timer_element == null){
    }
    else{
        timer_element.innerHTML = remaining_time
    }

}

function logOut() {
    let username = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            username = this.response;
        }
    }
    request.open("POST", "/logout");
    request.send(JSON.stringify(username));
}

function likePost(username, id) {
    var request = new XMLHttpRequest();

    request.onreadystatechange = function() {
        if (request.readyState == 4) {
            if (request.status == 200) {
                console.log('POST request successful');
            } else {
                console.error('POST request failed');
            }
        }
    };

    var data = {"id": id, "username" : username};

    request.open('POST', '/like_post');
    request.send(JSON.stringify(data));
    updatePost();
}

function postHTML(postJSON) {
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    let question_id = "question" + postJSON["postID"];
    let image_name = postJSON["file_name"];
    let question_button = question_id + "button";
    let question_box = question_id + "box";
    let question_timer = question_id + "time";

    let html_string = "";
    let beginning_html = "<div id=" + question_id + ">";
    let username_html = "<span><b>Username: </b>" + username + "<br>" ;
    let title_html = "<b>Title: </b>" + title + "<br><br>";
    html_string += beginning_html + username_html + title_html;
    if (image_name !== undefined && image_name !== null) {
        let image_string = "<img src='public/image/" + image_name + "'><br>";
        html_string += image_string;
    }
    let description_html = "<b>Description: </b>" + description + "<br>";
    let timer_html = "<b>Time Remaining: </b>"
    let timer_content_html = "<b id='" + question_timer + "'></b><br>"
    let submit_box_html = "<input id='" + question_box + "' type='text'>";
    let submit_html = "<button id='" + question_button + "' onclick='submitAnswer(this.id)'>Submit Answer</button><br>";
    let ending_html = "</span></div><br><br>";
    html_string += description_html + timer_html + timer_content_html + submit_box_html + submit_html + ending_html;
    return html_string;

    /*
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    // const likes = postJSON["likes"].size();
    const likes = postJSON["likes"].length;
    const liked = postJSON["likes"].includes(username);
    const id = postJSON["id"];

    var like_OR_dislike = ""
    if(liked){
        like_OR_dislike = "Dislike";
    }else{
        like_OR_dislike = "Like";
    }


    let postHTML = "";
    // postHTML += "<span><b>" + username + "</b>: - "+ title + "<br><br>" + description + "<br><br><br> likes: " + likes + "<br><button id=\"post-button\" value=\"" + like_OR_dislike + "\"onclick=\"likePost()\">Like <3</button><br><br><hr></span>";
    postHTML += "<span><b>" + username + "</b>: - " + title + "<br><br>" + description + "<br><br><br> likes: " + likes + "<br><button id=\"post-button\" value=\"" + like_OR_dislike + "\" onclick=\"likePost('" + username + "', " + id + ")\">Like <3</button><br><br><hr></span>";
    // postHTML += "<span><b>" + username + "</b>: - "+ title + "<br><br>" + description + "<br><br><br>" + likes + "<br><button id=\"post-button\" value=\"" + like_OR_dislike + "\"onclick=\"likePost(" + username + ", " + id + ")\">Like<br></button></span>";
    return postHTML;
     */
}

function clearPost() {
    const posts = document.getElementById("posts");
    posts.innerHTML = "";
}

function addPosts(postJSON) {
    const posts = document.getElementById("posts");
    posts.innerHTML += postHTML(postJSON);
    let html = postHTML(postJSON)
    /*
    console.log(postHTML(postJSON));
    let regex = /id='question(\d+)box'/;
    let match = html.match(regex);
    console.log("match")
    console.log(match)
    postList.push(match[1]);
    */
}

//This should be the only function modified to support websockets over ajax
function sendPost() {
    const postTitleBox = document.getElementById("post-title-box");
    const postDescriptionBox = document.getElementById("post-description-box");
    const postAnswerBox = document.getElementById("post-answer-key-box");
    let fileInput = document.getElementById("form-file");
    let file = fileInput.files[0];

    if (file !== undefined){
        let reader = new FileReader();
        reader.onload = function () {
            const arrayBuffer = reader.result;  // The ArrayBuffer
            const uint8Array = new Uint8Array(arrayBuffer);
            const fileData = {
                name: file.name,
                content: Array.from(uint8Array)  // Convert to a plain JavaScript array
            };
        const title = postTitleBox.value;
        const description = postDescriptionBox.value;
        const answer = postAnswerBox.value;
        const jsonObj = {
            title: title,
            description: description,
            answer: answer,
            file_name: fileData
        };

        postTitleBox.value = "";
        postDescriptionBox.value = "";
        postAnswerBox.value = "";

        socket.emit('message', JSON.stringify(jsonObj));

        };
        reader.readAsArrayBuffer(file);
        document.getElementById("form-file").value = null;
    }
    else{
        const title = postTitleBox.value;
        const description = postDescriptionBox.value;
        const answer = postAnswerBox.value;
        let jsonObj = {"title": title, "description": description, "answer": answer, "file_name": "null"};
        socket.emit('message', JSON.stringify(jsonObj));
        postTitleBox.value = "";
        postDescriptionBox.value = "";
        postAnswerBox.value = "";
        document.getElementById("form-file").value = null;
    }
}

//Called when a user wants to submit their answer
function submitAnswer(id){
    let text_box_id = id.slice(0, -6);
    text_box_id = text_box_id + "box";
    let text_box_content = document.getElementById(text_box_id).value;
    let jsonObj = {"answerID": id.slice(8, -6), "answerContent": text_box_content};
    socket.emit('answering', JSON.stringify(jsonObj));
}

//With websockets, this is only called on page load to load existing question posts
function updatePost() {

    let request2 = new XMLHttpRequest();
    request2.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearPost();
            const posts = JSON.parse(this.response);
            let postIDs = []
            for (const post of posts) {
                addPosts(post);
                postIDs.push(post["postID"])
            }
            for (const i of postIDs){
                let jsonObj = {"id": i}
                socket.emit("timer_history", JSON.stringify(jsonObj))
            }
        }
    }
    request2.open("GET", "/posts");
    request2.send();
}

function newPost() {
    document.getElementById("paragraph").innerHTML += "<br/><h1><center><b>CSE312 Quiz App</b></center></h1>";
    document.getElementById("post-title-box").focus();

    let username = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            username = JSON.parse(this.response);
            if (username === false) {
                username = "Guest";
            }
            document.getElementById("user").innerHTML += username;
        }
    }
    request.open("GET", "/username");
    request.send();

    initWS();
    updatePost();
    /*
    else{ //This code shouldn't run part 3 and onwards
        setInterval(updatePost, 1000);
    }
     */
}

// Retrieves username for grades page
function getUsername(){
    let username = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            username = JSON.parse(this.response);
            if (username === false) {
                username = "Guest";
            }
            document.getElementById("user").innerHTML += "<center>" + username + "<center>";
        }
    }
    request.open("GET", "/username");
    request.send();
}

// For grading page

function addGradedPosts(postJSON) {
    const posts = document.getElementById("answered-questions");
    posts.innerHTML += gradedPostHTML(postJSON);
    let html = gradedPostHTML(postJSON)
}

function gradedPostHTML(postJSON) {
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    const expectedAnswer = postJSON.answer;
    const userAnswers = postJSON.user_answers;
    const grade = postJSON.grade; 
    const real_username = postJSON.real_username;

    let question_id = "question" + postJSON["postID"];
    let image_name = postJSON["file_name"];

    let html_string = "";
    let beginning_html = "<div id=" + question_id + ">";
    let username_html = "<span><b>Username: </b>" + username + "<br>";
    let title_html = "<b>Title: </b>" + title + "<br><br>";
    html_string += beginning_html + username_html + title_html;

    if (image_name !== undefined && image_name !== null) {
        let image_string = "<img src='public/image/" + image_name + "'><br>";
        html_string += image_string;
    }

    let description_html = "<b>Description: </b>" + description + "<br>";
    let expectedAnswer_html = "<b>Expected Answer: </b></b><span style='color: blue;'>" + expectedAnswer + "</span><br>";
    let userAnswer_html = "<b>Your Answer: </b><span style='color: blue;'>"+userAnswers[real_username]+"</span></b><br>";
    // if (userAnswers && userAnswers[username]) {
    //     userAnswer_html += userAnswers[username] + "<br>";
    // } else {
    //     userAnswer_html += "No answer recorded<br>";
    // }

    let grade_html = "<b>Your Grade: </b>";
    if (grade === "Correct") {
        grade_html += "<span style='color: green;'>" + grade + "</span><br>";
    } else {
        grade_html += "<span style='color: red;'>" + grade + "</span><br>";
    }

    let ending_html = "</span></div><br><br><hr>";
    html_string += description_html + expectedAnswer_html + userAnswer_html + grade_html + ending_html;
    
    return html_string;
}


function updateGradedPost() {
    let request3 = new XMLHttpRequest();
    request3.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearGradedPost();
            const posts = JSON.parse(this.response);
            for (const post of posts) {
                addGradedPosts(post);
            }
        }
    }
    request3.open("GET", "/grading");
    request3.send();
}

function clearGradedPost() {
    const posts = document.getElementById("answered-questions");
    posts.innerHTML = "";

}

// For question gradebook

function addQuestionGradebook(postJSON) {
    const posts = document.getElementById("question-gradebook");
    posts.innerHTML += questionGradebookPostHTML(postJSON);
    let html = questionGradebookPostHTML(postJSON)
}

function questionGradebookPostHTML(postJSON) {
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    const grades = postJSON.question_grades;
    const expectedAnswer = postJSON.answer;  // Assuming the answer is stored in the "answer" property
    const userAnswers = postJSON.user_answers;  // Assuming user answers are stored in the "user_answers" property

    let question_id = "question" + postJSON["postID"];
    let image_name = postJSON["file_name"];

    let html_string = "";
    let beginning_html = "<div id=" + question_id + ">";
    let username_html = "<span><b>Username: </b>" + username + "<br>";
    let title_html = "<b>Title: </b>" + title + "<br><br>";
    html_string += beginning_html + username_html + title_html;

    if (image_name !== undefined && image_name !== null) {
        let image_string = "<img src='public/image/" + image_name + "'><br>";
        html_string += image_string;
    }

    let description_html = "<b>Description: </b>" + description + "<br>";
    html_string += description_html;

    // Display expected answer in blue
    html_string += "<b>Expected Answer: </b><span style='color: blue;'>" + expectedAnswer + "</span><br>";

    // Check if there are no answers
    if (!grades || Object.keys(grades).length === 0) {
        // Display "No Answers :(" in rainbow colors
        html_string += "<b>User's Answers and Grades: </b><span style='color: red;'>No Answers :(</span><br>";
    } else {
        // Iterate over the grades dictionary
        html_string += "<b>User Answers and Grades:</b><br>";
        for (const user in grades) {
            if (grades.hasOwnProperty(user)) {
                let grade_html = "&emsp;<b>" + user + ":</b><br>";

                // Display user's answer in blue
                if (userAnswers && userAnswers[user]) {
                    grade_html += "&emsp;&emsp;User's Answer: <span style='color: blue;'>" + userAnswers[user] + "</span><br>";
                } else {
                    grade_html += "&emsp;&emsp;User's Answer: <span style='color: blue;'>Not provided</span><br>";
                }

                // Check if the grade is "Correct" or "Incorrect"
                grade_html += "&emsp;&emsp;Grade: ";
                if (grades[user] === "Correct") {
                    grade_html += "<span style='color: green;'>" + grades[user] + "</span><br>";
                } else {
                    grade_html += "<span style='color: red;'>" + grades[user] + "</span><br>";
                }

                html_string += grade_html;
            }
        }
    }

    let ending_html = "</span></div><br><br><hr>";
    html_string += ending_html;

    return html_string;
}


function updateQuestionGradebook() {
    let request3 = new XMLHttpRequest();
    request3.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearQuestionGradebook();
            const posts = JSON.parse(this.response);
            for (const post of posts) {
                addQuestionGradebook(post);
            }
        }
    }
    request3.open("GET", "/question_gradebook");
    request3.send();
}

function clearQuestionGradebook() {
    const posts = document.getElementById("question-gradebook");
    posts.innerHTML = "";
}
