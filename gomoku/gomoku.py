from flask import Flask, request, jsonify, abort, redirect, url_for
import secrets

# Flask tutorial: https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
app = Flask(__name__)

# User {username: string, token: string}
users = {} # Dict: username -> User
tokens = {} # Dict: token -> User

def testData():
    testUsers = [{"username": "tata", "token": "1111"},
        {"username": "mama", "token": "2222"},
        {"username": "Pawełek", "token": "3333"}]
    for user in testUsers:
        users[user["username"]] = user
        tokens[user["token"]] = user

def error(msg):
    return jsonify({"error": msg})

@app.route("/")
def main():
    return redirect(url_for("static", filename="login.html"))

@app.route("/login", methods=["POST"])
def login():
    if "username" not in request.form:
        return error("Nie podano loginu")
    username = request.form["username"]
    if username in users:
        return error("Taki login jest już używany")
    token = secrets.token_urlsafe()
    user = {"username": username, "token": token}
    users[username] = user
    tokens[token] = user
    return jsonify(user)

@app.route("/users")
def getUsers():
    token = request.args["token"]
    if token not in tokens:
        return error("Zaloguj się")
    username = tokens[token]["username"]
    others = [u["username"] for u in users.values() if u["token"] != token]
    return jsonify({"you": username, "users": others})

testData()
