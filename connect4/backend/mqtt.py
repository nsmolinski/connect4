import paho.mqtt.client as mqtt
import json

# Konfiguracja MQTT
broker = "localhost"  # Adres lokalnego brokera MQTT
port = 1883           # Port brokera MQTT
topic = "connect4/game"  # Główny temat gry

# Przechowywanie gier (może być używane do synchronizacji z backendem)
games = {}

# Callback po połączeniu z brokerem
def on_connect(client, userdata, flags, rc):
    print(f"Połączono z MQTT Brokerem o kodzie: {rc}")
    client.subscribe(f"{topic}/#")  # Subskrybuj wszystkie ruchy dla gier

# Callback po odebraniu wiadomości
def on_message(client, userdata, msg):
    print(f"Odebrano wiadomość z tematu {msg.topic}")
    try:
        message = json.loads(msg.payload.decode())
        if "move" in message:
            handle_move(message)
    except Exception as e:
        print(f"Błąd przetwarzania wiadomości: {e}")

# Obsługa ruchu
def handle_move(message):
    game_id = message["game_id"]
    move = message["move"]
    row, col, player = move["row"], move["col"], move["player"]

    if game_id not in games:
        games[game_id] = {"board": [[None for _ in range(7)] for _ in range(6)]}
    
    # Aktualizacja planszy
    games[game_id]["board"][row][col] = player
    print(f"Aktualizacja gry {game_id}: Ruch gracza {player} ({row}, {col})")

# Publikowanie ruchu gracza
def publish_move(client, game_id, row, col, player):
    message = {
        "game_id": game_id,
        "move": {
            "row": row,
            "col": col,
            "player": player
        }
    }
    client.publish(f"{topic}/{game_id}/move", json.dumps(message))
    print(f"Opublikowano ruch: Gra {game_id}, Gracz {player}, Pole ({row}, {col})")

# Tworzenie klienta MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Połącz z brokerem
client.connect(broker, port, 60)
client.loop_start()

# Główna pętla (jeśli potrzebne)
try:
    print("MQTT client działa... Naciśnij Ctrl+C, aby zakończyć.")
    while True:
        pass  # Program działa w pętli nieskończonej
except KeyboardInterrupt:
    print("Zamykanie klienta MQTT...")
    client.loop_stop()
    client.disconnect()
