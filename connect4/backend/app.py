from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
import random
import string
import paho.mqtt.client as mqtt
import json

app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Przechowywanie danych o grach
games = {}
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "connect4/game/#"

# Callback po połączeniu z brokerem
def on_connect(client, userdata, flags, rc):
    print("Połączono z brokerem MQTT z kodem:", rc)
    client.subscribe(MQTT_TOPIC)

# Callback po odebraniu wiadomości MQTT
def on_message(client, userdata, msg):
    print(f"Odebrano wiadomość z tematu {msg.topic}: {msg.payload.decode()}")
    data = json.loads(msg.payload.decode())
    socketio.emit('mqtt_message', data, room=data['game_id'])

# Inicjalizacja klienta MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

def generate_game_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_id>')
def game(game_id):
    if game_id in games:
        return render_template('game.html', game_id=game_id)
    return "Game not found", 404

@app.route('/api/game', methods=['POST'])
def create_game():
    game_id = generate_game_id()
    games[game_id] = {"players": [], "board": [[None for _ in range(7)] for _ in range(6)], "current_turn": None}
    return jsonify({"game_id": game_id}), 201

@app.route('/api/join/<game_id>', methods=['POST'])
def join_game(game_id):
    if game_id in games:
        if len(games[game_id]["players"]) < 2:
            games[game_id]["players"].append(request.remote_addr)
            return jsonify({"status": "joined", "game_id": game_id}), 200
        return jsonify({"error": "Game full"}), 403
    return jsonify({"error": "Game not found"}), 404

@app.route('/api/check_winner', methods=['POST'])
def check_winner():
    data = request.json
    board = data['board']
    player = data['player']

    def check_line(r, c, dr, dc):
        count = 0
        for _ in range(4):
            if 0 <= r < 6 and 0 <= c < 7 and board[r][c] == player:
                count += 1
                if count == 4:
                    return True
            else:
                break
            r += dr
            c += dc
        return False

    for r in range(6):
        for c in range(7):
            if board[r][c] == player:
                if (
                    check_line(r, c, 0, 1) or
                    check_line(r, c, 1, 0) or
                    check_line(r, c, 1, 1) or
                    check_line(r, c, 1, -1)
                ):
                    return jsonify({"winner": player}), 200

    return jsonify({"winner": None}), 200

@socketio.on('join_room')
def handle_join(data):
    game_id = data['game_id']
    username = data['username']

    if game_id not in games:
        games[game_id] = {"players": [], "board": [[None for _ in range(7)] for _ in range(6)], "current_turn": None}

    if len(games[game_id]["players"]) < 2 and username not in games[game_id]["players"]:
        games[game_id]["players"].append(username)
        join_room(game_id)
        emit('user_joined', {"message": f"{username} dołączył do pokoju!"}, room=game_id)

    if len(games[game_id]["players"]) == 2:
        games[game_id]["current_turn"] = games[game_id]["players"][0]
        emit('game_start', {"message": "Gra się rozpoczęła!", "current_player": games[game_id]["current_turn"]}, room=game_id)

@socketio.on('make_move')
def handle_move(data):
    game_id = data['game_id']
    row = data['row']
    col = data['col']
    player = data['player']

    if games[game_id]["current_turn"] != player:
        emit('invalid_move', {"message": "Nie Twoja tura!"}, room=request.sid)
        return

    games[game_id]["board"][row][col] = player
    emit('move_made', data, room=game_id)

    response = check_winner_internal(games[game_id]["board"], player)
    if response:
        emit('game_over', {"winner": player}, room=game_id)
        return

    players = games[game_id]["players"]
    next_player = players[1] if games[game_id]["current_turn"] == players[0] else players[0]
    games[game_id]["current_turn"] = next_player
    emit('player_turn', {"current_player": next_player}, room=game_id)
@socketio.on('game_over')
def handle_game_over(data):
    """Obsługuje koniec gry."""
    winner = data['winner']
    game_id = data['game_id']
    emit('game_over', {"winner": winner}, room=game_id)

def check_winner_internal(board, player):
    def check_line(r, c, dr, dc):
        count = 0
        for _ in range(4):
            if 0 <= r < 6 and 0 <= c < 7 and board[r][c] == player:
                count += 1
                if count == 4:
                    return True
            else:
                break
            r += dr
            c += dc
        return False

    for r in range(6):
        for c in range(7):
            if board[r][c] == player:
                if (
                    check_line(r, c, 0, 1) or
                    check_line(r, c, 1, 0) or
                    check_line(r, c, 1, 1) or
                    check_line(r, c, 1, -1)
                ):
                    return True
    return False

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, log_output=True)
