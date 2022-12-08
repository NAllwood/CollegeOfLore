let form = document.querySelector('form');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    let address = "http://localhost:8080"

    let user_name = document.getElementById("uname").value
    let password = document.getElementById("password").value

    if (e.submitter.id == "sign_in_button") {
        address = new URL("login", address)
    }
    if (e.submitter.id == "register_button") {
        address = new URL("register", address)
    }

    post(address, { "user_name": user_name, "password": password })
});

function post(url, payload) {
    console.log("posting")
    console.log(payload)
    console.log("to", url)
    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(response => console.log(JSON.stringify(response)))
}