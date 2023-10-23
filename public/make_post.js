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
}

function clearPost() {
    const posts = document.getElementById("posts");
    posts.innerHTML = "";
}

function addPosts(postJSON) {
    const posts = document.getElementById("posts");
    posts.innerHTML += postHTML(postJSON);

}

function sendPost() {
    const postTitleBox = document.getElementById("post-title-box");
    const postDescriptionBox = document.getElementById("post-description-box");
    const title = postTitleBox.value;
    const description = postDescriptionBox.value;
    postTitleBox.value = "";
    postDescriptionBox.value = "";
    const likes = 0
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const postJSON = {"title": title, "description": description, "likes": likes};
    request.open("POST", "/new_post");
    request.send(JSON.stringify(postJSON));
    postTitleBox.focus();
}

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
    document.getElementById("paragraph").innerHTML += "<br/><h1><center><b>Make your new Post here!!!</b></center></h1>";
    document.getElementById("post-title-box").focus();

    let username = ""
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            username = JSON.parse(this.response);
            document.getElementById("user").innerHTML += username
        }
    }
    request.open("GET", "/username");
    request.send();

    updatePost();
    setInterval(updatePost, 1000);

}