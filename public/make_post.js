function postHTML(postJSON) {
    const username = postJSON.username;
    const title = postJSON.title;
    const description = postJSON.description;
    const content = postJSON.content;
    const postId = postJSON.id;
    postHTML += "<span id='post_" + postId + "'><b>" + username + "</b>: " + title + " - "+ description + "<br><br>" + content + "</span>";
    return postHTML;
}

function clearPost() {
    const postTitle = document.getElementById("title");
    const postDescription = document.getElementById("description");
    const postContent = document.getElementById("content");
    postTitle.innerHTML = "";
    postDescription.innerHTML = "";
    postContent.innerHTML = "";
}

function addPosts(postJSON) {
    const posts = document.getElementById("posts");
    posts.innerHTML += postHTML(postJSON);
    posts.scrollIntoView(false);
    posts.scrollTop = posts.scrollHeight - posts.clientHeight;
}

function sendPost() {
    const postTitleBox = document.getElementById("post-title-box");
    const postDescriptionBox = document.getElementById("post-description-box");
    const postContentBox = document.getElementById("post-content-box");
    const title = postTitleBox.value;
    const description = postDescriptionBox.value;
    const content = postContentBox.value;
    postTitleBox.value = "";
    postDescriptionBox.value = "";
    postContentBox.value = "";
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    const postJSON = {"title": title, "description": description, "content": content};
    request.open("POST", "/new_post");
    request.send(JSON.stringify(messageJSON));
    chatTextBox.focus();
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

    document.getElementById("paragraph").innerHTML += "<br/><h1><center><b>Make your new Post here!!!</b></center>/h1>";
    document.getElementById("post-title-box").focus();

    updatePost();
    setInterval(updatePost, 1000);
}