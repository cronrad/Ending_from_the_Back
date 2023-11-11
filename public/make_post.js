const ws = true;
let socket = null;
let postList = [];

function initWS() {
    // Establish a WebSocket connection with the server
    socket = io.connect('ws://' + window.location.host, { transports: ["websocket"] });

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

    socket.on('repeat', () => {
        alert("You cannot submit an answer more than once or you are trying to answer your own question")
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
    timer_element.innerHTML = remaining_time
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
    let timer_html = "<p>Time Remaining: </p>"
    let timer_content_html = "<p id='" + question_timer + "'></p>"
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
    console.log(postHTML(postJSON));
    let regex = /id='question(\d+)box'/;
    let match = html.match(regex);
    console.log("match")
    console.log(match)
    postList.push(match[1]);
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
            file: fileData
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
        let jsonObj = {"title": title, "description": description, "answer": answer, "file": "null"};
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
            for (const post of posts) {
                addPosts(post);
                document.getElementById('timer').innerHTML = "";
                socket.emit('timer');
            }
            
        }
    }
    request2.open("GET", "/posts");
    request2.send();
}

function newPost() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendPost();
        }
    });
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
    updatePost();

    if (ws) {
        initWS();
    }
    else{ //This code shouldn't run part 3 and onwards
        setInterval(updatePost, 1000);
    }
}

