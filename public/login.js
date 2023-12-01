function guestView() {
    window.location.href = "/app";
}

function registerAccount(){
    let username = document.getElementById("reg-form-username").value;
    let password = document.getElementById("reg-form-pass").value;
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let response_data = JSON.parse(request.responseText);
            alert(response_data.message)
        }
    }
    let user_data = {"username": username, "password": password}
    request.open("POST", "/register");
    request.send(JSON.stringify(user_data));
}

function loginAccount(){
    let username = document.getElementById("login-form-username").value;
    let password = document.getElementById("login-form-pass").value;
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            let response_data = JSON.parse(request.responseText);
            if (response_data.status == "0"){
                alert(response_data.message)
            }
            else if (response_data.status == "1"){
                alert(response_data.message)
                window.location.href = "/app";
            }
        }
    }
    let user_data = {"username": username, "password": password}
    request.open("POST", "/login");
    request.send(JSON.stringify(user_data));
}