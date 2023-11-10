const ws = true;
let socket = null;

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

    //Template for receiving websocket data from client
    /*
    socket.on('answering', (ws_message) => {
        let message = JSON.parse(ws_message);
    });
     */
}


function logOut() {
    let username = ""
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

    var data = {"id": id, "username" : username}

    request.open('POST', '/like_post');
    request.send(JSON.stringify(data));
    updatePost();
}

function postHTML(postJSON) {
    console.log("parsing received message")
    console.log(postJSON)
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    let question_id = "question" + postJSON["postID"];
    let image_name = postJSON["file_name"]
    let question_button = question_id + "button"
    let question_box = question_id + "box"

    console.log(username)
    console.log(title)
    console.log(description)
    console.log(image_name)

    let html_string = ""
    let beginning_html = "<div id=" + question_id + ">"
    let username_html = "<span><b>Username: </b>" + username + "<br>" ;
    let title_html = "<b>Title: </b>" + title + "<br><br>";
    html_string += beginning_html + username_html + title_html
    if (image_name !== undefined && image_name !== null) {
        let image_string = "<img src='public/image/" + image_name + "'><br>"
        html_string += image_string
    }
    let description_html = "<b>Description: </b>" + description + "<br>";
    let submit_box_html = "<input id='" + question_box + "' type='text'>"
    let submit_html = "<button id='" + question_button + "' onclick='submitAnswer(this.id)'>Submit Answer</button>"
    let ending_html = "</span></div><br><br>"
    html_string += description_html + submit_box_html + submit_html + ending_html;
    return html_string

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
        console.log("no file upload detected")
        const title = postTitleBox.value;
        const description = postDescriptionBox.value;
        const answer = postAnswerBox.value;
        let jsonObj = {"title": title, "description": description, "answer": answer, "file": "null"};
        socket.emit('message', JSON.stringify(jsonObj))
        postTitleBox.value = "";
        postDescriptionBox.value = "";
        postAnswerBox.value = "";
        document.getElementById("form-file").value = null;
    }
}

//Called when a user wants to submit their answer
function submitAnswer(id){
    let text_box_id = id.slice(0, -6)
    text_box_id = text_box_id + "box"
    let text_box_content = document.getElementById(text_box_id)
    let jsonObj = {"answerID": id.slice(0, -6), "answerContent": text_box_content}
    socket.emit('answering', JSON.stringify(jsonObj))
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

    let username = ""
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            username = JSON.parse(this.response);
            if (username === false) {
                username = "Guest"
            }
            document.getElementById("user").innerHTML += username
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

