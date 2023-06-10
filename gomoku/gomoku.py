from flask import Flask, request, jsonify, abort, redirect, url_for
import secrets

# Flask tutorial: https://auth0.com/blog/developing-restful-apis-with-python-and-flask/
app = Flask(__name__)

# User {username: string, token: string}
users = {} # Dict: username -> User
tokens = {} # Dict: token -> User
# Game {id: string, player1: string, player2: string, next: string, winner: string, board: string[][]}
games = {} # Dict: game id -> Game

gameId = 0

def getGameId():
    global gameId
    gameId += 1
    return str(gameId)

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
    game = {"id": getGameId(), "player1": user["username"], "player2": player2, "next": "X", "winner": "", "board": createBoard()}
    games[game["id"]] = game
    return jsonify({"gameId": game["id"], "games": games})

@app.route("/games")
def getGames():
    auth()
    return jsonify({"games": games})

def checkWin(board, row, col, rowOffset, colOffset):
    sum = 1
    piece = board[row][col]
    for i in range(1, 5):
        if 0 < (row + rowOffset * i) < 18 and 0 < (col + colOffset * i) < 18 and board[row + rowOffset * i][col + colOffset * i] == piece:
            sum += 1
        else:
            break
    for i in range(1, 5):
        if 0 < (row - rowOffset * i) < 18 and 0 < (col - colOffset * i) < 18 and board[row - rowOffset * i][col - colOffset * i] == piece:
            sum += 1
        else:
            break
    return sum >= 5

def makeMove(username, game, piece, row, col):
    if 0 > col > 18 or 0 > row > 18:
        return error("Wceluj w planszę")
    board = game["board"]
    if board[row][col] != "":
        return error("Tu już ktoś był")
    if game["next"] != piece:
        return error("Nie serwujemy poza kolejką")
    board[row][col] = piece
    game["next"] = "X" if piece == "O" else "O"
    if checkWin(board, row, col, 1, 0) or checkWin(board, row, col, 0, 1) or checkWin(board, row, col, 1, 1) or checkWin(board, row, col, -1, 1):
        game["winner"] = username
    return jsonify(game)

@app.route("/move", methods=["POST"])
def move():
    user = auth()
    if "id" not in request.form:
        return error("Ta gra nie istnieje")
    if "col" not in request.form or "row" not in request.form:
        return error("Wybierz pole")
    gameId = request.form["id"]
    row = int(request.form["row"])
    col = int(request.form["col"])
    if gameId not in games:
        return error("Ta gra nie istnieje")
    game = games[gameId]
    if game["winner"] != "":
        return error("Ta gra jest już skończona")
    if user["username"] == game["player1"]:
        return makeMove(user["username"], game, "X", row, col)
    if user["username"] == game["player2"]:
        return makeMove(user["username"], game, "O", row, col)
    return error("Ale pan tu nie grał")
    

def testData():
    testUsers = [{"username": "tata", "token": "1111"},
        {"username": "mama", "token": "2222"},
        {"username": "Pawełek", "token": "3333"}]
    for user in testUsers:
        users[user["username"]] = user
        tokens[user["token"]] = user
    testGames = [{"id": "1000", "player1": "tata", "player2": "Pawłek", "next": "X", "winner": "", "board": createBoard()}]
    testGames[0]["board"][3][7]="X"
    testGames[0]["board"][4][6]="O"
    for game in testGames:
        games[game["id"]] = game

testData()
