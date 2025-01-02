const params = new URLSearchParams(window.location.search);
const gameId = params.get('game_id');
const socket = io('http://127.0.0.1:5000');

// Pobranie ID gry
document.getElementById('game-id').textContent = `Kod pokoju: ${gameId}`;

// Dołączanie do pokoju
const username = prompt('Podaj swoją nazwę użytkownika:');
socket.emit('join_room', { game_id: gameId, username });

// Obsługa czatu
socket.on('user_joined', (data) => {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.textContent = data.message;
    chatMessages.appendChild(messageElement);
});

document.getElementById('send-message').addEventListener('click', () => {
    const message = document.getElementById('chat-input').value.trim();
    if (!message) return;

    socket.emit('send_message', { game_id: gameId, username, message });
    document.getElementById('chat-input').value = '';
});

socket.on('receive_message', (data) => {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
    chatMessages.appendChild(messageElement);
});

// Obsługa ruchów w grze
document.querySelectorAll('.cell').forEach((cell) => {
    cell.addEventListener('click', () => {
        const row = cell.dataset.row;
        const col = cell.dataset.col;

        socket.emit('make_move', { game_id: gameId, row, col, player: username });
    });
});

socket.on('move_made', (data) => {
    const cell = document.querySelector(`[data-row="${data.row}"][data-col="${data.col}"]`);
    cell.classList.add(data.player === username ? 'player1' : 'player2');
});
