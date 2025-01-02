import paho.mqtt.client as mqtt
from app import update_board  # Import funkcji do aktualizacji planszy

broker = 'localhost'  # Adres lokalnego brokera HiveMQ
port = 1883  # Domyślny port MQTT
topic = "connect4/game/update"

# Inicjalizacja klienta MQTT (API v2)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Funkcja wywoływana po połączeniu z brokerem (uwzględnia 5 argumentów)
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Połączono z lokalnym brokerem HiveMQ")
        client.subscribe(topic)
    else:
        print(f"Nie udało się połączyć, kod błędu: {rc}")

# Funkcja wywoływana po otrzymaniu wiadomości
def on_message(client, userdata, msg):
    data = msg.payload.decode()
    try:
        game_id, move = data.split(',')
        move = eval(move)  # Konwertowanie ruchu do słownika
        print(f"Otrzymano wiadomość: {data}")
        update_board(game_id, move)
    except Exception as e:
        print(f"Błąd podczas przetwarzania wiadomości: {e}")

# Przypisanie funkcji callback
client.on_connect = on_connect
client.on_message = on_message

# Połączenie z brokerem HiveMQ
client.connect(broker, port, 60)

# Nasłuchiwanie w trybie ciągłym
client.loop_forever()

print("MQTT Client nasłuchuje...")
