from flask import Flask, request, jsonify, abort, redirect, url_for
import secrets

# Flask tutorial: https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
app = Flask(__name__)

# User {username: string, token: string}
users = {} # Dict: username -> User
tokens = {} # Dict: token -> User
# Game {id: string, player1: string, player2: string, winner: string, board: string[][]}
games = {} # Dict: game id -> Game

gameId = 0

def getGameId():
    global gameId
    gameId += 1
    return gameId

def createBoard():
    return [[""] * 19 for _ in range(19)]

def error(msg):
    return jsonify({"error": msg})

def auth():
    token = request.args["token"]
    if token not in tokens:
        abort(401)
    return tokens[token]

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
    user = auth()
    others = [u["username"] for u in users.values() if u != user]
    return jsonify({"you": user["username"], "users": others})

@app.route("/games", methods=["POST"])
def startGame():
    user = auth()
    if "username" not in request.form:
        return error("Nie wiesz z kim grać?")
    player2 = request.form["username"]
    if player2 not in users:
        return error("Nie ma takiego gracza")
    game = {"id": getGameId(), "player1": user["username"], "player2": player2, "winner": "", "board": createBoard()}
    games[game["id"]] = game
    return jsonify({"gameId": game["id"], "games": games})

@app.route("/games")
def getGames():
    auth()
    return jsonify({"games": games})



def testData():
    testUsers = [{"username": "tata", "token": "1111"},
        {"username": "mama", "token": "2222"},
        {"username": "Pawełek", "token": "3333"}]
    for user in testUsers:
        users[user["username"]] = user
        tokens[user["token"]] = user
    testGames = [{"id": 1, "player1": "tata", "player2": "Pawłek", "winner": "", "board": createBoard()}]
    for game in testGames:
        games[game["id"]] = game

testData()
