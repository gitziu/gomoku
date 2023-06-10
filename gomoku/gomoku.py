from flask import Flask, request, jsonify, abort, redirect, url_for
import secrets

app = Flask(__name__)

users = {}
tokens = {}

@app.route("/")
def main():
    return redirect(url_for("static", filename="login.html"))

@app.route("/login", methods=["POST"])
def login():
    if "username" not in request.form:
        abort(401)
    username = request.form["username"]
    if username in users:
        return jsonify({"error": "Taki login jest już używany"})
    token = secrets.token_urlsafe()
    user = {"username": username, "token": token}
    users[username] = user
    tokens[token] = user
    return jsonify(user)

