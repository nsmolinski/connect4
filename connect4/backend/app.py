from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
import random
import string

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
# Przechowywanie danych o grach
games = {}

def generate_game_id():
    """Generuje unikalny identyfikator gry."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    """Strona główna."""
    return render_template('index.html')

@app.route('/game/<game_id>')
def game(game_id):
    """Strona gry."""
    if game_id in games:
        return render_template('game.html', game_id=game_id)
    return "Game not found", 404

@app.route('/api/game', methods=['POST'])
def create_game():
    """Tworzy nową grę."""
    game_id = generate_game_id()
    games[game_id] = {"players": []}
    return jsonify({"game_id": game_id}), 201

@app.route('/api/join/<game_id>', methods=['POST'])
def join_game(game_id):
    """Dołącza użytkownika do istniejącej gry."""
    if game_id in games:
        if len(games[game_id]["players"]) < 2:
            games[game_id]["players"].append(request.remote_addr)
            return jsonify({"status": "joined", "game_id": game_id}), 200
        return jsonify({"error": "Game full"}), 403
    return jsonify({"error": "Game not found"}), 404

@socketio.on('join_room')
def handle_join(data):
    """Obsługuje dołączanie użytkownika do pokoju."""
    game_id = data["game_id"]
    username = data["username"]

    if game_id in games:
        join_room(game_id)
        emit('user_joined', {"message": f"{username} dołączył do pokoju!"}, room=game_id)

@socketio.on('send_message')
def handle_message(data):
    """Obsługuje wysyłanie wiadomości."""
    game_id = data["game_id"]
    username = data["username"]
    message = data["message"]

    emit('receive_message', {"username": username, "message": message}, room=game_id)

@socketio.on('make_move')
def handle_move(data):
    """Obsługuje ruch w grze."""
    game_id = data["game_id"]
    row, col, player = data["row"], data["col"], data["player"]

    # Logika gry (tutaj można dodać aktualizację planszy)
    emit('move_made', {"row": row, "col": col, "player": player}, room=game_id)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
