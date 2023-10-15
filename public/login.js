function login(){
    let username = document.getElementById("reg-form-username");
    let password = document.getElementById("reg-form-pass");
    let auth_JSON = {"username": username, "password": password};
    request.open("POST", "/login");
    request.send(JSON.stringify(auth_JSON));
}

function register(){
    let username = document.getElementById("login-form-username");
    let password = document.getElementById("login-form-pass");
    let auth_JSON = {"username": username, "password": password};
    request.open("POST", "/register");
    request.send(JSON.stringify(auth_JSON));
}