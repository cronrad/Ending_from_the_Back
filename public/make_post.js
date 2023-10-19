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

function postHTML(postJSON) {
    const username = postJSON.username;
    const title = postJSON["title"];
    const description = postJSON["description"];
    let postHTML = "";
    postHTML += "<span><b>" + username + "</b>: - "+ title + "<br><br>" + description + "<br><br><br><br></span>";
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
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const postJSON = {"title": title, "description": description};
    request.open("POST", "/new_post");
    request.send(JSON.stringify(postJSON));
    postTitleBox.focus();
}

function updatePost() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearPost();
            const posts = JSON.parse(this.response);
            for (const post of posts) {
                addPosts(post);
            }
        }
    }
    request.open("GET", "/posts");
    request.send();
}

function newPost() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendPost();
        }
    });

    document.getElementById("paragraph").innerHTML += "<br/><h1><center><b>Make your new Post here!!!</b></center></h1>";
    document.getElementById("post-title-box").focus();

    updatePost();
    setInterval(updatePost, 1000);
}