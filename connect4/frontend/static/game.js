let currentPlayer = null; // Aktualny gracz, który wykonuje ruch
let username = null; // Nazwa gracza zalogowanego w przeglądarce

const params = new URLSearchParams(window.location.search);
const gameId = params.get('game_id');
const socket = io('http://127.0.0.1:5000');

const boardState = Array.from({ length: 6 }, () => Array(7).fill(null)); // Plansza gry 6x7

// Pobranie ID gry
document.getElementById('game-id').textContent = `Kod pokoju: ${gameId}`;

// Pobranie nazwy użytkownika
username = prompt('Podaj swoją nazwę użytkownika:');
socket.emit('join_room', { game_id: gameId, username });

// Obsługa czatu
socket.on('user_joined', (data) => {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.textContent = data.message;
    chatMessages.appendChild(messageElement);
});

socket.on('game_start', (data) => {
    alert(data.message); // Wyświetlenie informacji o rozpoczęciu gry
    currentPlayer = data.current_player;
    updateCurrentPlayerDisplay();
});

socket.on('player_turn', (data) => {
    currentPlayer = data.current_player;
    updateCurrentPlayerDisplay();
});

socket.on('game_over', (data) => {
    alert(`Gracz ${data.winner} wygrał!`);
    setTimeout(() => {
        window.location.href = '/'; // Przenosi na stronę główną po 3 sekundach
    }, 3000);
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
socket.on('move_made', (data) => {
    const { row, col, player } = data;
    updateBoard(row, col, player);
});

// Publikowanie ruchu do backendu
function publishMove(col) {
    if (currentPlayer !== username) {
        alert('To nie jest Twoja tura!');
        return;
    }

    // Znalezienie najniższego wolnego wiersza w wybranej kolumnie
    let row = -1;
    for (let r = 5; r >= 0; r--) {
        if (boardState[r][col] === null) {
            row = r;
            break;
        }
    }

    if (row === -1) {
        alert('Ta kolumna jest już pełna!');
        return;
    }

    const moveMessage = {
        game_id: gameId,
        row,
        col,
        player: username
    };

    socket.emit('make_move', moveMessage);
}

function updateCurrentPlayerDisplay() {
    const currentPlayerElement = document.getElementById('current-player');
    currentPlayerElement.textContent = `Ruch gracza: ${currentPlayer}`;
}

// Generowanie planszy gry (7x6)
function generateBoard() {
    const board = document.getElementById('board');
    for (let row = 0; row < 6; row++) {
        for (let col = 0; col < 7; col++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.row = row;
            cell.dataset.col = col;
            board.appendChild(cell);
        }
    }

    // Obsługa kliknięcia na kolumnę
    board.addEventListener('click', (e) => {
        const col = e.target.dataset.col;
        if (col !== undefined) {
            publishMove(parseInt(col));
        }
    });
}

// Aktualizacja planszy
function updateBoard(row, col, player) {
    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (cell) {
        cell.classList.add(player === username ? 'player1' : 'player2');
        boardState[row][col] = player;

        // Sprawdź zwycięzcę
        fetch('http://127.0.0.1:5000/api/check_winner', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: boardState, player })
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.winner) {
                socket.emit('game_over', { winner: data.winner, game_id: gameId });
            }
        });
    }
}

// Ustaw gracza początkowego
document.addEventListener('DOMContentLoaded', generateBoard);
