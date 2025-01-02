import asyncio
import websockets
import json

# Przechowywanie listy aktywnych użytkowników i wiadomości
rooms = {}

async def join_room(websocket, path):
    """
    Obsługuje dołączanie użytkowników do pokoju i wiadomości.
    """
    try:
        async for message in websocket:
            data = json.loads(message)

            if data['action'] == 'join_room':
                game_id = data['game_id']
                username = data['username']

                # Dodaj użytkownika do pokoju
                if game_id not in rooms:
                    rooms[game_id] = []
                rooms[game_id].append(websocket)

                # Powiadom wszystkich w pokoju
                for client in rooms[game_id]:
                    if client != websocket:
                        await client.send(json.dumps({
                            "action": "user_joined",
                            "message": f"{username} dołączył do pokoju!",
                            "username": username
                        }))

            elif data['action'] == 'send_message':
                game_id = data['game_id']
                username = data['username']
                message = data['message']

                # Wyślij wiadomość do wszystkich w pokoju
                for client in rooms[game_id]:
                    await client.send(json.dumps({
                        "action": "receive_message",
                        "username": username,
                        "message": message
                    }))

            elif data['action'] == 'make_move':
                game_id = data['game_id']
                row, col, player = data['row'], data['col'], data['player']

                # Prześlij ruch do wszystkich w pokoju
                for client in rooms[game_id]:
                    await client.send(json.dumps({
                        "action": "move_made",
                        "row": row,
                        "col": col,
                        "player": player
                    }))

    except websockets.exceptions.ConnectionClosedOK:
        # Usuń użytkownika, jeśli zamknął połączenie
        for game_id, clients in rooms.items():
            if websocket in clients:
                clients.remove(websocket)
                break

async def main():
    """
    Uruchamia serwer WebSocket na porcie 6789.
    """
    async with websockets.serve(join_room, "localhost", 6789):
        print("WebSocket serwer działa na ws://localhost:6789")
        await asyncio.Future()  # Trwa nieskończenie długo

if __name__ == "__main__":
    asyncio.run(main())
